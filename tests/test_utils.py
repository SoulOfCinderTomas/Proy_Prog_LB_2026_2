import pytest

from teoria_conjuntos_toolkit.exceptions import (
    ConjuntoInvalidoError,
    ElementoNoHashableError,
    NaturalInvalidoError,
)
from teoria_conjuntos_toolkit.utils import (
    a_frozenset,
    es_hashable,
    validar_natural,
)


def test_es_hashable():
    assert es_hashable(3) and es_hashable((1, 2)) and es_hashable(frozenset())
    assert not es_hashable([1]) and not es_hashable({1})


def test_a_frozenset_quita_repetidos():
    assert a_frozenset([1, 1, 2]) == frozenset({1, 2})


def test_a_frozenset_acepta_generadores_y_rangos():
    assert a_frozenset(x * 2 for x in range(3)) == frozenset({0, 2, 4})
    assert a_frozenset(range(3)) == frozenset({0, 1, 2})


@pytest.mark.parametrize("malo", ["abc", b"abc"])
def test_a_frozenset_rechaza_cadenas(malo):
    with pytest.raises(ConjuntoInvalidoError):
        a_frozenset(malo)


@pytest.mark.parametrize("malo", [5, None, 3.14])
def test_a_frozenset_rechaza_no_iterables(malo):
    with pytest.raises(ConjuntoInvalidoError):
        a_frozenset(malo)


def test_a_frozenset_rechaza_no_hashables():
    with pytest.raises(ElementoNoHashableError):
        a_frozenset([[1], [2]])


@pytest.mark.parametrize("bueno", [0, 1, 100])
def test_validar_natural_acepta(bueno):
    assert validar_natural(bueno) == bueno


@pytest.mark.parametrize("malo", [-1, 2.0, "3", None, True])
def test_validar_natural_rechaza(malo):
    with pytest.raises(NaturalInvalidoError):
        validar_natural(malo)
