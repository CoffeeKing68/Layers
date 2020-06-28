from layers.bounds import Bounds
from layers.exceptions import InsufficientBoundsError, InvalidBoundsError
from pytest import raises

class TestBounds():
    def test_cannot_make_bounds_with_1_bounding_value(self):
        with raises(InsufficientBoundsError):
            b = Bounds(start=1)
            b2 = Bounds(P20=20)

    def test_can_make_bounds_with_2_bounding_values(self):
        b = Bounds(start=1, end=20)
        b2 = Bounds(P20=40.0, center=70)

    def test_large_descriptors_must_be_greater_than_small_descriptors(self):
        """
        Basically, descriptors must be arranged in this order when ordered numerically;
        start -> center -> end or P0 -> P50 -> P100
        """
        with raises(InvalidBoundsError):
            Bounds(center=30, end=20) # center greater than end
            Bounds(start=54, end=50) # start greater than end
            Bounds(P23=40, p70=30) # 23% less than 70%

    def test_bounds_may_have_0_full(self):
        """Changed Bounds so that 0 width is allowed (< 0 is still illegal)."""
        Bounds(start=23, P40_5=23) # start equal to end
        Bounds(center=67, end=67) # center equal to end
        Bounds(P50=40, end=40) # start equal to end

    def test_percent_with_decimals_after_underscore_is_valid(self):
        test_pct = "P40_5"
        assert Bounds.parse_pct(test_pct) is not None

    def test_percent_descriptors_cannot_excede_100(self):
        assert Bounds.parse_pct("P300") is None

    def test_can_access_descriptors_and_percents(self):
        b = Bounds(start=20, P40=30)
        assert b.start == b["start"] == b[0] == b["0"] == b["p0"] == b["P0"] == 20
        assert b[40] == b["P40"] == b["p40"]== b["40"] == 30

    def test_full_attribute_will_be_a_nice_round_number(self):
        attributes = {'end': 1050.0, 'start': 916.4}
        full_should_be = 133.6

        b = Bounds(**attributes)
        assert b["full"] == full_should_be

