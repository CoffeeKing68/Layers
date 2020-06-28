from wand.color import Color
from wand.image import Image

from layers.base_layers import ShapeLayer

from layers.attribute import StringAttribute as SA
from layers.attribute import NumericAttribute as NA
from layers.attribute import AddAttribute as AA
from layers.attribute import MultiplyAttribute as MulA
from layers.attribute import DivideAttribute as DivA

class ColorLayer(ShapeLayer):
    """A ShapeLayer that has 1 solid color."""
    def render(self, fresh=False):
        if fresh and self.pre_render is not None:
            return self.pre_render
        elif self.content is not None:
            if not isinstance(self.content, Color):
                self.content = Color(self.content)
            img = Image(width=int(self["width"]), height=int(self["height"]), background=self.content)
            return img
        else:
            raise NotReadyToRenderError("Content is needed to render ColorLayer.")

class ColorBackgroundLayer(ColorLayer):
    def __init__(self, name, *args, **kwargs):
        kwargs["left"] = NA(0)
        kwargs["width"] = SA("parent.width")
        kwargs["top"] = NA(0)
        kwargs["height"] = SA("parent.height")
        if "order" not in kwargs:
            kwargs["order"] = -99
        super().__init__(name, **kwargs)

class GradientLayer(ShapeLayer):
    def __init__(self, name, start, end, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        if not isinstance(start, Color):
            start = Color(start)
        if not isinstance(end, Color):
            end = Color(end)
        self.start = start
        self.end = end
        self.content = "Temporary fix"

    def render(self, fresh=False):
        if fresh or self.pre_render is None: # if fresh is false and there is a pre_render
            img = Image(width=int(self["width"]), height=int(self["height"]),
                pseudo=f"gradient:{self.start.string}-{self.end.string}")
            self.pre_render = img
        return self.pre_render
