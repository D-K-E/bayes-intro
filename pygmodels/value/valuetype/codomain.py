"""!
\file codomain.py Represents a codomain of a function. Since we are dealing
with probabilities and related concepts the codomain should be a measurable
value
"""

from typing import Callable, Optional
from xml.etree import ElementTree as ET

from pygmodels.utils import is_optional_type, is_type
from pygmodels.value.valuetype.abstractvalue import (
    FiniteTypedSet,
    OrderedFiniteTypedSequence,
    TypedMutableSet,
    TypedOrderedSequence,
)
from pygmodels.value.valuetype.abstractvalue import Interval as AbsInterval
from pygmodels.value.valuetype.value import NumericValue, SetValue, Value


class CodomainValue(SetValue):
    """"""

    def __init__(
        self,
        v: Value,
        set_id: str,
        mapping_name: str,
        domain_name: Optional[str] = None,
    ):
        super().__init__(v=v, set_id=set_id)

        is_type(mapping_name, "mapping_name", str, True)
        self._fn = mapping_name
        is_optional_type(domain_name, "domain_name", str, True)
        self._fn_domain = domain_name

    @property
    def mapped_by(self) -> str:
        "name of the function mapping to the codomain"
        if self._fn is None:
            raise ValueError("Codomain is not associated with a function")
        return self._fn

    @property
    def mapped_from(self) -> Optional[str]:
        "the domain name of the function mapping to the codomain"
        return self._fn_domain

    def __str__(self):
        """"""
        m = ET.Element("CodomainValue")
        m.text = str(self.value)
        m.set("set", self.belongs_to)
        m.set("mapped_by", self.mapped_by)
        if self.mapped_from:
            m.set("mapped_from", self.mapped_from)
        ET.indent(m)
        return ET.tostring(m, encoding="unicode")


class Interval(AbsInterval):
    """"""

    def __init__(self, name: str, lower: CodomainValue, upper: CodomainValue):
        """"""
        super().__init__(name=name, lower=lower, upper=upper, open_on=None)

    def __call__(
        self, sampler: Callable[[NumericValue, NumericValue], NumericValue]
    ) -> CodomainValue:
        """
        Sampler function for the interval
        """
        codom = CodomainValue(
            v=sampler(self.lower, self.upper),
            mapping_name=str(sampler),
            set_id=self._name,
        )
        return codom


class Codomain(TypedMutableSet):
    """"""

    def __init__(self, name: str, iterable):
        """"""
        super().__init__(iterable, CodomainValue, name=name)


class Range(Codomain):
    """"""

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)


class RangeSubset(Range):
    """"""

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)


class OrderedCodomain(TypedOrderedSequence):
    """"""

    def __init__(self, name: str, iterable):
        """"""
        super().__init__(iterable, CodomainValue, name=name)


class FiniteCodomain(FiniteTypedSet):
    """"""

    def __init__(self, name: str, iterable):
        super().__init__(iterable, CodomainValue, name=name)


class OrderedFiniteCodomain(OrderedFiniteTypedSequence):
    """"""

    def __init__(self, name: str, iterable):
        super().__init__(iterable, CodomainValue, name=name)
