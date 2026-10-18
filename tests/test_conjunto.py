import random

import pytest

from teoria_conjuntos_toolkit import (
    Conjunto,
    ConjuntoDemasiadoGrandeError,
    ConjuntoInvalidoError,
    ElementoNoHashableError,
    FamiliaVaciaError,
    OperacionInvalidaError,
    UniversoInvalidoError,
    como_conjunto,
    interseccion_generalizada,
    producto_cartesiano,
    union_generalizada,
)


def test_sin_repetidos_y_cardinal():
    assert Conjunto([1, 1, 2]).cardinal == 2
    assert len(Conjunto()) == 0


def test_vacio():
    assert Conjunto().es_vacio()
    assert not Conjunto([0]).es_vacio()


def test_rechaza_datos_invalidos():
    with pytest.raises(ConjuntoInvalidoError):
        Conjunto("abc")
    with pytest.raises(ConjuntoInvalidoError):
        Conjunto(7)
    with pytest.raises(ElementoNoHashableError):
        Conjunto([[1, 2]])


def test_excepcion_es_tambien_typeerror_y_valueerror():
    with pytest.raises(TypeError):
        Conjunto([[1]])
    with pytest.raises(ValueError):
        Conjunto("abc")


def test_inmutable():
    c = Conjunto([1])
    with pytest.raises(AttributeError):
        c.otro = 3
    with pytest.raises(AttributeError):
        c._elementos = frozenset()


def test_pertenencia(a):
    assert 1 in a and 9 not in a
    assert [1] not in a


def test_igualdad_y_hash():
    assert Conjunto([1, 2]) == Conjunto([2, 1, 1])
    assert Conjunto([1, 2]) != Conjunto([1])
    assert Conjunto([1]) != {1}
    assert len({Conjunto([1, 2]), Conjunto([2, 1])}) == 1


def test_iteracion_determinista():
    assert list(Conjunto([3, 1, 2])) == [1, 2, 3]
    assert list(Conjunto([2, "a", 1])) == [1, 2, "a"]


def test_str_y_repr():
    assert str(Conjunto()) == "∅"
    assert str(Conjunto([2, 1])) == "{1, 2}"
    assert repr(Conjunto([2, 1])) == "Conjunto([1, 2])"
    assert eval(repr(Conjunto([1, 2])), {"Conjunto": Conjunto}) == Conjunto([1, 2])


def test_subconjuntos(a):
    assert Conjunto([1, 2]) <= a
    assert Conjunto([1, 2]) < a
    assert a <= a and not a < a
    assert a >= Conjunto([1]) and a > Conjunto([1])
    assert Conjunto() <= a
    assert a.es_subconjunto([1, 2, 3, 4])
    assert not a.es_subconjunto_propio([1, 2, 3])


def test_disjuntos(a, b):
    assert not a.es_disjunto(b)
    assert a.es_disjunto([8, 9])


def test_operaciones_basicas(a, b):
    assert a | b == Conjunto([1, 2, 3, 4, 5])
    assert a & b == Conjunto([3])
    assert a - b == Conjunto([1, 2])
    assert a ^ b == Conjunto([1, 2, 4, 5])


def test_operaciones_aceptan_iterables_nativos(a):
    assert a | [9] == Conjunto([1, 2, 3, 9])
    assert a & {3, 4} == Conjunto([3])


def test_operacion_con_dato_invalido(a):
    with pytest.raises(ConjuntoInvalidoError):
        a | 5


def test_union_e_interseccion_n_aria(a, b):
    assert a.union(b, [9]) == Conjunto([1, 2, 3, 4, 5, 9])
    assert a.interseccion(b, [3, 7]) == Conjunto([3])


def test_complemento(a, universo):
    assert a.complemento(universo) == Conjunto([4, 5, 6, 7])
    assert Conjunto().complemento(universo) == universo
    assert universo.complemento(universo) == Conjunto()


def test_complemento_fuera_del_universo(a):
    with pytest.raises(UniversoInvalidoError):
        a.complemento([1, 2])


def test_union_generalizada():
    assert union_generalizada([[1], [2], [2, 3]]) == Conjunto([1, 2, 3])
    assert union_generalizada([]) == Conjunto()


def test_interseccion_generalizada():
    assert interseccion_generalizada([[1, 2, 3], [2, 3], [3]]) == Conjunto([3])
    assert interseccion_generalizada([[1, 2]]) == Conjunto([1, 2])


def test_interseccion_de_nada_necesita_universo():
    with pytest.raises(FamiliaVaciaError):
        interseccion_generalizada([])
    assert interseccion_generalizada([], universo=[1, 2]) == Conjunto([1, 2])


def test_como_conjunto_no_copia_si_ya_es_conjunto(a):
    assert como_conjunto(a) is a


@pytest.mark.parametrize("n", range(0, 6))
def test_tamano_conjunto_potencia(n):
    assert Conjunto(range(n)).conjunto_potencia().cardinal == 2**n


def test_conjunto_potencia_contenido():
    p = Conjunto([1, 2]).conjunto_potencia()
    assert Conjunto() in p and Conjunto([1, 2]) in p
    assert all(s <= Conjunto([1, 2]) for s in p)


def test_conjunto_potencia_demasiado_grande():
    with pytest.raises(ConjuntoDemasiadoGrandeError):
        Conjunto(range(25)).conjunto_potencia()


def test_producto_cartesiano(a):
    p = a * Conjunto(["x", "y"])
    assert p.cardinal == 6 and (1, "x") in p and ("x", 1) not in p


def test_producto_cartesiano_n_ario():
    p = producto_cartesiano([1, 2], [3], [4, 5])
    assert p.cardinal == 4 and (2, 3, 5) in p


def test_producto_con_vacio_es_vacio(a):
    assert (a * Conjunto()).es_vacio()


def test_producto_sin_argumentos():
    with pytest.raises(OperacionInvalidaError):
        producto_cartesiano()


def _aleatorios(semilla, n=60):
    rng = random.Random(semilla)
    return [
        (
            set(rng.sample(range(15), rng.randint(0, 8))),
            set(rng.sample(range(15), rng.randint(0, 8))),
        )
        for _ in range(n)
    ]


def test_coincide_con_set_nativo():
    for x, y in _aleatorios(1):
        A, B = Conjunto(x), Conjunto(y)
        assert (A | B).elementos == x | y
        assert (A & B).elementos == x & y
        assert (A - B).elementos == x - y
        assert (A ^ B).elementos == x ^ y
        assert (A <= B) == (x <= y)


def test_leyes_de_de_morgan():
    U = Conjunto(range(15))
    for x, y in _aleatorios(2):
        A, B = Conjunto(x), Conjunto(y)
        assert (A | B).complemento(U) == A.complemento(U) & B.complemento(U)
        assert (A & B).complemento(U) == A.complemento(U) | B.complemento(U)


def test_distributividad_y_diferencia_simetrica():
    for x, y in _aleatorios(3):
        A, B, C = Conjunto(x), Conjunto(y), Conjunto(x ^ y)
        assert A & (B | C) == (A & B) | (A & C)
        assert A ^ B == (A - B) | (B - A)
