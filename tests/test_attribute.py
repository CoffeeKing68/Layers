from layers.attribute import StringAttribute as SA
from layers.attribute import NumericAttribute as NA
from layers.attribute import AddAttribute as AA
from layers.attribute import MaxAttribute as MinA
from layers.template import Template
from layers.color import ColorLayer, ColorBackgroundLayer
from layers.text import PointTextLayer as PTL
import pytest
from os.path import join
from layers.exceptions import LayerDoesNotExistError
# GetAttribute("")
# SumAttribute("parent.width", NegateAttribute("text.height"))
# "template.width,-45", "fill:template.width,template.height"
# "get:template.width|negate:45" ""
# SumAttributes(SA("template.width"), NA(45, negative=True))

class TestStringAttribute():
    def test_can_make_string_attribute(self):
        SA("layer.width")
        SA("parent.XP40")
        SA("template.right")

    def test_can_make_negative_string_attribute(self):
        """Tests if negative SAs can be initialised
        and if the different conventions will produce the same result"""
        negative_str_attr_1 = SA("-title.right")
        negative_str_attr_2 = SA("title.right", True)

        # test_layer_1 and test_layer_2 will have same left value
        title = PTL("title", "Arial", 15, "Black", content="Hello World",
            left=NA(0), top=NA(0))

        test_layer_1 = ColorLayer("test_layer_1", content="Blue",
            left=negative_str_attr_1, right=SA("parent.right"),
            top=SA("title.top"), height=NA(20))

        test_layer_2 = ColorLayer("test_layer_2", content="Green",
            left=negative_str_attr_2, right=SA("parent.right"),
            top=SA("test_layer_1.top"), height=NA(20))

        temp = Template("temp", title, test_layer_1, test_layer_2,
            left=NA(0), width=NA(100),
            top=NA(0), height=NA(100))

        temp.update_bounds()
        assert test_layer_1["left"] == test_layer_2["left"]

    def test_exception_raised_if_no_existant_layer_is_referenced_in_SA(self):
        with pytest.raises(LayerDoesNotExistError):
            pt = PTL("test", "Arial", 15, "Black", content="Hello", left=NA(0),
                top=NA(0))
            sq = ColorLayer("square", content="Red", left=NA(0),
                top=SA("doesnotexist.bottom"), width=NA(20), height=NA(20))
            bg = ColorBackgroundLayer("bg", content="Green")
            bg2 = ColorBackgroundLayer("bg2", content="White")
            temp2 = Template("temp2", sq, bg, left=NA(0), width=NA(25),
                top=NA(0), height=NA(25))
            temp = Template("temp", pt, bg2, temp2, left=NA(0), width=NA(100),
                top=NA(0), height=NA(100))
            temp.update_bounds()
            # from pprint import pprint
            # pprint(temp.get_layer("temp2").__dict__)
            temp.render().save(filename="tests/images/test_exception_raised_if_no_existant_layer_is_referenced_in_SA.png")

    # def test_can_unset_an_attributes_evaluated_value(self):
    #     """
    #     This test won't work because the bounds of pt are not reset before l1's
    #     attribute is evaluated. The Layer.reset_bounds must reset bounds and unset
    #     attributes.
    #     """
    #     pt = PTL("ptl", "", 15, "", content="H", left=NA(0), top=NA(0))
    #     # pt.content = "Wor" # changing content of pt should change width -> l1.left
    #     l1 = ColorLayer("l1", content="Blue", left=AA(SA("ptl.right"), NA(1)), height=NA(20),
    #         right=SA("parent.right"), top=SA("parent.top"))
    #     temp = Template("temp", l1, pt,  left=NA(0), top=NA(0), width=NA(50), height=NA(50))
    #     temp.update_bounds() # get evaluated values for attributes
    #     first_left = l1.x.attributes["left"].evaluated_value
    #     temp.render().save(filename="tests/images/test_can_unset_an_attributes_evaluated_value_1.png")
    #     pt.content = "Wor"
    #     # l1.x.attributes["left"].unset_evaluated_value() # unset's ev, cannot use saved value
    #     # l1.x.bounds = None
    #     # print(l1.x.attributes["left"].evaluated_value)
    #     # pt.update_bounds()
    #     # print(l1.x.attributes["left"].evaluated_value)
    #     temp.unset_bounds_and_attributes()
    #     temp.update_bounds()
    #     # print(l1.x.attributes["left"].evaluated_value)
    #     second_left = l1.x.attributes["left"].evaluated_value
    #     temp.render().save(filename="tests/images/test_can_unset_an_attributes_evaluated_value_2.png")
    #     assert first_left != second_left

class TestNumericAttribute():
    def test_can_make_numeric_attribute(self):
        NA(40)
        NA(-30)
        NA(12, True)

    def test_can_make_negative_numeric_attribute(self):
        """Tests if negative NAs can be initialised
        and if the different conventions will produce the same result"""
        negative_num_attr_1 = NA(-30)
        negative_num_attr_2 = NA(30, True)

        # test_layer_1 and test_layer_2 will have same left value
        title = PTL("title", "Arial", 15, "Black", content="Hello World",
            left=NA(0), top=NA(0))

        test_layer_1 = ColorLayer("test_layer_1", content="Blue",
            left=negative_num_attr_1, right=SA("parent.right"),
            top=SA("title.top"), height=NA(20))

        test_layer_2 = ColorLayer("test_layer_2", content="Green",
            left=negative_num_attr_2, right=SA("parent.right"),
            top=SA("test_layer_1.top"), height=NA(20))

        temp = Template("temp", title, test_layer_1, test_layer_2,
            left=NA(0), width=NA(100),
            top=NA(0), height=NA(100))

        temp.update_bounds()
        assert test_layer_1["left"] == test_layer_2["left"]

class TestAAttribute():
    def test_can_make_add_attribute(self):
        add_attr = AA(SA("template.height"), NA(-45))

    def test_template_with_add_attribute_can_render(self):
        title = PTL("title", "Arial", 15, "Black", content="Hello World",
            left=NA(0), top=NA(0))
        sub_title = PTL("sub_title", "Arial", 15, "Black", content="Bottom Text",
            left=NA(10), bottom=AA(SA("template.height"), NA(45, negative=True)))
        bg = ColorBackgroundLayer("bg", content="White")
        temp = Template("temp", title, sub_title, bg, left=NA(0), top=NA(0),
            width=NA(200), height=NA(200))

        temp.update_bounds()
        image = temp.render()
        image.save(filename=f"tests/images/test_template_with_add_attribute_can_render.jpg")

class TestMaxAttribute():
    def test_can_make_a_max_attribute(self):
        mmax = MinA(NA(50), NA(60))

    def test_template_with_max_attribute_can_render(self):
        c1 = ColorLayer("color1", content="Green", left=NA(0), width=NA(50),
            top=NA(0), height=NA(50))
        c2 = ColorLayer("color2", content="Blue", left=NA(0), width=NA(60),
            top=SA("color1.bottom"), height=NA(50))
        text = PTL("test", "Arial", 15, "Black", content="Hello World",
            left=MinA(SA("color1.right"), SA("color2.right")), top=SA("color2.bottom"))
        bg = ColorBackgroundLayer("name", content="White")
        layers = [c1, c2, bg, text]
        temp = Template("temp", *layers, left=NA(0), top=NA(0), width=NA(300),
            height=NA(300))
        temp.update_bounds()
        assert text["left"] == 60
        # image = temp.render()
        # image.save(filename="tests/images/test_template_with_max_attribute_can_render.jpg")
