"""!
\file value.py Represents the value of functions in the case of PGMs
"""

import math
from types import FunctionType
from typing import Callable, Optional, Union
from xml.etree import ElementTree as ET

from pygmodels.utils import is_optional_type, is_type
from pygmodels.value.valuetype.abstractvalue import (
    AbstractSetValue,
    AbstractValue,
    Interval,
    IntervalConf,
    TypedSequence,
)


class Value(AbstractValue):
    """"""

    def is_numeric(self) -> bool:
        """"""
        return isinstance(self.value, (float, int, bool))

    def is_string(self) -> bool:
        """"""
        return isinstance(self.value, str)

    def is_container(self) -> bool:
        """"""
        types = (tuple, frozenset)
        return isinstance(self.value, types)

    def is_callable(self) -> bool:
        """"""
        return callable(self.value)


class NumericValue(Value):
    """!"""

    def __init__(self, v: Union[float, int, bool]):
        is_type(v, "v", (float, int, bool), True)
        self._v = v

    @property
    def value(self) -> Union[float, int, bool]:
        return self._v

    def __myop__(self, func, other) -> Union[Value, bool]:
        """"""
        is_type(other, "other", (NumericValue, float, int, bool))
        if not isinstance(other, NumericValue):
            other = NumericValue(v=other)
        #
        return func(self, other)

    @staticmethod
    def __cond_check__(s, o):
        """"""
        cond1 = s.value == math.inf
        cond2 = s.value == (-math.inf)
        cond3 = o.value == (math.inf)
        cond4 = o.value == (-math.inf)
        return cond1, cond2, cond3, cond4

    @staticmethod
    def __add_cond__(s, o):
        """"""
        s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
        if s_inf and o_minf:
            raise ValueError(f"{s.value} + {o.value} is undefined")
        if s_minf and o_inf:
            raise ValueError(f"{s.value} + {o.value} is undefined")
        if s_inf and o_inf:
            return (NumericValue(math.inf), True)
        if s_minf and o_minf:
            return (NumericValue(-math.inf), True)
        return (None, False)

    @staticmethod
    def __sub_cond__(s, o):
        """"""
        s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
        if s_inf and o_minf:
            return (NumericValue(math.inf), True)
        if s_minf and o_inf:
            return (NumericValue(-math.inf), True)
        if s_inf and o_inf:
            raise ValueError(f"{s.value} - {o.value} is undefined")
        if s_minf and o_minf:
            raise ValueError(f"{s.value} - {o.value} is undefined")
        return (None, False)

    @staticmethod
    def __mul_cond__(s, o):
        """"""
        s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
        if s_inf and o_minf:
            return (NumericValue(-math.inf), True)
        if s_minf and o_inf:
            return (NumericValue(-math.inf), True)
        if s_inf and o_inf:
            return (NumericValue(math.inf), True)
        if s_minf and o_minf:
            return (NumericValue(math.inf), True)
        if s.value == 0 and (o_inf or o_minf):
            return (NumericValue(0), True)
        if o.value == 0 and (s_minf or s_inf):
            return (NumericValue(0), True)
        return (None, False)

    @staticmethod
    def __truediv_cond__(s, o):
        """"""
        s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
        if s_inf and o_minf:
            raise ValueError(f"{s.value} / {o.value} is undefined")
        if s_minf and o_inf:
            raise ValueError(f"{s.value} / {o.value} is undefined")
        if s_inf and o_inf:
            raise ValueError(f"{s.value} / {o.value} is undefined")
        if s_minf and o_minf:
            raise ValueError(f"{s.value} / {o.value} is undefined")
        return (None, False)

    @staticmethod
    def __pow_cond__(s, o):
        """"""
        s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
        if s_inf and o_inf:
            return (NumericValue(math.inf), True)
        if s_inf and o_minf:
            raise ValueError(f"{s.value} ** {o.value} is undefined")
        if s_minf and o_inf:
            raise ValueError(f"{s.value} ** {o.value} is undefined")
        if s_minf and o_minf:
            raise ValueError(f"{s.value} ** {o.value} is undefined")
        return (None, False)

    @staticmethod
    def __add_op__(s, o):
        """
        infinity aware summation from: Shao 2010, p. 3
        """
        val, is_cond = NumericValue.__add_cond__(s=s, o=o)
        if is_cond:
            return val
        return NumericValue(s.value + o.value)

    @staticmethod
    def __sub_op__(s, o):
        """
        infinity aware subtraction from: Shao 2010, p. 3
        """
        val, is_cond = NumericValue.__sub_cond__(s=s, o=o)
        if is_cond:
            return val
        return NumericValue(s.value - o.value)

    @staticmethod
    def __mul_op__(s, o):
        """
        infinity aware subtraction from: Shao 2010, p. 3
        """
        val, is_cond = NumericValue.__mul_cond__(s=s, o=o)
        if is_cond:
            return val
        return NumericValue(s.value * o.value)

    def __add__(self, other):
        """
        infinity aware summation from: Shao 2010, p. 3
        """
        return self.__myop__(func=NumericValue.__add_op__, other=other)

    def __radd__(self, other):
        """"""

        def radd_op(s, o):
            """"""
            val, is_cond = NumericValue.__add_op__(s=o, o=s)
            if is_cond:
                return val
            return NumericValue(o.value + s.value)

        return self.__myop__(func=radd_op, other=other)

    def __sub__(self, other):
        """
        infinity aware summation from: Shao 2010, p. 3
        """
        return self.__myop__(func=NumericValue.__sub_op__, other=other)

    def __rsub__(self, other):
        """"""

        def rsub_op(s, o):
            """"""
            val, is_cond = NumericValue.__sub_cond__(s=o, o=s)
            if is_cond:
                return val
            return NumericValue(o.value - s.value)

        return self.__myop__(func=rsub_op, other=other)

    def __mul__(self, other):
        """
        infinity aware multiplication
        """
        return self.__myop__(func=NumericValue.__mul_op__, other=other)

    def __rmul__(self, other):
        """
        infinity aware multiplication
        """

        def mul_op(s, o):
            val, is_cond = NumericValue.__mul_cond__(s=o, o=s)
            if is_cond:
                return val
            return NumericValue(o.value * s.value)

        return self.__myop__(func=mul_op, other=other)

    def __truediv__(self, other):
        """"""

        def truediv_op(s, o):
            """"""
            val, is_cond = NumericValue.__truediv_cond__(s=s, o=o)
            return NumericValue(s.value / o.value)

        return self.__myop__(func=truediv_op, other=other)

    def __floordiv__(self, other):
        """"""

        def floordiv_op(s, o):
            """"""
            val, is_cond = NumericValue.__truediv_cond__(s=s, o=o)
            return NumericValue(s.value // o.value)

        return self.__myop__(func=floordiv_op, other=other)

    def __mod__(self, other):
        """"""

        def mod_op(s, o):
            """"""
            s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
            if s_inf or s_minf or o_inf or o_minf:
                raise ValueError(
                    f"% operation is not supported with infinities {s.value}"
                    + f" and {o.value}"
                )
            return NumericValue(s.value % o.value)

        return self.__myop__(func=mod_op, other=other)

    def __pow__(self, other):
        """"""

        def pow_op(s, o):
            """"""
            val, is_cond = NumericValue.__pow_cond__(s=s, o=o)
            if is_cond:
                return val
            return NumericValue(pow(s.value, o.value))

        return self.__myop__(func=pow_op, other=other)

    def __rtruediv__(self, other):
        """"""

        def rtruediv_op(s, o):
            """"""
            val, is_cond = NumericValue.__truediv_cond__(s=o, o=s)
            return NumericValue(o.value / s.value)

        return self.__myop__(func=rtruediv_op, other=other)

    def __rfloordiv__(self, other):
        """"""

        def rfloordiv_op(s, o):
            """"""
            val, is_cond = NumericValue.__truediv_cond__(s=o, o=s)
            return NumericValue(o.value // s.value)

        return self.__myop__(func=rfloordiv_op, other=other)

    def __rmod__(self, other):
        """"""

        def rmod_op(s, o):
            """"""
            s_inf, s_minf, o_inf, o_minf = NumericValue.__cond_check__(s=s, o=o)
            if s_inf or s_minf or o_inf or o_minf:
                raise ValueError(
                    f"% operation is not supported with infinities {s.value}"
                    + f" and {o.value}"
                )
            return NumericValue(o.value % s.value)

        return self.__myop__(func=rmod_op, other=other)

    def __rpow__(self, other):
        """"""

        def rpow_op(s, o):
            """"""
            val, is_cond = NumericValue.__pow_cond__(s=o, o=s)
            if is_cond:
                return val
            return NumericValue(pow(o.value, s.value))

        return self.__myop__(func=rpow_op, other=other)

    def __lt__(self, other):
        return self.__myop__(func=lambda s, o: s.value < o.value, other=other)

    def __le__(self, other):
        return self.__myop__(func=lambda s, o: s.value <= o.value, other=other)

    def __gt__(self, other):
        return self.__myop__(func=lambda s, o: s.value > o.value, other=other)

    def __ge__(self, other):
        return self.__myop__(func=lambda s, o: s.value >= o.value, other=other)

    def __eq__(self, other):
        return self.__myop__(func=lambda s, o: s.value == o.value, other=other)

    def __ne__(self, other):
        return self.__myop__(func=lambda s, o: s.value != o.value, other=other)


class StringValue(Value):
    """!"""

    def __init__(self, v: str):
        is_type(v, "v", str, True)
        self._v = v

    @property
    def value(self):
        return self._v


class ContainerValue(Value, TypedSequence):
    """"""

    def __init__(self, v: Union[tuple, frozenset], name="container", member_type=Value):
        """"""
        types = (tuple, frozenset)
        is_type(v, "v", types, True)
        super().__init__(iterable=v, name=name, member_type=member_type)

    @property
    def value(self) -> Union[tuple, frozenset]:
        return self._iter

    def __str__(self) -> str:
        """"""
        m = ET.Element(self.__name__)
        m.set("name", self._name)
        for v in self.value:
            vv = ET.SubElement(m, "value")
            vv.set("type", self._member_type.__name__)
            vv.text = str(v)
        ET.indent(m)
        return ET.tostring(m, encoding="unicode")


class NTupleValue(ContainerValue):
    """"""

    def __init__(self, v: tuple):
        is_type(v, "v", tuple, True)
        super().__init__(v=v, name="ntuple", member_type=NumericValue)

    def is_numeric(self) -> bool:
        return True

    def __myop__(self, func: FunctionType, other: Union[ContainerValue, int, float]):
        """"""
        is_type(other, "other", (NTupleValue, int, float), True)
        if isinstance(other, NTupleValue):
            cond1 = len(other) == len(self)
            cond2 = len(other) == 1
            cond3 = cond1 or cond2
            if not cond3:
                raise ValueError(
                    f"dimension mismatch between {len(self)}" + f" and {len(other)}"
                )
        else:
            other = NTupleValue(tuple([NumericValue(other)]))
        dims = list(range(len(self)))
        if len(other) == 1:
            # broadcast
            other = NTupleValue(tuple([other[0] for _ in dims]))
        vs = [func(self[i], other[i]) for i in dims]
        return NTupleValue(tuple(vs))

    def __add__(self, other):
        """"""
        return self.__myop__(func=lambda s, o: s + o, other=other)

    def __sub__(self, other):
        return self.__myop__(func=lambda s, o: s - o, other=other)

    def __rsub__(self, other):
        return self.__myop__(func=lambda s, o: o - s, other=other)

    def __mul__(self, other):
        return self.__myop__(func=lambda s, o: s * o, other=other)

    def __truediv__(self, other):
        return self.__myop__(func=lambda s, o: s / o, other=other)

    def __floordiv__(self, other):
        return self.__myop__(func=lambda s, o: s // o, other=other)

    def __rtruediv__(self, other):
        """"""
        return self.__myop__(func=lambda s, o: o / s, other=other)

    def __rfloordiv__(self, other):
        """"""
        return self.__myop__(func=lambda s, o: o // s, other=other)


class CallableValue(Value):
    def __init__(self, v: FunctionType):
        is_type(v, "v", FunctionType, True)
        self._v = v

    @property
    def value(self):
        return self._v


class SetValue(Value, AbstractSetValue):
    "Value contained by a set"

    def __init__(self, v: Optional[Value] = None, set_id: Optional[str] = None):
        is_optional_type(v, "v", Value, True)
        self._v = v

        is_optional_type(set_id, "set_id", str, True)
        self._set = set_id

    @property
    def belongs_to(self) -> str:
        """"""
        if self._set is None:
            raise ValueError("Value not associated to any set")
        return self._set

    @property
    def value(self) -> object:
        """inner python object attached to value"""
        return self.fetch().value

    def fetch(self) -> Value:
        """"""
        if self._v is None:
            raise ValueError("Value is not associated to any data")
        return self._v

    def __str__(self) -> str:
        """"""
        m = ET.Element("SetValue")
        m.set("set", self.belongs_to)
        m.text = str(self.value)
        ET.indent(m)
        return ET.tostring(m, encoding="unicode")


class NumericInterval(Interval):
    ""

    def __init__(
        self,
        lower: NumericValue,
        upper: NumericValue,
        open_on: Optional[IntervalConf] = None,
        name: Optional[str] = None,
    ):
        s = ""
        if open_on is None:
            s += "[" + str(lower) + ", " + str(upper) + "]"
        elif open_on == IntervalConf.Lower:
            s += "(" + str(lower) + ", " + str(upper) + "]"
        elif open_on == IntervalConf.Upper:
            s += "[" + str(lower) + ", " + str(upper) + ")"
        elif open_on == IntervalConf.Both:
            s += "(" + str(lower) + ", " + str(upper) + ")"
        if name:
            s = name
        is_type(lower, "lower", NumericValue, True)
        is_type(upper, "upper", NumericValue, True)
        lower = min(lower, upper)
        upper = max(lower, upper)
        super().__init__(name=s, lower=lower, upper=upper, open_on=open_on)

    def length(self):
        """
        Lebesque measure as per: Epps, 2014, p. 19
        Originally defined for (a, b] type intervals but the derivation in
        p. 19-20 show that results are equivalent for (a, b) as well.
        """
        return self.upper - self.lower

    def _has_number(self, nb: NumericValue) -> bool:
        ""
        v = nb.value if isinstance(nb, NumericValue) else nb
        cond1 = (v >= self.lower) if self.is_lower_bounded() else (v > self.lower)
        cond2 = (v <= self.upper) if self.is_upper_bounded() else (v < self.upper)
        return cond1 and cond2

    def __contains__(self, other: Interval) -> bool:
        ""
        has_upper = self._has_number(other.upper)
        has_lower = self._has_number(other.lower)
        return has_upper and has_lower

    def __and__(self, other: Interval):
        """
        interval intersection from Jaulin 2001, p. 18, 2.37
        """
        lows = [
            (self.lower, self.is_lower_bounded()),
            (other.lower, other.is_lower_bounded()),
        ]

        ups = [
            (self.upper, self.is_upper_bounded()),
            (other.upper, other.is_upper_bounded()),
        ]
        max_low = max(lows, key=lambda x: x[0])
        min_up = min(ups, key=lambda x: x[0])
        if not max_low[1] and not min_up[1]:
            open_on = IntervalConf.Both
        elif max_low[1] and not min_up[1]:
            open_on = IntervalConf.Upper
        elif not max_low[1] and min_up[1]:
            open_on = IntervalConf.Lower
        else:
            open_on = None
        return NumericInterval(lower=max_low[0], upper=min_up[0], open_on=open_on)

    def __rand__(self, other):
        return self & other

    def __or__(self, other):
        """
        Several interpretations are possible, but in most case the or
        operation results not in an interval. One needs to define it either as
        interval hull as it is done by Jaulin 2001, p. 18
        """
        raise NotImplementedError

    def _apply_op(
        self, other: Interval, op: Callable[[NumericValue, NumericValue], NumericValue]
    ):
        """ """
        lower_bounded = self.is_lower_bounded() and other.is_lower_bounded()
        upper_bounded = self.is_upper_bounded() and other.is_upper_bounded()

        lower = op(self.lower, other.lower)
        upper = op(self.upper, other.upper)
        vals = [(lower, lower_bounded), (upper, upper_bounded)]
        min_val = min(vals, key=lambda x: x[0])
        max_val = max(vals, key=lambda x: x[0])
        lower, lower_bounded = min_val
        upper, upper_bounded = max_val
        if not lower_bounded and not upper_bounded:
            open_on = IntervalConf.Both
        elif not lower_bounded and upper_bounded:
            open_on = IntervalConf.Lower
        elif lower_bounded and not upper_bounded:
            open_on = IntervalConf.Upper
        else:
            open_on = None
        return NumericInterval(lower=lower, upper=upper, open_on=open_on)

    def __add__(self, other: Interval):
        ""
        return self._apply_op(other=other, op=lambda x, y: x + y)

    def __lt__(self, other: Union[Interval, NumericValue]) -> bool:
        """
        From Dawood, 2011, p. 9
        """
        if isinstance(other, NumericValue):
            in_int = self._has_number(other)
            return (not in_int) and self.upper < other
        if isinstance(other, Interval):
            s_up = self.upper
            o_low = other.lower
            in_self = o_low in self
            is_big = s_up < o_low
            return (not in_self) and is_big
        raise TypeError(
            f"only interval and numeric value types are supported {type(other)}"
        )

    def __eq__(self, other: Interval) -> bool:
        """
        Equality for intervals
        """
        if isinstance(other, Interval):
            if other._open_on != self._open_on:
                return False
            return (other.lower == self.lower) and (other.upper == self.upper)
        return False

    def __le__(self, other: Interval) -> bool:
        ""
        is_less = self < other
        is_equal = self == other
        return is_less or is_equal

    def __gt__(self, other: Interval) -> bool:
        ""
        is_less_or_equal = self <= other
        return not is_less_or_equal

    def __hash__(self):
        """"""
        return hash((str(self.lower), str(self.upper), self._open_on, self._name))

    def __str__(self) -> str:
        """ """
        m = ET.Element(type(self).__name__)
        if self._name is not None:
            m.set("name", self._name)
        if self._open_on == IntervalConf.Lower:
            m.set("open_on", "lower")
        elif self._open_on == IntervalConf.Upper:
            m.set("open_on", "upper")
        elif self._open_on == IntervalConf.Both:
            m.set("open_on", "both")
        #
        lower = ET.SubElement(m, "value")

        def add_txt(el, val):
            """"""
            el.set("type", type(val).__name__)
            if val == (-math.inf):
                el.text = "-inf"
            elif val == (math.inf):
                el.text = "inf"
            else:
                el.text = str(val)

        add_txt(lower, self.lower)
        upper = ET.SubElement(m, "value")
        add_txt(upper, self.upper)
        ET.indent(m)
        return ET.tostring(m, encoding="unicode")
