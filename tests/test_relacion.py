import random
from itertools import product

import pytest

from teoria_conjuntos_toolkit import (
    ComposicionInvalidaError,
    Conjunto,
    ConjuntoInvalidoError,
    FueraDeDominioError,
    OperacionInvalidaError,
    Relacion,
    RelacionInvalidaError,
    RelacionNoHomogeneaError,
    warshall,
)


@pytest.fixture
def menor_igual():
    """Crea la relación ≤ sobre {1, 2, 3, 4}.

    Entrada: ninguna.
    Salida: Relacion, orden parcial (y total) sobre los naturales del 1 al 4.
    """
    return Relacion.desde_predicado(range(1, 5), lambda a, b: a <= b)


@pytest.fixture
def congruencia_mod_3():
    """Crea la relación de congruencia módulo 3 sobre {0, ..., 5}.

    Entrada: ninguna.
    Salida: Relacion, de equivalencia con 3 clases.
    """
    return Relacion.desde_predicado(range(6), lambda a, b: (a - b) % 3 == 0)


def _aleatorias(semilla, cuantas=60, n=5):
    rng = random.Random(semilla)
    universo = list(range(n))
    todos = list(product(universo, repeat=2))
    return [
        Relacion(rng.sample(todos, rng.randint(0, len(todos))), universo)
        for _ in range(cuantas)
    ]


def _cierre_transitivo_ingenuo(pares):
    cierre = set(pares)
    while True:
        nuevos = {(a, d) for a, b in cierre for c, d in cierre if b == c} - cierre
        if not nuevos:
            return cierre
        cierre |= nuevos


def test_construccion_basica():
    R = Relacion([(1, 2), (2, 3)], [1, 2, 3])
    assert R.dominio == Conjunto([1, 2, 3]) and R.codominio == R.dominio
    assert len(R) == 2 and (1, 2) in R and (2, 1) not in R
    assert [1, 2] not in R and 5 not in R


def test_codominio_distinto():
    R = Relacion([(1, "a"), (2, "b")], [1, 2], ["a", "b", "c"])
    assert R.codominio == Conjunto(["a", "b", "c"])
    assert R.imagen() == Conjunto(["a", "b"])


def test_pares_repetidos_se_ignoran():
    assert len(Relacion([(1, 2), (1, 2)], [1, 2])) == 1


@pytest.mark.parametrize(
    "malos", ["ab", 5, [(1, 2, 3)], [(1,)], [5], [[1, 2]], [(1, 2), 3]]
)
def test_rechaza_pares_mal_formados(malos):
    with pytest.raises(RelacionInvalidaError):
        Relacion(malos, [1, 2, 3])


def test_rechaza_pares_fuera_de_dominio_y_codominio():
    with pytest.raises(RelacionInvalidaError):
        Relacion([(1, 9)], [1, 2])
    with pytest.raises(RelacionInvalidaError):
        Relacion([(9, 1)], [1, 2])
    with pytest.raises(RelacionInvalidaError):
        Relacion([(1, "z")], [1, 2], ["a"])


def test_rechaza_dominio_invalido():
    with pytest.raises(ConjuntoInvalidoError):
        Relacion([], "abc")
    with pytest.raises(ConjuntoInvalidoError):
        Relacion([], [1], 7)


def test_inmutable():
    R = Relacion([(1, 2)], [1, 2])
    with pytest.raises(AttributeError):
        R.otro = 1
    with pytest.raises(AttributeError):
        del R._pares


def test_igualdad_y_hash():
    R = Relacion([(1, 2), (2, 1)], [1, 2])
    assert R == Relacion([(2, 1), (1, 2)], [2, 1])
    assert R != Relacion([(1, 2)], [1, 2])
    assert R != Relacion([(1, 2), (2, 1)], [1, 2, 3])
    assert R != {(1, 2), (2, 1)}
    assert len({R, Relacion([(1, 2), (2, 1)], [1, 2])}) == 1


def test_str_y_repr():
    R = Relacion([(2, 3), (1, 2)], [1, 2, 3])
    assert str(R) == "{(1, 2), (2, 3)}"
    assert str(Relacion([], [1])) == "∅"
    reconstruida = eval(repr(R), {"Relacion": Relacion, "Conjunto": Conjunto})
    assert reconstruida == R


def test_iteracion_ordenada():
    assert list(Relacion([(2, 1), (1, 2)], [1, 2])) == [(1, 2), (2, 1)]


def test_desde_predicado_divisibilidad():
    R = Relacion.desde_predicado(range(1, 7), lambda a, b: b % a == 0)
    assert len(R) == 14 and (2, 6) in R and (4, 6) not in R
    assert R.es_relacion_orden() and not R.es_relacion_equivalencia()


def test_desde_predicado_con_codominio():
    R = Relacion.desde_predicado([1, 2], lambda a, b: b == a * 10, [10, 20, 30])
    assert R == Relacion([(1, 10), (2, 20)], [1, 2], [10, 20, 30])


def test_desde_predicado_no_invocable():
    with pytest.raises(RelacionInvalidaError):
        Relacion.desde_predicado([1, 2], "no soy funcion")


def test_matriz():
    R = Relacion([(1, 2), (2, 3)], [1, 2, 3])
    assert R.matriz() == [
        [False, True, False],
        [False, False, True],
        [False, False, False],
    ]


def test_matriz_rectangular():
    R = Relacion([(1, "b")], [1, 2], ["a", "b", "c"])
    assert R.matriz() == [[False, True, False], [False, False, False]]


def test_desde_matriz_ida_y_vuelta():
    for R in _aleatorias(7, cuantas=20):
        assert Relacion.desde_matriz(R.matriz(), R.dominio) == R
    S = Relacion([(1, "b")], [1, 2], ["a", "b", "c"])
    assert Relacion.desde_matriz(S.matriz(), S.dominio, S.codominio) == S


@pytest.mark.parametrize(
    "mala", [[[True, False]], [[True], [False, True]], "xx", 5, [[1, 0], 7]]
)
def test_desde_matriz_dimensiones_invalidas(mala):
    with pytest.raises(RelacionInvalidaError):
        Relacion.desde_matriz(mala, [1, 2])


def test_imagenes_e_imagen():
    R = Relacion([(1, 2), (1, 3), (2, 3)], [1, 2, 3])
    assert R.imagenes(1) == Conjunto([2, 3])
    assert R.imagenes(3) == Conjunto()
    assert R.imagen() == Conjunto([2, 3])


def test_imagenes_fuera_del_dominio():
    R = Relacion([(1, 2)], [1, 2])
    with pytest.raises(FueraDeDominioError):
        R.imagenes(9)
    with pytest.raises(FueraDeDominioError):
        R.imagenes([1])


def test_inversa():
    R = Relacion([(1, "a"), (2, "a")], [1, 2], ["a", "b"])
    I = R.inversa()
    assert I == Relacion([("a", 1), ("a", 2)], ["a", "b"], [1, 2])
    assert I.inversa() == R


def test_orden_menor_igual(menor_igual):
    assert menor_igual.es_reflexiva() and menor_igual.es_antisimetrica()
    assert menor_igual.es_transitiva() and not menor_igual.es_simetrica()
    assert menor_igual.es_relacion_orden()
    assert not menor_igual.es_relacion_equivalencia()


def test_equivalencia_congruencia(congruencia_mod_3):
    assert congruencia_mod_3.es_reflexiva() and congruencia_mod_3.es_simetrica()
    assert congruencia_mod_3.es_transitiva()
    assert not congruencia_mod_3.es_antisimetrica()
    assert congruencia_mod_3.es_relacion_equivalencia()
    assert not congruencia_mod_3.es_relacion_orden()


def test_menor_estricto():
    R = Relacion.desde_predicado(range(1, 4), lambda a, b: a < b)
    assert not R.es_reflexiva() and R.es_antisimetrica() and R.es_transitiva()
    assert not R.es_simetrica()


def test_relacion_no_transitiva():
    R = Relacion([(1, 2), (2, 3)], [1, 2, 3])
    assert not R.es_transitiva()


def test_diagonal_es_simetrica_y_antisimetrica():
    R = Relacion([(1, 1), (2, 2)], [1, 2])
    assert R.es_simetrica() and R.es_antisimetrica() and R.es_reflexiva()
    assert R.es_relacion_orden() and R.es_relacion_equivalencia()


def test_relacion_vacia():
    R = Relacion([], [1, 2])
    assert not R.es_reflexiva()
    assert R.es_simetrica() and R.es_antisimetrica() and R.es_transitiva()
    assert Relacion([], []).es_reflexiva()


@pytest.mark.parametrize(
    "metodo",
    [
        "es_reflexiva",
        "es_simetrica",
        "es_antisimetrica",
        "es_transitiva",
        "es_relacion_orden",
        "es_relacion_equivalencia",
        "cerradura_reflexiva",
        "cerradura_simetrica",
        "cerradura_transitiva",
    ],
)
def test_requieren_relacion_homogenea(metodo):
    R = Relacion([(1, "a")], [1], ["a"])
    with pytest.raises(RelacionNoHomogeneaError):
        getattr(R, metodo)()


@pytest.mark.parametrize("faltante", [1, 2, 3, 4])
def test_reflexiva_detecta_un_solo_elemento_faltante(faltante):
    diagonal = [(a, a) for a in range(1, 5) if a != faltante]
    assert not Relacion(diagonal, range(1, 5)).es_reflexiva()
    assert Relacion(diagonal + [(faltante, faltante)], range(1, 5)).es_reflexiva()


def test_una_sola_violacion_rompe_la_propiedad():
    assert not Relacion([(1, 2), (2, 1), (3, 4)], range(1, 5)).es_simetrica()
    assert not Relacion([(1, 1), (2, 3), (3, 2)], range(1, 4)).es_antisimetrica()
    casi = [(1, 2), (2, 3), (3, 4), (1, 3), (2, 4)]
    assert not Relacion(casi, range(1, 5)).es_transitiva()
    assert Relacion(casi + [(1, 4)], range(1, 5)).es_transitiva()


def test_propiedades_coinciden_con_las_definiciones():
    for R in _aleatorias(11):
        pares = set(R.pares.elementos)
        dominio = list(R.dominio)
        assert R.es_reflexiva() == all((a, a) in pares for a in dominio)
        assert R.es_simetrica() == all((b, a) in pares for a, b in pares)
        assert R.es_antisimetrica() == all(
            a == b for a, b in pares if (b, a) in pares
        )
        assert R.es_transitiva() == all(
            (a, d) in pares for a, b in pares for c, d in pares if b == c
        )


def test_es_funcion():
    assert Relacion([(1, "a"), (2, "a")], [1, 2], ["a"]).es_funcion()
    assert not Relacion([(1, "a")], [1, 2], ["a"]).es_funcion()
    assert not Relacion([(1, "a"), (1, "b")], [1], ["a", "b"]).es_funcion()


def test_composicion():
    R = Relacion([(1, "a"), (2, "b")], [1, 2], ["a", "b"])
    S = Relacion([("a", 10), ("b", 20), ("b", 30)], ["a", "b"], [10, 20, 30])
    C = S.composicion(R)
    assert C == Relacion([(1, 10), (2, 20), (2, 30)], [1, 2], [10, 20, 30])


def test_composicion_con_codominio_contenido():
    R = Relacion([(1, "a")], [1], ["a"])
    S = Relacion([("a", 5), ("b", 6)], ["a", "b"], [5, 6])
    assert S.composicion(R) == Relacion([(1, 5)], [1], [5, 6])


def test_composicion_invalida():
    R = Relacion([(1, "a")], [1], ["a", "z"])
    S = Relacion([("a", 5)], ["a"], [5])
    with pytest.raises(ComposicionInvalidaError):
        S.composicion(R)
    with pytest.raises(ComposicionInvalidaError):
        S.composicion({(1, "a")})


def test_composicion_con_la_inversa_contiene_la_diagonal():
    for R in _aleatorias(13, cuantas=20):
        compuesta = R.inversa().composicion(R)
        for a in R.dominio:
            if len(R.imagenes(a)) > 0:
                assert (a, a) in compuesta


def test_warshall_cadena():
    cadena = [
        [False, True, False, False],
        [False, False, True, False],
        [False, False, False, True],
        [False, False, False, False],
    ]
    cierre = warshall(cadena)
    assert sum(valor for fila in cierre for valor in fila) == 6
    assert cierre[0][3] and not cierre[3][0]


def test_warshall_ciclo():
    cierre = warshall([[False, True], [True, False]])
    assert cierre == [[True, True], [True, True]]


def test_warshall_no_modifica_la_entrada():
    original = [[False, True], [False, False]]
    copia = [fila[:] for fila in original]
    warshall(original)
    assert original == copia


def test_warshall_casos_borde():
    assert warshall([]) == []
    assert warshall([[False]]) == [[False]]
    assert warshall([[True]]) == [[True]]


def test_warshall_rechaza_no_cuadradas():
    with pytest.raises(OperacionInvalidaError):
        warshall([[True, False]])


def test_cerradura_transitiva_ejemplo():
    R = Relacion([(1, 2), (2, 3), (3, 4)], [1, 2, 3, 4])
    cierre = R.cerradura_transitiva()
    assert set(cierre.pares.elementos) == {
        (1, 2), (2, 3), (3, 4), (1, 3), (2, 4), (1, 4)
    }
    assert cierre.dominio == R.dominio


def test_cerradura_transitiva_contra_cierre_ingenuo():
    for R in _aleatorias(17):
        cierre = R.cerradura_transitiva()
        assert set(cierre.pares.elementos) == _cierre_transitivo_ingenuo(
            R.pares.elementos
        )
        assert cierre.es_transitiva()
        assert R.pares.es_subconjunto(cierre.pares)
        assert cierre.cerradura_transitiva() == cierre


def test_cerradura_reflexiva():
    R = Relacion([(1, 2)], [1, 2, 3])
    cierre = R.cerradura_reflexiva()
    assert cierre.es_reflexiva() and len(cierre) == 4
    assert cierre.cerradura_reflexiva() == cierre


def test_cerradura_simetrica():
    R = Relacion([(1, 2), (2, 2)], [1, 2])
    cierre = R.cerradura_simetrica()
    assert cierre.es_simetrica() and len(cierre) == 3
    assert cierre.cerradura_simetrica() == cierre


def test_cerraduras_son_minimas():
    for R in _aleatorias(19, cuantas=30):
        pares = set(R.pares.elementos)
        diagonal = {(a, a) for a in R.dominio}
        invertidos = {(b, a) for a, b in pares}
        assert set(R.cerradura_reflexiva().pares.elementos) == pares | diagonal
        assert set(R.cerradura_simetrica().pares.elementos) == pares | invertidos


def test_cerraduras_combinadas_dan_una_equivalencia():
    for R in _aleatorias(23):
        cierre = R.cerradura_reflexiva().cerradura_simetrica().cerradura_transitiva()
        assert cierre.es_relacion_equivalencia()


def test_cerradura_de_equivalencia_no_cambia(congruencia_mod_3):
    assert congruencia_mod_3.cerradura_transitiva() == congruencia_mod_3
