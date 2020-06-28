from abc import ABC, abstractmethod
from re import match
from functools import reduce
from layers.exceptions import NotBoundedError, NotReadyToEvaluateError, LayerDoesNotExistError
from pprint import pprint

class Attribute(ABC):
    negative_char = "-"
    absolute_char = "!" # #/^/*/&

    def __init__(self, attr, negative=False, absolute=False):
        if not self.isValid(attr):
            raise ValueError("Invalid attribute.")
        self.evaluated_value = None
        self.dimension = None
        while True:
            if attr[0] == Attribute.negative_char:
                attr = attr[1:]
                negative = True
            elif attr[0] == Attribute.absolute_char:
                attr = attr[1:]
                absolute = True
            else:
                break

        self.attr = attr
        self.negative = negative
        self.absolute = absolute

    @staticmethod
    @abstractmethod
    def isValid(attr):
        """
        Way to check if attr is a valid attribute
        :return: boolean
        """
        pass

    @abstractmethod
    def evaluate(self, template):
        pass

    @property
    def evaluated_value(self):
        return self.last_pass()

    @evaluated_value.setter
    def evaluated_value(self, value):
        self._evaluated_value = value

    def last_pass(self):
        ev = self._evaluated_value
        if ev is not None:
            try:
                ev = self.negate(ev)
                ev = self.absolutify(ev)
            except NotReadyToEvaluateError:
                return None
        return ev

    def negate(self, value):
        if self.negative:
            value = -value
        return value

    def absolutify(self, value):
        # print("bounds", self.dimension.layer.name)
        # if not self.absolute and self.dimension.layer.parent is not None: # is relative
        #     try:
        #         pd = self.dimension.layer.parent.dimensions[self.dimension.name]
        #         # print(pd.layer)
        #         value += pd.bounds["start"]
        #     except:
        #         raise NotReadyToEvaluate
        return value

    def unset_evaluated_value(self):
        self.evaluated_value = None

    @property
    def is_evaluated(self):
        return self.evaluated_value is not None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        try:
            evaluate = self.evaluated_value
        except:
            evaluate = "NULL"
        return f"{self.__class__.__name__}({'-' if self.negative else ''}{self.attr}, {evaluate})"

    def __short_str__(self):
        try:
            evaluate = self.evaluated_value
        except:
            evaluate = "NULL"
        return f"{self.__short_class_name__()}({'-' if self.negative else ''}{self.attr}, {evaluate})"

    @abstractmethod
    def __short_class_name__(self):
        pass

class FunctionAttribute(Attribute):
    def __init__(self, *attrs, negative=False, absolute=False):
        self.attrs = attrs
        self.dimension = None
        for attr in self.attrs:
            self.dimension = None
        self.negative = negative
        self.absolute = absolute
        self.evaluated_value = None

    def print_map(self):
        l = []
        for attr in self.attrs:
            attr.evaluate()
            if isinstance(attr, FunctionAttribute):
                l.append([attr, attr.print_map()])
            else:
                l.append(attr)
        return l

    @property
    def dimension(self):
        return self._dimension

    @dimension.setter
    def dimension(self, value):
        self._dimension = value
        for attr in self.attrs:
            attr.dimension = value

    @property
    def evaluated_value(self):
        return self.last_pass()

    @evaluated_value.setter
    def evaluated_value(self, value):
        self._evaluated_value = value

    def evaluate(self):
        self.evaluated_value = None
        for attr in self.attrs:
            attr.evaluate()

    def unset_evaluated_value(self):
        super().unset_evaluated_value()
        # self.evaluated_value = None
        for attr in self.attrs:
            attr.unset_evaluated_value()

    @property
    def is_evaluated(self):
        return all(attr.is_evaluated for attr in self.attrs)

    @staticmethod
    def isValid(attr):
        """
        :attr: Be a string and in <layer>.<attribute> format.
        """
        return isinstance(attr, Attribute)

    def __str__(self):
        try:
            evaluate = self.evaluated_value
        except:
            evaluate = "NULL"
        return f"{self.__class__.__name__}({'-' if self.negative else ''}..., {evaluate})"

    def __short_str__(self):
        try:
            evaluate = self.evaluated_value
        except:
            evaluate = "NULL"
        return f"{self.__short_class_name__()}({'-' if self.negative else ''}..., {evaluate})"

class AddAttribute(FunctionAttribute):
    def evaluate(self):
        """Weird behaviour here, with other FunctionAttributes setting ev should
        take place outside of try.except, but not AddAttribute.Pytest passes
        either way, so should write some more tests."""
        try:
            super().evaluate()
            self.evaluated_value = sum(attr.evaluated_value for attr in self.attrs)
            return self.last_pass()
        except:
            return None

    def __short_class_name__(self):
        return "AddAttr"

class MaxAttribute(FunctionAttribute):
    def evaluate(self):
        try:
            super().evaluate()
            self.evaluated_value = max(attr.evaluated_value for attr in self.attrs)
            return self.last_pass()
        except:
            return None

    def __short_class_name__(self):
        return "MaxAttr"

class MinAttribute(FunctionAttribute):
    def evaluate(self):
        try:
            super().evaluate()
            self.evaluated_value = min(attr.evaluated_value for attr in self.attrs)
            return self.last_pass()
        except:
            return None

    def __short_class_name__(self):
        return "MinAttr"

class DivideAttribute(FunctionAttribute):
    def evaluate(self):
        try:
            super().evaluate()
            if any(a.evaluated_value == 0 for a in self.attrs): # avoid div / 0
                self.evaluated_value = 0
            else:
                self.evaluated_value = reduce((lambda x, y: x / y),
                    [a.evaluated_value for a in self.attrs])
            return self.last_pass()
        except:
            return None

    def __short_class_name__(self):
        return "DivAttr"

class MultiplyAttribute(FunctionAttribute):
    def evaluate(self):
        try:
            super().evaluate()
            self.evaluated_value = reduce((lambda x, y: x * y),
                [a.evaluated_value for a in self.attrs])
            return self.last_pass()
        except:
            return None

    def __short_class_name__(self):
        return "MulAttr"

class StringAttribute(Attribute):
    """
    eg. <>.<left/xcenter/right/width/
    :accepted layers: layer.name, template, parent
    :accepted attributes:
        left, xcenter, right, width
        top, ycenter, bottom, height
        XP<pct>, YP<pct>
    """
    def evaluate(self):
        l, attr = self.attr.split(".")
        llayer = self.dimension.layer
        if self.evaluated_value is None and llayer.template is not None:
        # if True: # TODO this change may be very expensive
            if l == "parent" and llayer.parent is not None:
                layer = llayer.parent
                reference = SingleLayerReference(attr, layer)
            elif l == "template" and llayer.template is not None:
                layer = llayer.template
                reference = SingleLayerReference(attr, layer)
            elif l == "self":
                layer = self.dimension.layer
                reference = SingleLayerReference(attr, layer)
            elif l == "null":
                if attr == "height":
                    reference = NullHeightTemplateReference(*llayer.layers)
                elif attr == "width":
                    reference = NullWidthTemplateReference(*llayer.layers)
            else:
                template = llayer.template
                if llayer.template is None:
                    template = llayer
                layer = template.get_layer(l)
                reference = SingleLayerReference(attr, layer)
            try:
                self.evaluated_value = reference.evaluate()
                return self.evaluated_value
            except NotBoundedError: # Don't complain if not bounded
                # pass # complain if bad key (see Layer.__getitem__)
                if type(reference) == SingleLayerReference:
                    for dim in layer.dimensions.values():
                        for key, attribute in dim.attributes.items():
                            if key == attr and attribute.is_evaluated:
                                self.evaluated_value = attribute.evaluated_value
                                return self.evaluated_value
            except TypeError:
                raise LayerDoesNotExistError(f"{l} does not exist in template {template.name}")
        else:
            return self.evaluated_value

    @staticmethod
    def isValid(attr):
        """
        :attr: Be a string and in <layer>.<attribute> format.
        """
        try:
            layer, attribute = attr.split('.')
            return isinstance(attr, str) and match(r"\D+", layer) and match(r"\D+", attribute) and "." in attr
        except:
            return False

    def __short_class_name__(self):
        return "StrAttr"

class NumericAttribute(Attribute):
    def __init__(self, attr, *args, **kwargs):
        """
        :param attr: Can be int or str, might make it int only later?
        """
        if isinstance(attr, int): # pass in number
            if int(attr) < 0: # number is negative
                kwargs["negative"] = True
                attr = str(abs(attr))
            else:
                attr = str(attr)
        elif isinstance(attr, float):
            attr = str(attr)
        super().__init__(attr, *args, **kwargs)

    def evaluate(self):
        if self.evaluated_value is None:
        # if True: # TODO this change my be expensive
            self.evaluated_value = float(self.attr)
            return self.evaluated_value
        else:
            return self.evaluated_value

    def unset_evaluated_value(self):
        pass

    @staticmethod
    def isValid(attr):
        """
        :attr: Be numeric
        """
        try:
            val = float(attr)
            return True
        except ValueError:
            return False

    def __short_class_name__(self):
        return "NumAttr"

class LayerReference(ABC):
    def __init__(self, attribute, *layers):
        self.attribute = attribute
        self.layers = layers

    @abstractmethod
    def evaluate(self):
        pass

class SingleLayerReference(LayerReference):
    def __init__(self, attribute, layer):
        super().__init__(attribute, layer)

    def evaluate(self):
        return self.layers[0][self.attribute]

class NullHeightTemplateReference(LayerReference):
    def __init__(self, *layers):
        self.layers = layers

    def evaluate(self):
        # pprint([(l.name, l.y.bounds) for l in self.layers])
        min_top = min(l["top"] for l in self.layers)
        max_bottom = max(l["bottom"] for l in self.layers)
        return max_bottom - min_top

# class NullWidthTemplateReference(LayerReference):
#     def __init__(self, *layers):
#         self.layers = layers

#     def evaluate(self):
#         min_left = min(l["left"] for l in self.layers)
#         max_right = max(l["right"] for l in self.layers)
#         return max_right - min_left

