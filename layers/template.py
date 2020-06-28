from layers.base_layers import Layer, ShapeLayer

from wand.image import Image
from wand.color import Color
from pprint import pprint

class Template(ShapeLayer):
    """Layers that appear first in *layers arg are rendered first if order is
    not specified (order = 0 by default)."""
    def __init__(self, name, *layers, **kwargs):
        self.layers = []
        super().__init__(name, **kwargs)
        self.layers = layers

    @property
    def layers(self):
        return self._layers

    @layers.setter
    def layers(self, layers):
        for l in layers:
            l.parent = self
            l.template = self
        self._layers = layers

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        self._template = value
        for l in self.layers:
            l.template = value

    @property
    def are_layers_bounded(self):
        return all(l.is_bounded for l in self.layers)

    def update_bounds(self):
        tries = 0
        def update_dimensions(layer):
            should_reset = False
            for dim in layer.dimensions.values():
                bounded_before = dim.is_bounded
                # if not bounded_before:
                dim.update_bounds()
                if dim.is_bounded and not bounded_before:
                    should_reset = True
            return should_reset

        while tries < 3:
            tries += 1
            if update_dimensions(self):
                tries = 0
            for l in self.layers:
                if isinstance(l, Template):
                    l.update_bounds()
                else:
                    if update_dimensions(l):
                        tries = 0

    def unset_bounds_and_attributes(self):
        super().unset_bounds_and_attributes()
        for l in self.layers:
            l.unset_bounds_and_attributes()

    def unset_content_and_pre_render(self):
        super().unset_content_and_pre_render()
        for l in self.layers:
            l.unset_content_and_pre_render()

    def render(self, fresh=False):
        image = Image(width=int(self["width"]), height=int(self["height"]))
        for layer in sorted(self.layers, key=lambda l: l.order):
            if layer.content is not None or isinstance(layer, Template):
                img = layer.render(fresh)
                if img is not None:
                    image.composite(img, left=int(layer["left"]), top=int(layer["top"]))
        return image

    # def shadow(self, x, y, radius=2, sigma=4, fresh=False, color="Black"):
    #     # image = Image(width=int(self["width"]), height=int(self["height"]))
    #     # for layer in sorted(self.layers, key=lambda l: l.order):
    #     #     if layer.content is not None or isinstance(layer, Template):
    #     img = self.render()
    #     img = shadow(x, y, radius=radius, sigma=sigma, color=color)
    #     return img

    def render_boundary(self):
        image = Image(width=int(self["width"]), height=int(self["height"]),
            background=Color("Transparent"))
        for layer in sorted(self.layers, key=lambda l: l.order):
            img = layer.render_boundary()
            if img is not None:
                image.composite(img, left=int(layer["left"]), top=int(layer["top"]))
        return image

    def __str__(self):
        attributes = ", ".join([f"{key}={attribute.__short_str__()}" for key, attribute in self.attributes.items()])
        return f"Template({self.name}, {attributes})"

    def get_layer(self, key):
        if isinstance(key, Layer):
            key = key.name
        if isinstance(key, str):
            for layer in self.layers:
                if layer.name == key:
                    return layer
                elif isinstance(layer, Template):
                    l = layer.get_layer(key)
                    if l is not None:
                        return l
        else:
            raise ValueError("You can only pass in layer names or layers.")

