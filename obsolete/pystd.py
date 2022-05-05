# For this to work, you have to do this:
# from pystd import *
# This will replace all the existing types with custom inherited types.
# It will keep the original methods, but will add some additional ones
# that could be useful for you.
# NOTE: literals are not this type by default. If you type [], {}, 1 or "a",
# they will be the original types. To fix that, either type list([]), dict({}), int(1), str("a")
# OR use FT % [] | FT([])

import builtins as _py
from typing import Any, Union

class list(_py.list):
    def to_python(self) -> _py.list:
        return _py.list(self)

    def join(self, sep: str):
        return sep.join([str(x) for x in self])

    def prepend(self, elem: Any):
        self.insert(0, elem)

    def is_sorted(self, *args, **kwargs):
        sorted_ = sorted(self, *args, **kwargs)
        return sorted_ == self

    def size(self):
        return len(self)

class dict(_py.dict):
    def to_python(self) -> _py.dict:
        return _py.dict(self)

    def _keys(self):
        keys = super().keys()
        return keys

    def _values(self):
        vals = super().values()
        return vals

    def keys(self) -> list[Any]:
        return list(self._keys())

    def values(self) -> list[Any]:
        return list(self._values())

    def reverse_get(self, value: Any) -> Union[list[Any], Any]:
        toreturn = FT([])

        for k,v in self.items():
            if v == value:
                toreturn.append(k)

        if toreturn.size() == 0:
            raise ValueError("Value not found in dict")
        elif toreturn.size() == 1:
            return toreturn[0]
        else:
            return toreturn

class float(_py.float):
    def to_python(self) -> _py.float:
        return _py.float(self)

    def round(self, digits):
        return round(self, digits)

    def pretty(self, digits = 3):
        string = f"{self.round(digits):.3f}"
        return string

class str(_py.str):
    def to_python(self) -> _py.str:
        return _py.str(self)

    def censor(self, char='*'):
        string = char * self.__len__()
        return FT % string

    def size(self):
        return len(self)

    def before_first(self, char):
        return FT % self.partition(char)[0]

    def before_last(self, char):
        return FT % self.rpartition(char)[0]

    def after_first(self, char):
        return FT % self.partition(char)[2]

    def after_last(self, char):
        return FT % self.rpartition(char)[2]


class StdTypeFixer:
    def fix(val):
        if isinstance(val, _py.list):
            return list(val)
        elif isinstance(val, _py.dict):
            return dict(val)
        elif isinstance(val, _py.float):
            return float(val)
        elif isinstance(val, _py.str):
            return str(val)

    def __mod__(self, val):
        return type(self).fix(val)

    def __call__(self, val):
        return type(self).fix(val)

FT = StdTypeFixer()

if __name__ == '__main__':
    # test
    d = {1: 3, 2: 4}
    print(type(d),
    type(FT(d)),
    type(FT % d))