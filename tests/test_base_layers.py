import pytest
from layers.template import Template
from layers.color import ColorLayer, ColorBackgroundLayer
from layers.text import PointTextLayer as PTL
from layers.text import AreaTextLayer
from layers.attribute import StringAttribute as SA
from layers.attribute import NumericAttribute as NA
from layers.attribute import AddAttribute as AA

class TestLayer():
    def test_can_order_layers_for_rendering(self):
        kwargs = {
            "left": SA("parent.left"),
            "right": SA("parent.right"),
            "top": SA("parent.top"),
            "bottom": SA("parent.bottom")
        }
        l1 = ColorLayer("layer_1", content="#FF0000", order=1, **kwargs)
        l2 = ColorLayer("layer_1", content="#00FF00", order=2, **kwargs)
        temp = Template("temp", l1, l2, left=NA(0), width=NA(50),
            top=NA(0), height=NA(50))

        temp.update_bounds()

        green_above = temp.render()
        color_of_top_left_most_pixel = green_above.export_pixels(width=1, height=1)
        # RGBA, [1] is green
        assert color_of_top_left_most_pixel[:3] == [0, 255, 0]

        l1.order = 3 # move red above
        red_above = temp.render()
        color_of_top_left_most_pixel = red_above.export_pixels(width=1, height=1)
        assert color_of_top_left_most_pixel[:3] == [255, 0, 0]

    def test_layers_passed_in_first_without_order_are_rendered_first(self, save_images):
        kwargs = {
            "left": SA("parent.left"),
            "right": SA("parent.right"),
            "top": SA("parent.top"),
            "bottom": SA("parent.bottom")
        }
        l1 = ColorLayer("layer_1", content="#FF0000", **kwargs) # red
        l2 = ColorLayer("layer_1", content="#00FF00", **kwargs) # green
        # l1 is first, is rendered first; therefore l2 (green) should be on top
        temp = Template("temp", l1, l2, left=NA(0), width=NA(50),
            top=NA(0), height=NA(50))
        temp.update_bounds()

        green_above = temp.render()
        color_of_top_left_most_pixel = green_above.export_pixels(width=1, height=1)
        assert color_of_top_left_most_pixel[:3] == [0, 255, 0] # RGBA, [1] is green

        # remake template, now l2 is first, l1 rendered last
        temp = Template("temp", l2, l1, left=NA(0), width=NA(50),
            top=NA(0), height=NA(50))
        temp.update_bounds()
        red_above = temp.render()

        color_of_top_left_most_pixel = red_above.export_pixels(width=1, height=1)
        assert color_of_top_left_most_pixel[:3] == [255, 0, 0]
        if save_images:
            green_above.save(filename="tests/images/green_above.png")
            red_above.save(filename="tests/images/red_above.png")

    def test_can_unset_attributes_evaluated_values(self):
        """Because the content of pt is changing per iteration, the left of
        square should change as well (top should change due to p in people)."""
        content_list = ["hello world", "people"]
        square_lefts = [] # stores left values per iteration
        square_tops = []
        pt = PTL("pt", "Arial", 15, "Black", left=NA(0), top=NA(0))
        square = ColorLayer("square", content="Red", left=AA(SA("pt.right")),
            top=SA("pt.bottom"), width=NA(20), height=NA(20))
        bg = ColorBackgroundLayer("bg", content="White")
        temp = Template("temp", pt, square, bg, left=NA(0), top=NA(0),
            height=NA(100), width=NA(100))
        for i, content in enumerate(content_list):
            pt.pre_render = None
            pt.content = content
            temp.unset_bounds_and_attributes()
            temp.update_bounds()
            temp.render().save(filename=f"tests/images/{i}_test_can_unset_attributes_evaluated_values.png")
            square_lefts.append(temp.get_layer("square")["left"])
            square_tops.append(temp.get_layer("square")["top"])
        assert square_lefts[0] != square_lefts[1]
        assert square_tops[0] != square_tops[1]

    def test_can_render_color_overlay(self):
        pt = PTL("pt", "Arial", 15, "Black", content="PT", left=NA(0), top=NA(0))
        pt2 = PTL("pt2", "Arial", 15, "Black", content="PT2", left=NA(0),
            top=AA(SA("pt.bottom"), NA(5)))
        bg = ColorBackgroundLayer("bg", content="Red")
        temp = Template("temp", pt, pt2, bg, left=NA(0), width=NA(50), top=NA(0),
            height=NA(50))
        temp.update_bounds()
        image = temp.render()
        image.save(filename="tests/images/test_can_render_color_overlay_1.png")
        overlay = pt2.color_overlay("Blue")
        image.composite(overlay, int(pt2["left"]), int(pt2["top"]))
        image.save(filename="tests/images/test_can_render_color_overlay_2.png")

    def test_can_render_shadow(self):
        pt = PTL("pt", "Arial", 15, "Black", content="PT", left=NA(0), top=NA(0))
        pt2 = PTL("pt2", "Arial", 15, "Black", content="PT2", left=NA(0),
            top=AA(SA("pt.bottom"), NA(5)))
        bg = ColorBackgroundLayer("bg", content="White")
        temp = Template("temp", pt, pt2, bg, left=NA(0), width=NA(50), top=NA(0),
            height=NA(50))
        temp.update_bounds()
        image = temp.render()
        image.save(filename="tests/images/test_can_render_shadow_1.png")
        shadow = pt2.shadow(2, 2, radius=4, sigma=2)
        image.composite(shadow, 0, 0)
        image.save(filename="tests/images/test_can_render_shadow_2.png")

class TestShapeLayer():
    # ShapeLayer is abstract so testing using AreaTextLayer
    def area_text_layer(self):
        return AreaTextLayer("area_text_layer", "Arial", 12, "Black", left=NA(0), width=NA(40), bottom=NA(50), height=NA(50))

    def test_can_make_a_shape_layer(self):
        layer = self.area_text_layer()

    def test_can_update_x_bounds(self):
        layer = self.area_text_layer()
        temp = Template("temp", layer, left=NA(0), width=NA(50), top=NA(0), height=NA(50))
        layer.x.update_bounds()

    def test_can_update_y_bounds(self):
        layer = self.area_text_layer()
        temp = Template("temp", layer, left=NA(0), width=NA(50), top=NA(0), height=NA(50))
        layer.y.update_bounds()


class TestPointLayer():
    # PointLayer is abstract so testing on concrete object PTL
    def point_text_layer(self):
        return PTL("area_text_layer", "Arial", 12, "Black", content="test", left=NA(0), bottom=NA(50))

    def test_can_make_a_point_layer(self):
        layer = self.point_text_layer()

    def test_can_update_x_bounds_when_attributes_are_evaluatable_and_content_is_set(self):
        layer = self.point_text_layer()
        temp = Template("temp", layer, left=NA(0), width=NA(50), top=NA(0), height=NA(50))
        layer.x.update_bounds()

    def test_can_update_y_bounds_when_attributes_are_evaluatable_and_content_is_set(self):
        layer = self.point_text_layer()
        temp = Template("temp", layer, left=NA(0), width=NA(50), top=NA(0), height=NA(50))
        layer.y.update_bounds()

