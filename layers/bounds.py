from layers.exceptions import InsufficientBoundsError, InvalidBoundsError
from decimal import Decimal as Dec

class Bounds():
    standard_bound_names = ["start", "center", "end", "full"]
    """
    :param kwargs: {start: 0, full: 20}.
    start=None, center=None, end=None, full=None
    """
    def __init__(self, **kwargs):
        self.__bounds = {key: val for key, val in kwargs.items() if Bounds.is_valid_descriptor(key)}
        self.__eval_bounds = {}

        if len(self.__bounds) == 2:
            self.determine_bounds()
        else:
            raise InsufficientBoundsError("Not enough bounding descriptors.")

    def __bound_property_maker(bound_name):
        def getter(self):
            return self.__eval_bounds.get(bound_name)
        def setter(self, value):
            self.__eval_bounds[bound_name] = value
        def deleter(bound_name):
            del self.__eval_bounds[bound_name]
        return property(getter, setter, deleter)

    start = __bound_property_maker("start")
    end = __bound_property_maker("end")
    center = __bound_property_maker("center")
    full = __bound_property_maker("full")

    def determine_bounds(self):
        # first "plot" points we have on quantifiable line
        plot = {}
        available_bounds = self.__bounds
        if "start" in self.__bounds:
            plot[Dec('0')] = Dec(repr(available_bounds.pop("start")))
        if "center" in self.__bounds:
            plot[Dec('50')] = Dec(repr(available_bounds.pop("center")))
        if "end" in self.__bounds:
            plot[Dec('100')] = Dec(repr(available_bounds.pop("end")))

        if len(plot) < 2: # Don't look for percent defs if we have all defs already
            for bound in list(available_bounds):
                # print(Bounds.parse_pct(bound), type(Bounds.parse_pct(bound)))
                pct = Bounds.parse_pct(bound)
                if pct is not None:
                    plot[Dec(repr(pct))] = Dec(repr(available_bounds.pop(bound)))

        if "full" in self.__bounds and len(plot) == 1: # if full was passed in
            pct, value = list(plot.items())[0]
            # pct = Dec(repr(pct))
            # value = Dec(repr(value))
            self.full = Dec(repr(self.__bounds["full"]))
        elif len(plot) == 2: # found 2 bound defs
            (pct, value), (bpct, bval) = sorted(plot.items())
            self.full = (bval - value) / (bpct - pct) * 100
        else:
            raise InsufficientBoundsError("Not enough bounds.")
        if self.full < 0:
            raise InvalidBoundsError("Full cannot be less than 0.")

        # print(repr(pct), repr(self.full), repr(value))
        self.end = (1 - pct / 100) * self.full + value
        self.start = value - pct * self.full / 100
        self.center = self.start + self.full / 2
        # print(self.start, type(self.start))
        # print(self.full, type(self.full))
        # self.convert_attributes_to_floats()

    def convert_attributes_to_floats(self):
        self.start = float(self.start)
        self.center = float(self.center)
        self.end = float(self.end)
        self.full = float(self.full)

    @staticmethod
    def is_valid_descriptor(key):
        """
        Checks if key is a recognised bound name or percentage
        :param key: Potentially valid bound (either in standard_bound_names or is in form p<pct>)
        """
        return key in Bounds.standard_bound_names or Bounds.parse_pct(key) is not None

    # def is_valid_pct_descriptor(pct_key):
    #     if pct_key[0].upper() == "P": # P or p
    #         try:
    #             Bounds.parse_pct(pct_key)
    #             return True
    #         except ValueError:
    #             pass
    #     return False

    @staticmethod
    def parse_pct(pct_key):
        if pct_key[0].upper() == "P":
            pct_key = pct_key[1:]
        pct_key = pct_key.replace("_", ".") # change underscore so that float will work
        try:
            pct = float(pct_key)
            if not pct > 100:
                return pct
        except:
            pass

    @property
    def bounds(self):
        return self.__eval_bounds

    def __getitem__(self, key):
        if key in self.__eval_bounds:
            return float(self.__eval_bounds[key])
        else:
            return float(self.get_percent(key))

    def get_percent(self, key):
        if isinstance(key, (int, float)): # is this a number?
            pct = key
        elif isinstance(key, str):
            pct = Bounds.parse_pct(key)
        else:
            raise ValueError("Pass in an int, float, <percent_string> or P/p<percent_string>")
        # print("get_percent")
        # print(self.start, type(self.start))
        # print(self.full, type(self.full))
        # print(pct, type(pct))
        return self.start + Dec(repr(pct)) * self.full / 100

    def __repr__(self):
        return f"Bounds: {self.__eval_bounds}"

    def shift(self, value):
        self.start += value
        self.center += value
        self.end += value

# if __name__ == "__main__":
#     b = Bounds(start=20, P40=30)
