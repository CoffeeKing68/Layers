import pytest
from layers.template import Template
from layers.color import ColorLayer, ColorBackgroundLayer
from layers.text import PointTextLayer, AreaTextLayer
from layers.attribute import StringAttribute as SA
from layers.attribute import NumericAttribute as NA
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from wand.compat import nested

class TestPointTextLayer():
    def test_can_make_a_text_layer_without_content(self):
        l = PointTextLayer("layer", "Arial", 12, "Black", left=NA(30), top=NA(45))

    def test_cannot_make_text_layer_with_bad_coords(self):
        with pytest.raises(ValueError):
            PointTextLayer("layer", "Arial", 12, "Black", test=SA("parent.height"), wow=NA(12))

    def test_a_text_layer_requires_1_x_y_coord(self):
        with pytest.raises(ValueError):
            PointTextLayer("layer", "Arial", 12, "Black")
            PointTextLayer("layer", "Arial", 12, "Black", left=NA(40), XP30=NA(20))

    def test_can_make_a_text_layer_with_content(self):
        l = PointTextLayer("layer", "Arial", 12, "Black", content="hello world", left=NA(30), top=NA(45))

    def test_point_text_layer_can_render_when_content_and_parent_is_set(self):
        l = PointTextLayer("layer", "Arial", 12, "Black", content="hello world", left=NA(30), top=NA(45))
        temp = Template("temp", l, left=NA(0), width=NA(50), top=NA(0), height=NA(50))
        temp.update_bounds()
        l.render()
        assert l.pre_render is not None

    def test_can_make_a_text_layer_with_percent_bounds(self):
        l = PointTextLayer("layer", "Arial", 12, "Black", YP40=NA(30), XP50_50=SA("title.left"))

    def test_can_get_mean_indepth_font_metrics_for_ptl(self):
        bg = ColorBackgroundLayer("bg", content="White")
        l = PointTextLayer("l", "Arial", 12, "Black", content="Hpqrs", left=NA(0), base=NA(20))
        l2 = PointTextLayer("l2", "Arial", 12, "Black", content="e", left=NA(10), median=NA(50))
        # l3 = PointTextLayer("l3", "Arial", 12, "Black", content="l", left=NA(20), descender=NA(50))
        l4 = PointTextLayer("l4", "Arial", 12, "Black", content="l", left=NA(30), cap=NA(50))
        # l5 = PointTextLayer("l5", "Arial", 12, "Black", content="o", left=NA(40), ascender=NA(50))

        temp = Template("temp", l, l2, bg, left=NA(0),
        # temp = Template("temp", l, l2, l3, l4, l5, left=NA(0),
                # right=SA("l5.right"), top=NA(0), bottom=SA("l5.bottom"))
                right=SA("l.right"), top=NA(0), bottom=SA("l.bottom"))
        temp.update_bounds()
        temp.render().save(filename="tests/images/test_can_get_mean_indepth_font_metrics_for_ptl.png")

    def test_idm_works_for_text_layer_without_content(self):
        bg = ColorBackgroundLayer("bg", content="White")
        # content is None
        layer = PointTextLayer("layer", "Arial", 12, "Black", left=NA(0), base=NA(40))
        square = ColorLayer("sqr", content="Red", width=NA(20), height=NA(20),
                bottom=SA("layer.cap"), left=NA(25))
        temp = Template("temp", layer, square, bg, left=NA(0),
                width=NA(50), top=NA(0), height=NA(50))
        temp.update_bounds()
        temp.render().save(filename="tests/images/test_idm_works_for_text_layer_without_content.png")

    def test_setting_base_on_ptl_is_same_as_drawing_text(self):
        width = 100
        text = "Hpqrs"
        left = 0
        base = 20
        median = 40
        median_offset_for_font_size_12 = 6
        bg_color = "White"
        bg = ColorBackgroundLayer("bg", content=bg_color)
        l = PointTextLayer("l", "Arial", 12, "Black", content=text, left=NA(left), base=NA(base))
        l2 = PointTextLayer("l2", "Arial", 12, "Black", content=text, left=NA(left), median=NA(median))

        temp = Template("temp", l, l2, bg, left=NA(0),
                right=NA(width), top=NA(0), bottom=NA(width))
        temp.update_bounds()
        img = temp.render()
        img.save(filename="tests/images/test_setting_base_on_ptl_is_same_as_drawing_text.png")

        with nested(Image(width=width, height=width, background=Color(bg_color)),
            Drawing()) as (img2, draw):
            draw.font = l.font
            draw.font_size = l.size
            draw.text(left, base, text)
            draw.text(left, median + median_offset_for_font_size_12, text)
            draw(img2)
            img2.save(filename="tests/images/test_setting_base_on_ptl_is_same_as_drawing_text_2.png")

            location, diff = img.similarity(img2, metric="absolute")
            assert diff == 0

