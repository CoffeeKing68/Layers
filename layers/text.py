from layers.base_layers import Layer, PointLayer, ShapeLayer
from layers.exceptions import NotReadyToRenderError
from layers.dimensions import PTLYDimension, XDimension

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from wand.compat import nested
from string import ascii_lowercase as al
from string import ascii_uppercase as au
from math import ceil

class PointTextLayer(PointLayer):
    """
    A PointTextLayer is only defined by an xy coord.
    The text width is limited only by it's parent's width
    """
    def __init__(self, name, font, size, color, *args, **kwargs):
        self.font = font
        self.size = size
        self.color = color
        self.set_defaults(name, 1, 1, *args, **kwargs)
        self.dimensions["x"] = XDimension(self.x_attributes_required, self, **kwargs)
        self.dimensions["y"] = PTLYDimension(self.y_attributes_required, self, **kwargs)

    def get_in_depth_font_metrics(self):
        # if self.content is None:
        #     return {
        #         "median" : 0,
        #         "descender" : 0,
        #         "cap" : 0,
        #         "ascender": 0,
        #         "absolute_ascender": 0
        #         "absolute_descender": 0
        #     }
        # else:
        with nested(Image(width=1, height=1), Drawing()) as (temp_image, draw):
            draw.font = self.font
            draw.font_size = self.size

            max_descender = 0
            max_ascender = 0
            alpha_metrics = {}
            for l in al + au:
                alpha_metrics[l] = draw.get_font_metrics(temp_image, l, False)
                if alpha_metrics[l].y2 > max_ascender:
                    max_ascender = alpha_metrics[l].y2
                if alpha_metrics[l].y1 < max_descender:
                    max_descender = alpha_metrics[l].y1

            a_asc = 0
            a_desc = 0
            if self.content is None or self.content == "":
                a_asc = max_ascender
                a_asc = max_descender
            else:
                for l in self.content:
                    if l not in alpha_metrics:
                        alpha_metrics[l] = draw.get_font_metrics(temp_image, l, False)
                    if alpha_metrics[l].y2 > a_asc:
                        a_asc = alpha_metrics[l].y2
                    if alpha_metrics[l].y1 < a_desc:
                        a_desc = alpha_metrics[l].y1

            ml = draw.get_font_metrics(temp_image, al)
            mu = draw.get_font_metrics(temp_image, au)

            max_ascender = ceil(abs(max_ascender - max(ml.y2, mu.y2)))
            # absolute_height = ceil(a_asc) + ceil(- a_desc)

        return { # TODO maybe make cap relative to base
            "median" : ceil(ml.y2),
            "cap" : ceil(mu.y2),
            "ascender": ceil(max_ascender),
            "descender" : ceil(- max_descender),
            "absolute_ascender": ceil(a_asc),
            "absolute_descender": ceil(- a_desc),
        }

    def __getitem__(self, key):
        if key in self.y.ptl_mapping:
            if self.y.is_bounded: # y must be bounded for idm
                idm = self.get_in_depth_font_metrics()
                if key == "base":
                    return self["bottom"] - idm["absolute_descender"]
                elif key == "median":
                    return self["bottom"] - idm["absolute_descender"] - idm["median"]
                elif key == "cap":
                    return self["bottom"] - idm["absolute_descender"] - idm["cap"]
        else:
            return super().__getitem__(key)

    def should_render(self):
        """
        if any(self.font.has_changed, ...): # has changed
            self.render()
        """

    def render(self, fresh=False):
        if not fresh and self.pre_render is not None: # if fresh is false and there is a pre_render
            return self.pre_render
        if self.content is not None:
            # print(self.name, self.template.get_layer("name").content)
            with Drawing() as draw:
                draw.font = self.font
                draw.font_size = self.size
                if not isinstance(self.color, Color):
                    self.color = Color(self.color)
                draw.fill_color = self.color
                draw.text_antialias = True
                # get estimated width and height
                with Image(width=1, height=1) as temp_image:
                    metrics = draw.get_font_metrics(temp_image, self.content)
                    width = int(metrics.text_width)
                    height = int(metrics.text_height)

                img = Image(width=width + 100, height=height + 100)
                draw.text(10, height + 10, self.content)
                draw(img)
            img.trim()
            self.pre_render = img
            return img
        else:
            raise NotReadyToRenderError(f"{self.name} is not ready to render right now.")

class AreaTextLayer(ShapeLayer):
    """TextLayer that has a rect (Shape)."""
    def __init__(self, name, font, size, color, *args, **kwargs):
        self.font = font
        self.size = size
        self.color = color
        super().__init__(name, *args, **kwargs)

    def render(self, fresh=False):
        pass


