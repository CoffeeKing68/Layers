from layers.bounds import Bounds
from layers.exceptions import NotEvaluatedError, InsufficientBoundsError
from layers.attribute import Attribute
from layers.attribute import StringAttribute as SA
from layers.attribute import NumericAttribute as NA
from layers.attribute import AddAttribute as AA

class Dimension():
    def __init__(self, name, pct, mapping, amount, layer, bounds=None, **kwargs):
        self.amount = amount
        self.pct = pct # YP/XP
        self.name = name
        self.mapping = mapping # {top: start, right: end, height: full}
        self.layer = layer
        self.attributes = self.validate_attributes(kwargs)
        self.bounds = bounds # None if bounds is not present

    @property
    def is_evaluated(self):
        """Will check it's attributes if they are all evaluated."""
        return all(attr.is_evaluated for attr in self.attributes.values())

    def map_bound(self, descriptor):
        """Maps dimension specific bound descriptors to standard Bounds
        conventions. eg. left/top -> start, XP40/YP40 -> P40."""
        # if descriptor in self.mapping.values():
        #     return descriptor
        if descriptor in self.mapping: # if is left, top, height
            return self.mapping[descriptor]
        elif descriptor[:2].upper() == self.pct.upper(): # is pct
            # change . to _ for bounds method
            parsed_pct = str(Bounds.parse_pct(descriptor[1:])).replace(".", "_")
            return f"P{parsed_pct}"

    def validate_attributes(self, kwargs):
        """Validates attribute keys to make sure they are valid and that the
        correct amount have been passed in."""
        attributes = {}
        for key, argument in kwargs.items():
            mapped_key = self.map_bound(key)
            # is valid bound descriptor and arg is Attribute
            if mapped_key is not None and isinstance(argument, Attribute):
                argument.dimension = self
                attributes[key] = argument

        if len(attributes) > self.amount:
            raise ValueError("You passed in too many attributes")
        elif len(attributes) < self.amount:
            raise ValueError("You passed in too few attributes")
        else:
            return attributes

    def attributes_to_bounds(self):
        """If all attributes are evaluated, will return a dict with Standard
        Bound names and the attributes evaluated_value."""
        for attribute in self.attributes.values():
            attribute.evaluate()
        if all(a.is_evaluated for a in self.attributes.values()): # all attributes evaled?
            bounds = {}
            for descriptor, attribute in self.attributes.items():
                bounds[self.map_bound(descriptor)] = attribute.evaluated_value
            return bounds
        else:
            raise NotEvaluatedError(f"Layer {self.layer.name}'s attributes can't be evaluated right now")

    def update_bounds(self, **kwargs):
        if not self.is_bounded:
            if self.amount == 1: # is a point layer
                full = next(key for key, value in self.mapping.items() if value == 'full')
                if self.layer.content is None:
                    self.attributes[full] = NA(0)
                else:
                    self.attributes[full] = NA(getattr(self.layer.render(), full))
            try:
                bounds = self.attributes_to_bounds()
                self.bounds = Bounds(**bounds, **kwargs)
                return self.bounds
            except NotEvaluatedError:
                pass
        else:
            return self.bounds

    # def update_bounds_if_neccessary(self, **kwargs):
    #     self.update_bounds(**kwargs)

    # def full_reset_bounds(self, **kwargs):
    #     for attr in self.attributes.values(): # unset attribute_ev
    #         attr.unset_evaluated_value()
    #     self.bounds = None
    #     self.update_bounds(**kwargs)

    @property
    def is_bounded(self):
        """Returns True if Dimension has a bounds object that is not None."""
        return self.bounds is not None

class XDimension(Dimension):
    mapping = {
        "left": "start",
        "xcenter": "center",
        "right": "end",
        "width": "full",
    }
    def __init__(self, amount, layer, bounds=None, **attributes):
        super().__init__("x", "XP", XDimension.mapping, amount, layer, bounds, **attributes)

class YDimension(Dimension):
    mapping = {
        "top": "start",
        "ycenter": "center",
        "bottom": "end",
        "height": "full",
    }
    def __init__(self, amount, layer, bounds=None, **attributes):
        super().__init__("y", "YP", YDimension.mapping, amount, layer, bounds, **attributes)

class PTLYDimension(YDimension):
    def __init__(self, amount, layer, bounds=None, **attributes):
        self.ptl_mapping = {
            "base": "base_temporary_value",
            "median": "median_temporary_value",
            "cap": "cap_height_temporary_value",
            "descender": "descender_temporary_value",
            "ascender": "ascender_temporary_value",
        }
        self.mapping = {**YDimension.mapping, **self.ptl_mapping}
        super(YDimension, self).__init__("y", "YP", self.mapping, amount, layer, bounds, **attributes)

    def update_bounds(self, **kwargs):
        """
        3. find idm bound
            -
                - get idm
                - set bottom
                - go super()
            - else
                - pass
        """
        # if self.layer.name == "name":
        #     print(self.attributes)
        try: # go super()
            super().update_bounds(**kwargs)
        except InsufficientBoundsError: # idm bound is set or real InsufficientBoundsError
            idm_attrs = {}
            for key, attr in self.attributes.items():
                if key in self.ptl_mapping:
                    idm_attrs[key] = attr
            if all(a.is_evaluated for a in idm_attrs.values()): # if evaled
                if self.layer.content is None:
                    for key, attribute in self.attributes.items():
                        if key in self.ptl_mapping:
                            # print(key, self.layer.name)
                            kwargs["end"] = attribute.evaluated_value
                else:
                    idm = self.layer.get_in_depth_font_metrics()
                    for key in self.attributes:
                        ev = self.attributes[key].evaluated_value
                        if key == "base":
                            kwargs["end"] = ev + idm["absolute_descender"]
                        elif key == "median":
                            kwargs["end"] = ev + idm["absolute_descender"] + idm["median"]
                        elif key == "cap":
                            kwargs["end"] = ev + idm["absolute_descender"] + idm["cap"]
                super().update_bounds(**kwargs)
            else:
                return None

        # if not self.is_bounded:
        #     if self.amount == 1: # is a point layer
        #         full = next(key for key, value in self.mapping.items() if value == 'full')
        #         if self.layer.content is None:
        #             self.attributes[full] = NA(0)
        #         else:
        #             self.attributes[full] = NA(getattr(self.layer.render(), full))
        #     try:
        #         bounds = self.attributes_to_bounds()
        #         self.bounds = Bounds(**bounds, **kwargs)
        #         return self.bounds
        #     except NotEvaluatedError:
        #         pass
        # else:
        #     return self.bounds

        # if self.layer.content is None:
        #     self.attributes["height"] = NA(0)
        # else:
        #     self.attributes["height"] = self.layer.render().height
        # print(self.attributes)

        # if self.layer.content is None:
        #     for key in list(self.attributes):
        #         if key in self.ptl_mapping:
        #             self.attributes[bottom] = self.attributes[key]
        # else:
        #     idm = self.layer.get_in_depth_font_metrics()
        #     for key in list(self.attributes):
        #         if key == "base":
        #             self.attributes["bottom"] = AA(self.attributes["base"], NA(idm["absolute_descender"]))
        #         elif key == "median":
        #             a = NA(idm["absolute_descender"] + idm["median"])
        #             self.attributes["bottom"] = AA(self.attributes["median"], a)
        #         elif key == "cap":
        #             a = NA(idm["absolute_descender"] + idm["cap"])
        #             self.attributes["bottom"] = AA(self.attributes["cap"], a)

