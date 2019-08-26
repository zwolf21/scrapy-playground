import re
import fnmatch

import furl
import pynumparser


def parse_number_range_exp(value, limits=(1, 9999)):
    if value is not None:
        parser = pynumparser.NumberSequence(limits=limits)
        return sorted(parser.parse(value))
