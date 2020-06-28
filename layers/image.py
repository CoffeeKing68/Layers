from wand.image import Image

from layers.base_layers import ShapeLayer, PointLayer

from layers.attribute import StringAttribute as SA
from layers.attribute import AddAttribute as AA
from layers.attribute import MultiplyAttribute as MulA
from layers.attribute import MaxAttribute as MaxA
from layers.attribute import MinAttribute as MinA
from layers.attribute import DivideAttribute as DivA

class ImageLayer(PointLayer):
    def render(self, fresh=False):
        if not fresh and self.pre_render is not None: # if fresh is false and there is a pre_render
            return self.pre_render
        if self.content is not None:
            img = Image(filename=self.content)
            self.pre_render = img
            return img
        else:
            raise NotReadyToRenderError(f"{self.name} is not ready to render right now.")

class ResizeImageLayer(ShapeLayer):
    """Image will be resized to the provided width and height."""
    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value
        # super(ShapeLayer, type(self)).content.fset(self, value)
        if value is None:
            self.initial_width = self.initial_height = 0
        else:
            with Image(filename=value) as img:
                self.initial_width, self.initial_height = img.size

    def render(self, fresh=False):
        if not fresh and self.pre_render is not None: # if fresh is false and there is a pre_render
            return self.pre_render
        if self.content is not None:
            img = Image(filename=self.content)
            img.resize(int(self["width"]), int(self["height"]))
            self.pre_render = img
            return img
        else:
            raise NotReadyToRenderError(f"{self.name} is not ready to render right now.")

    def __getitem__(self, key):
        if key == "initial_width":
            return self.initial_width
        elif key == "initial_height":
            return self.initial_height
        else:
            return super().__getitem__(key)

class FitImageLayer(ResizeImageLayer):
    """Sets width and height to fit in shape defined by width and height.
    The ratio of the image is respected."""
    def __init__(self, name, *args, width=None, height=None, **kwargs):
        initial_width = SA("self.initial_width")
        initial_height = SA("self.initial_height")
        ratio_attr = MinA(DivA(width, initial_width), DivA(height, initial_height))
        super().__init__(name, *args, width=MulA(initial_width, ratio_attr),
            height=MulA(initial_height, ratio_attr), **kwargs)

class FillImageLayer(ResizeImageLayer):
    """Sets width and height to fill shape defined by width and height.
    The ratio of the image is respected."""
    def __init__(self, name, *args, width=None, height=None, **kwargs):
        initial_width = SA("self.initial_width")
        initial_height = SA("self.initial_height")
        ratio_attr = MaxA(DivA(width, initial_width), DivA(height, initial_height))
        super().__init__(name, *args, width=MulA(initial_width, ratio_attr),
            height=MulA(initial_height, ratio_attr), **kwargs)


