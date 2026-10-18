import pytest

from teoria_conjuntos_toolkit import (
    Conjunto,
    FamiliaDeConjuntos,
    FamiliaInvalidaError,
    FamiliaVaciaError,
    NaturalInvalidoError,
    es_natural_von_neumann,
    naturales_von_neumann,
    numero_von_neumann,
    sucesor,
)


def test_convierte_iterables_a_conjuntos():
    F = FamiliaDeConjuntos([[1, 2], {3}, Conjunto([4])])
    assert F[0] == Conjunto([1, 2]) and len(F) == 3
    assert all(isinstance(c, Conjunto) for c in F)


def test_familia_indexada_conserva_repetidos():
    assert len(FamiliaDeConjuntos([[1], [1]])) == 2


@pytest.mark.parametrize("malo", ["abc", 5, None])
def test_rechaza_familias_invalidas(malo):
    with pytest.raises(FamiliaInvalidaError):
        FamiliaDeConjuntos(malo)


def test_rechaza_miembro_invalido():
    with pytest.raises(FamiliaInvalidaError):
        FamiliaDeConjuntos([[1], 7])
    with pytest.raises(FamiliaInvalidaError):
        FamiliaDeConjuntos([[1], [[2]]])


def test_inmutable_igualdad_y_hash():
    F = FamiliaDeConjuntos([[1], [2]])
    with pytest.raises(AttributeError):
        F.x = 1
    assert F == FamiliaDeConjuntos([[1], [2]])
    assert F != FamiliaDeConjuntos([[2], [1]])
    assert hash(F) == hash(FamiliaDeConjuntos([[1], [2]]))


def test_familia_desde_conjunto_potencia():
    P = Conjunto([1, 2]).conjunto_potencia()
    F = FamiliaDeConjuntos(P)
    assert len(F) == 4 and F.union() == Conjunto([1, 2])


def test_union_e_interseccion():
    F = FamiliaDeConjuntos([[1, 2, 3], [2, 3, 4], [3, 5]])
    assert F.union() == Conjunto([1, 2, 3, 4, 5])
    assert F.interseccion() == Conjunto([3])


def test_familia_vacia():
    F = FamiliaDeConjuntos()
    assert F.union() == Conjunto()
    with pytest.raises(FamiliaVaciaError):
        F.interseccion()
    assert F.interseccion(universo=[1, 2]) == Conjunto([1, 2])


def test_disjunta_dos_a_dos():
    assert FamiliaDeConjuntos([[1], [2], [3]]).es_disjunta_dos_a_dos()
    assert not FamiliaDeConjuntos([[1, 2], [3], [2]]).es_disjunta_dos_a_dos()
    assert FamiliaDeConjuntos().es_disjunta_dos_a_dos()


def test_disjuncion_con_repetidos_no_vacios_falla():
    assert not FamiliaDeConjuntos([[1], [1]]).es_disjunta_dos_a_dos()


def test_recubre():
    F = FamiliaDeConjuntos([[1, 2], [3]])
    assert F.recubre([1, 2, 3]) and F.recubre([1])
    assert not F.recubre([1, 4])


def test_particion_valida():
    assert FamiliaDeConjuntos([[1, 2], [3], [4, 5]]).es_particion_de(range(1, 6))


def test_particion_invalida_por_traslape():
    assert not FamiliaDeConjuntos([[1, 2], [2, 3]]).es_particion_de([1, 2, 3])


def test_particion_invalida_por_no_cubrir():
    assert not FamiliaDeConjuntos([[1], [2]]).es_particion_de([1, 2, 3])


def test_particion_invalida_por_sobrar_elementos():
    assert not FamiliaDeConjuntos([[1], [2], [3]]).es_particion_de([1, 2])


def test_particion_invalida_por_miembro_vacio():
    assert not FamiliaDeConjuntos([[1], [], [2]]).es_particion_de([1, 2])


def test_familia_vacia_solo_particiona_el_vacio():
    assert FamiliaDeConjuntos().es_particion_de([])
    assert not FamiliaDeConjuntos().es_particion_de([1])


def test_primeros_naturales():
    cero = Conjunto()
    uno = Conjunto([cero])
    dos = Conjunto([cero, uno])
    assert numero_von_neumann(0) == cero
    assert numero_von_neumann(1) == uno
    assert numero_von_neumann(2) == dos
    assert str(numero_von_neumann(3)) == "{∅, {∅}, {∅, {∅}}}"


@pytest.mark.parametrize("n", range(0, 8))
def test_cardinal_de_n_es_n_y_contiene_a_los_anteriores(n):
    num = numero_von_neumann(n)
    assert num.cardinal == n
    assert all(numero_von_neumann(k) in num for k in range(n))


def test_sucesor_agrega_el_propio_conjunto():
    x = Conjunto([1, 2])
    s = sucesor(x)
    assert x in s and x <= s and s.cardinal == 3


def test_naturales_es_cadena_por_inclusion():
    F = naturales_von_neumann(6)
    assert len(F) == 7
    assert all(F[i] < F[i + 1] for i in range(6))
    assert all(F[i] in F[i + 1] for i in range(6))


def test_naturales_von_neumann_cero():
    assert list(naturales_von_neumann(0)) == [Conjunto()]


@pytest.mark.parametrize("malo", [-1, 2.5, "3", None, True])
def test_numero_von_neumann_rechaza_no_naturales(malo):
    with pytest.raises(NaturalInvalidoError):
        numero_von_neumann(malo)
    with pytest.raises(NaturalInvalidoError):
        naturales_von_neumann(malo)


def test_es_natural_von_neumann():
    assert all(es_natural_von_neumann(numero_von_neumann(k)) for k in range(7))
    assert not es_natural_von_neumann([1, 2])
    assert not es_natural_von_neumann([Conjunto(), Conjunto([1])])
