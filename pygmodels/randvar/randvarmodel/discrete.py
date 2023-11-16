"""
\brief discrete random number as defined in Biagini, Campanino, 2016, p. 27
"""

from pygmodels.randvar.randvartype.baserandvar2 import BaseRandomNumber
from pygmodels.randvar.randvartype.abstractrandvar import PossibleOutcomes
from pygmodels.value.valuetype.codomain import CodomainValue
from pygmodels.value.valuetype.value import NumericValue
from pygmodels.utils import mk_id, is_type, is_optional_type
from typing import Optional, Callable, List
from types import FunctionType


class DiscreteRandomNumber(BaseRandomNumber):
    """"""

    def __init__(self, *args, outcomes: Optional[PossibleOutcomes] = None, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        is_optional_type(outcomes, "outcomes", PossibleOutcomes, True)
        self._outcomes = outcomes

    @property
    def upper_bound(self) -> float:
        """"""
        if self._evidence is not None:
            return self._evidence.value().value
        f = max([out.value for out in self.outcomes])
        return f

    @property
    def lower_bound(self) -> float:
        """"""
        if self._evidence is not None:
            return self._evidence.value().value
        f = min([out.value for out in self.outcomes])
        return f

    @property
    def outcomes(self) -> PossibleOutcomes:
        """
        Biagini, Campanino, 2016, p. 5
        """
        if self._outcomes is None:
            raise ValueError("outcomes is none")
        if self._evidence is not None:
            return PossibleOutcomes(set([self._evidence.value]))
        return self._outcomes

    def __and__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def min_f(e, f):
            return min(e, f)

        return self.__myop__(other=other, func=min_f, func_name="&")

    def __or__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def max_f(e, f):
            return max(e, f)

        return self.__myop__(other=other, func=max_f, func_name="|")

    def __invert__(self) -> BaseRandomNumber:
        """
        Biagini, Campanino, 2016, p. 4
        """
        name = "~" + self.name

        def invert():
            """"""
            for out in self.outcomes:
                comp = 1 - out.fetch()
                cval = CodomainValue(
                    v=comp,
                    set_id=self.id(),
                    mapping_name="~",
                    domain_name=self.name,
                )
                yield cval

        new_outcomes = PossibleOutcomes(iterable=invert())
        return DiscreteRandomNumber(
            randvar_id=mk_id(), randvar_name=name, outcomes=new_outcomes
        )

    def __myop__(
        self,
        other,
        func: Callable[[NumericValue, NumericValue], NumericValue] = lambda e, f: e + f,
        func_name: str = "+",
    ):
        "Biagini, Campanino, 2016, p. 4"
        is_type(other, "other", DiscreteRandomNumber, True)
        is_type(func, "func", FunctionType, True)
        is_type(func_name, "func_name", str, True)
        #
        opname = func_name
        name = "(" + opname + " " + " ".join(["#" + other.name, "#" + self.name])
        name += ")"
        set_name = "outcome"

        def get_outcomes():
            """"""
            for f_val in other.outcomes:
                f = f_val.fetch()
                for e_val in self.outcomes:
                    e: NumericValue = e_val.fetch()
                    ef_max = func(e, f)
                    rval = CodomainValue(
                        v=ef_max,
                        set_id=set_name,
                        mapping_name=func_name,
                        domain_name=name,
                    )
                    yield rval

        oname = "(" + set_name + " " + name + ")"
        op_result = DiscreteRandomNumber(
            randvar_id=mk_id(),
            randvar_name=name,
            outcomes=PossibleOutcomes(iterable=get_outcomes(), name=oname),
        )
        return op_result

    def __add__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def add_f(e, f):
            """"""
            ef = e + f
            return ef

        return self.__myop__(other=other, func=add_f, func_name="+")

    def __sub__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def sub_f(e, f):
            """"""
            ef = e - f
            return ef

        return self.__myop__(other=other, func=sub_f, func_name="-")

    def __mul__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def mul_f(e, f):
            """"""
            ef = e * f
            return ef

        return self.__myop__(other=other, func=mul_f, func_name="*")

    def __truediv__(self, other) -> BaseRandomNumber:
        "Biagini, Campanino, 2016, p. 4"

        def div_f(e, f):
            """"""
            ef = e / f
            return ef

        return self.__myop__(other=other, func=div_f, func_name="/")
