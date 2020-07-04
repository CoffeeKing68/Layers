from layers.base_layers import Layer, ShapeLayer

from wand.image import Image
from wand.color import Color
from pprint import pprint

from layers.text import PointTextLayer
from layers.template import Template
from layers.color import ColorLayer, ColorBackgroundLayer
from layers.attribute import NumericAttribute as NA
from layers.attribute import StringAttribute as SA
from layers.attribute import AddAttribute as AA


class Mask(Template):
    "This Layer will out its children"

    def render(self, fresh=False):
        image = Image(width=int(self["width"]), height=int(self["height"]))
        for layer in sorted(self.layers, key=lambda l: l.order):
            if layer.content is not None or isinstance(layer, Template):
                img = layer.render(fresh)
                if img is not None:
                    image.composite(img, left=int(layer["left"] - self["left"]), top=int(layer["top"]- self["top"]))
        return image



if __name__ == "__main__":
    # color = ColorLayer("color", content="Red", left=AA(SA('-parent.left'), NA(100)), width=NA(300),
    #                    top=AA(SA('-parent.top'), NA(100)), height=NA(500))
    # bg = ColorBackgroundLayer("bg", content="White")
    # mask_bg = ColorBackgroundLayer("bg", content="Green")
    # mask = Template("mask", color, mask_bg, left=NA(
    #     200), width=NA(200), top=NA(100), height=NA(300))
    # temp = Template("main", mask, bg, left=NA(
    #     0), width=NA(500), top=NA(0), height=NA(700))

    color2 = ColorLayer("color", content="Red", left=NA(100), width=NA(300),
                       top=NA(100), height=NA(500))
    bg2 = ColorBackgroundLayer("bg", content="White")
    mask_bg2 = ColorBackgroundLayer("bg", content="Green")
    mask2 = Mask("mask", color2, mask_bg2, left=NA(200), width=NA(200), top=NA(100), height=NA(300))
    temp2 = Template("main", mask2, bg2, left=NA(0), width=NA(500), top=NA(0), height=NA(700))
    
    temp2.update_bounds()
    image = temp2.render()
    image.save(filename="test.png")
