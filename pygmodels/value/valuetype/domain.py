"""!
\file domain.py Represents the domain of a function. It can be anything.
"""


from pygmodels.value.valuetype.abstractvalue import (
    FiniteTypedSet,
    OrderedFiniteTypedSequence,
    TypedMutableSet,
    TypedOrderedSequence,
)
from pygmodels.value.valuetype.value import SetValue


class DomainValue(SetValue):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Domain(TypedMutableSet):
    """"""

    def __init__(self, name: str, iterable):
        super().__init__(iterable, DomainValue, name=name)


class DomainSample(Domain):
    """"""

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)


class Sample(DomainSample):
    """"""

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)


class OrderedDomain(TypedOrderedSequence):
    """"""

    def __init__(self, name: str, iterable):
        super().__init__(iterable, DomainValue, name=name)


class FiniteDomain(FiniteTypedSet):
    """"""

    def __init__(self, name: str, iterable):
        """"""
        super().__init__(iterable, DomainValue, name=name)


class OrderedFiniteDomain(OrderedFiniteTypedSequence):
    """"""

    def __init__(self, name: str, iterable):
        """"""
        super().__init__(iterable, DomainValue, name=name)
