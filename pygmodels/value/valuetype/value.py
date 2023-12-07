"""!
\file value.py Represents the value of functions in the case of PGMs
"""

from typing import Callable, FrozenSet, List, Optional, Set, Tuple, Union

from pygmodels.value.valuetype.abstractvalue import AbstractSetValue
from pygmodels.value.valuetype.abstractvalue import AbstractValue
from pygmodels.value.valuetype.abstractvalue import Countable
from pygmodels.value.valuetype.abstractvalue import TypedSequence
from pygmodels.value.valuetype.abstractvalue import Interval
from pygmodels.value.valuetype.abstractvalue import NamedContainer
from pygmodels.value.valuetype.abstractvalue import IntervalConf
from pygmodels.utils import is_type, is_optional_type
from pygmodels.utils import is_all_type
from types import FunctionType
from xml.etree import ElementTree as ET
import math
import pdb


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


class IntervalPair(NamedContainer):
    "A special object to make interval set operations compatible with set ops"

    def __init__(self, lower: Interval, upper: Interval):
        lname = lower._name
        uname = upper._name
        name = "[" + lname + ", " + uname + "]"
        super().__init__(name=name)
        is_type(lower, "lower", Interval, True)
        self._lower = min(lower, upper)

        is_type(upper, "upper", Interval, True)
        self._upper = max(lower, upper)

    def __or__(self, other):
        """
        \brief basic or operation for IntervalPair

        There are several cases:
        - argument is interval, we | with lower and upper:
            - We obtain two intervals from the operation:
                - we obtain an overlapping intervals: merge them and output an
                  interval
                - we obtain non overlapping intervals: output IntervalPair
            - We obtain IntervalPair from one, interval from another:
                - keep the resulting interval, ignore the resulting IntervalPair and output IntervalPair.
            - We obtain 2 IntervalPairs from the operation:
                - we output IntervalPair effectively creating a binary tree.
        - argument is interval pair, we | with lower and upper:
            - We propagate | op on lower and upper parts of the pair, and
              combine the results with or again
        """

        def output(lower, upper):
            """"""
            if all(isinstance(a, Interval) for a in [lower, upper]):
                is_overlapping = lower & upper
                if is_overlapping:
                    # overlapping intervals
                    return lower | upper
                else:
                    # not overlapping intervals
                    return IntervalPair(lower=lower, upper=upper)
            elif any(isinstance(a, Interval) for a in [lower, upper]):
                is_low, intvl = (
                    (True, lower) if isinstance(lower, Interval) else (False, upper)
                )
                return IntervalPair(
                    lower=intvl if is_low else self._lower,
                    upper=intvl if not is_low else self._upper,
                )
            elif all(isinstance(a, IntervalPair) for a in [lower, upper]):
                return IntervalPair(lower=lower, upper=upper)

        if isinstance(other, Interval):
            lower = self._lower | other
            upper = self._upper | other
            return output(lower, upper)
        #
        is_type(other, "other", IntervalPair, True)
        lower_1 = self._lower | other._lower
        lower_2 = self._lower | other._upper
        lower = lower_1 | lower_2
        upper_1 = self._upper | other._lower
        upper_2 = self._upper | other._upper
        upper = upper_1 | upper_2
        return output(lower, upper)

    def __and__(self, other) -> FrozenSet[Interval]:
        """
        \brief basic and operation for IntervalPair

        It outputs either an interval, interval pair or an empty set

        There are several cases:
        - argument is interval, we & with lower and upper:
            - We obtain two intervals from the operation:
                - we obtain an overlapping intervals: merge them and output an
                  interval
                - we obtain non overlapping intervals: output IntervalPair
            - We obtain IntervalPair from one, interval from another:
                - keep the resulting interval, ignore the resulting IntervalPair and output IntervalPair.
            - We obtain 2 IntervalPairs from the operation:
                - we output IntervalPair effectively creating a binary tree.
        - argument is interval pair, we | with lower and upper:
            - We propagate | op on lower and upper parts of the pair, and
              combine the results with or again
        """
        if not other:
            return frozenset()

        if isinstance(other, Interval):
            lower = self._lower & other
            upper = self._upper & other
            if all(isinstance(a, Interval) for a in [lower, upper]):
                is_overlapping = lower & upper
                if is_overlapping:
                    # overlapping intervals
                    return other
                else:
                    # not overlapping intervals
                    return IntervalPair(lower=lower, upper=upper)
            if upper and not lower:
                return upper
            if lower and not upper:
                return lower
            if not lower and not upper:
                return frozenset()
        #
        is_type(other, "other", IntervalPair, True)
        lower_1 = self._lower & other._lower
        lower_2 = self._lower & other._upper
        lower = lower_1 | lower_2
        upper_1 = self._upper & other._lower
        upper_2 = self._upper & other._upper
        upper = upper_1 | upper_2
        return upper | lower

    def __invert__(self) -> Interval:
        l_i = ~self._lower
        u_i = ~self._upper
        return l_i | u_i

    def __str__(self) -> str:
        """"""
        m = ET.Element(type(self).__name__)
        if self._name is not None:
            m.set("name", self._name)
        #
        lstr = ET.fromstring(str(self._lower))
        ustr = ET.fromstring(str(self._upper))
        m.append(lstr)
        m.append(ustr)
        ET.indent(m)
        return ET.tostring(m, encoding="unicode")


class NumericInterval(Interval):
    """
    An interval defined on real line
    """

    def __init__(
        self,
        lower: NumericValue,
        upper: NumericValue,
        open_on: Optional[IntervalConf] = None,
        name: Optional[str] = None,
    ):
        up_fn = None
        low_fn = None
        s = ""
        if open_on is None:
            s += "[" + str(lower) + ", " + str(upper) + "]"
            up_fn = lambda x: x <= self.upper
            low_fn = lambda x: x >= self.lower
        elif open_on == IntervalConf.Lower:
            s += "(" + str(lower) + ", " + str(upper) + "]"
            up_fn = lambda x: x <= self.upper
            low_fn = lambda x: x > self.lower

        elif open_on == IntervalConf.Upper:
            s += "[" + str(lower) + ", " + str(upper) + ")"
            up_fn = lambda x: x < self.upper
            low_fn = lambda x: x >= self.lower
        elif open_on == IntervalConf.Both:
            s += "(" + str(lower) + ", " + str(upper) + ")"
            up_fn = lambda x: x < self.upper
            low_fn = lambda x: x > self.lower
        if name:
            s = name
        is_type(lower, "lower", NumericValue, True)
        is_type(upper, "upper", NumericValue, True)
        lower = min(lower, upper)
        upper = max(lower, upper)
        super().__init__(name=s, lower=lower, upper=upper, open_on=open_on)
        self._compare_lower = low_fn
        self._compare_upper = up_fn

    def __contains__(self, other: NumericValue):
        """"""
        return self._compare_lower(other) and self._compare_upper(other)

    def length(self):
        """
        Lebesque measure as per: Epps, 2014, p. 19
        Originally defined for (a, b] type intervals but the derivation in
        p. 19-20 show that results are equivalent for (a, b) as well.
        """
        return self.upper - self.lower

    def __decide_conf__(self, other, l_minmax_fn, u_minmax_fn):
        """"""
        is_l_closed = l_minmax_fn()
        is_u_closed = u_minmax_fn()
        if is_u_closed and is_l_closed:
            conf = None
        elif is_u_closed and not is_l_closed:
            conf = IntervalConf.Lower
        elif not is_u_closed and is_l_closed:
            conf = IntervalConf.Upper
        elif not is_u_closed and not is_l_closed:
            conf = IntervalConf.Both
        return conf

    def __or__(
        self, other: Union[IntervalPair, Interval, set, frozenset]
    ) -> Union[IntervalPair, Interval]:
        """
        From Jaulin, 2001, p. 18
        """
        if isinstance(other, NumericInterval):
            is_small = self < other
            os_small = other < self
            if is_small or os_small:
                if is_small:
                    return IntervalPair(lower=self, upper=other)
                if os_small:
                    return IntervalPair(lower=other, upper=self)
            min_l = min(other.lower, self.lower)
            max_l = max(other.upper, self.upper)
            is_l_closed_fn = lambda: (min_l in self) or (min_l in other)
            is_u_closed_fn = lambda: (max_l in self) or (max_l in other)
            conf = self.__decide_conf__(
                other=other, l_minmax_fn=is_l_closed_fn, u_minmax_fn=is_u_closed_fn
            )
            return NumericInterval(lower=min_l, upper=max_l, name=None, open_on=conf)
        elif isinstance(other, IntervalPair):
            return other | self
        elif isinstance(other, (set, frozenset)):
            if other:
                raise ValueError("only empty set is accepted as argument")
            return self
        else:
            raise TypeError(
                "other must have type NumericInterval or IntervalPair"
                + f" or empty set but it has {type(other).__name__}"
            )

    def __ror__(self, other):
        return self | other

    def __and__(
        self, other: Union[IntervalPair, Interval, set, frozenset]
    ) -> Union[FrozenSet[Interval], Interval]:
        """
        From Jaulin, 2001, p. 18
        """
        if isinstance(other, NumericInterval):
            if (self < other) or (other < self):
                return frozenset()
            lower = max(self.lower, other.lower)
            upper = min(self.upper, other.upper)
            is_l_closed_fn = (
                lambda: lower in self if lower == self.lower else lower in other
            )
            is_u_closed_fn = (
                lambda: upper in self if upper == self.upper else upper in other
            )
            conf = self.__decide_conf__(
                other=other, l_minmax_fn=is_l_closed_fn, u_minmax_fn=is_u_closed_fn
            )
            if lower <= upper:
                return NumericInterval(
                    lower=lower, upper=upper, name=None, open_on=conf
                )
            else:
                raise ValueError(f"Unexpected interval error {self} and {other}")

        elif isinstance(other, IntervalPair):
            return other & self

        elif isinstance(other, (set, frozenset)):
            if other:
                raise ValueError("only empty set is accepted as argument")
            return frozenset()
        else:
            raise TypeError(
                "other must have type NumericInterval or IntervalPair"
                + f" or empty set but it has {type(other).__name__}"
            )

    def __rand__(self, other):
        return self & other

    def __sub__(
        self, other: Union[IntervalPair, Interval, set, frozenset]
    ) -> Union[FrozenSet[Interval], Interval]:
        """
        Set difference between intervals from
        Jaulin, 2001, p. 18 (2.40)
        """
        if isinstance(other, (NumericInterval, IntervalPair)):
            other_c = ~other
            return self & other_c
        elif isinstance(other, (set, frozenset)):
            if not other:
                return self
            oset = set(other)
            rset = ~oset.pop()
            result = self & rset
            for o in oset:
                o_c = ~o
                inters = self & o_c
                result = result | inters
            return result
        else:
            raise TypeError(
                "other must have type NumericInterval or IntervalPair"
                + f" or empty set but it has {type(other).__name__}"
            )

    def __invert__(self) -> IntervalPair:
        """
        From Jaulin, 2001, p. 20
        """
        left_low = NumericValue(-math.inf)
        right_up = NumericValue(math.inf)

        def ret_set(i, j):
            """"""
            return IntervalPair(
                lower=NumericInterval(
                    lower=left_low,
                    upper=self.lower,
                    name=None,
                    open_on=i,
                ),
                upper=NumericInterval(
                    lower=self.upper, upper=right_up, name=None, open_on=j
                ),
            )

        if self._open_on == IntervalConf.Lower:
            return ret_set(i=IntervalConf.Lower, j=IntervalConf.Both)
        elif self._open_on == IntervalConf.Upper:
            return ret_set(i=IntervalConf.Both, j=IntervalConf.Upper)
        else:
            return ret_set(i=IntervalConf.Both, j=IntervalConf.Both)

    def __lt__(
        self, other: Union[IntervalPair, Interval, Set[Interval], FrozenSet[Interval]]
    ) -> bool:
        """
        From Dawood, 2011, p. 9
        """
        if isinstance(other, NumericInterval):
            s_up = self.upper
            o_low = other.lower
            if o_low == s_up:
                if self.is_upper_bounded() and other.is_lower_bounded():
                    return False
                return True
            else:
                return s_up < o_low
        elif isinstance(other, (set, frozenset)):
            is_all_type(other, "other", NumericInterval, True)
            return all(self < o for o in other)
        elif isinstance(other, IntervalPair):
            return (self < other._lower) and (self < other._upper)
        else:
            raise TypeError(
                f"can't compare 'other' of type {type(other).__name__}"
                + " it has to be either NumericInterval or "
                + "FrozenSet[NumericInterval]"
            )

    def __le__(
        self, other: Union[IntervalPair, Interval, Set[Interval], FrozenSet[Interval]]
    ) -> bool:
        """
        Moore et al. 2009, p. 10
        """
        if isinstance(other, NumericInterval):
            s_l = self.lower
            s_u = self.upper
            o_l = other.lower
            o_u = other.upper
            if o_l == s_l:
                if self.is_lower_bounded() and (not other.is_lower_bounded()):
                    is_low_inc = False
                else:
                    is_low_inc = True
            else:
                is_low_inc = o_l < s_l
            if o_u == s_u:
                if not other.is_upper_bounded() and self.is_upper_bounded():
                    is_up_inc = False
                else:
                    is_up_inc = True
            else:
                is_up_inc = s_u < o_u
            is_le = is_low_inc and is_up_inc
            return is_le
        elif isinstance(other, (set, frozenset)):
            is_all_type(other, "other", NumericInterval, True)
            return all(self <= o for o in other)
        elif isinstance(other, IntervalPair):
            return (self <= other._lower) and (self <= other._upper)
        else:
            raise TypeError(
                f"can't compare 'other' of type {type(other).__name__}"
                + " it has to be either NumericInterval or "
                + "FrozenSet[NumericInterval] or IntervalPair"
            )

    def is_superset_of(self, other: Union[FrozenSet[Interval], Interval]) -> bool:
        """"""
        if isinstance(other, NumericInterval):
            return other <= self
        elif isinstance(other, (set, frozenset)):
            is_all_type(other, "other", NumericInterval, True)
            return all(o <= self for o in other)
        else:
            raise TypeError(
                f"can't compare 'other' of type {type(other).__name__}"
                + " it has to be either NumericInterval or "
                + "FrozenSet[NumericInterval]"
            )

    def __neq__(self, other: Interval) -> bool:
        """"""
        if isinstance(other, NumericInterval):
            return (self < other) or (other < self)
        return False

    def __eq__(self, other: Interval) -> bool:
        """
        Equality for intervals
        """
        if isinstance(other, NumericInterval):
            if other._open_on != self._open_on:
                return False
            return (other.lower == self.lower) and (other.upper == self.upper)
        return False

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


class R(NumericInterval):
    """"""

    def __init__(self):
        super().__init__(
            lower=NumericValue(-math.inf),
            upper=NumericValue(math.inf),
            open_on=IntervalConf.Both,
            name="R",
        )
