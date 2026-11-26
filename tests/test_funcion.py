import random
from itertools import product

import pytest

from teoria_conjuntos_toolkit import (
    ComposicionInvalidaError,
    Conjunto,
    FueraDeDominioError,
    Funcion,
    FuncionInvalidaError,
    NoBiyectivaError,
    Relacion,
    RelacionInvalidaError,
)


@pytest.fixture
def suma_uno():
    """Crea la función biyectiva x ↦ x + 1 de {1, 2, 3} en {2, 3, 4}.

    Entrada: ninguna.
    Salida: Funcion, biyectiva.
    """
    return Funcion.desde_regla([1, 2, 3], lambda x: x + 1, [2, 3, 4])


def _todas_las_funciones(dominio, codominio):
    return [
        Funcion(list(zip(dominio, valores)), dominio, codominio)
        for valores in product(codominio, repeat=len(dominio))
    ]


def test_construccion_valida():
    f = Funcion([(1, "a"), (2, "a")], [1, 2], ["a", "b"])
    assert f.dominio == Conjunto([1, 2])
    assert f.codominio == Conjunto(["a", "b"])
    assert len(f) == 2 and f.es_funcion()


def test_es_una_relacion():
    f = Funcion([(1, "a")], [1], ["a"])
    assert isinstance(f, Relacion)
    assert f.imagenes(1) == Conjunto(["a"])
    assert f.imagen() == Conjunto(["a"])
    assert str(f) == "{(1, 'a')}"


def test_rechaza_elemento_sin_imagen():
    with pytest.raises(FuncionInvalidaError, match="2"):
        Funcion([(1, "a")], [1, 2], ["a"])


def test_rechaza_elemento_con_varias_imagenes():
    with pytest.raises(FuncionInvalidaError, match="2 imágenes"):
        Funcion([(1, "a"), (1, "b")], [1], ["a", "b"])


def test_funcion_invalida_tambien_es_relacion_invalida():
    with pytest.raises(RelacionInvalidaError):
        Funcion([(1, "a")], [1, 2], ["a"])


def test_rechaza_pares_fuera_de_los_conjuntos():
    with pytest.raises(RelacionInvalidaError):
        Funcion([(1, "z")], [1], ["a"])


def test_inmutable_igualdad_y_hash():
    f = Funcion([(1, "a")], [1], ["a"])
    with pytest.raises(AttributeError):
        f.x = 1
    assert f == Funcion([(1, "a")], [1], ["a"])
    assert f == Relacion([(1, "a")], [1], ["a"])
    assert hash(f) == hash(Relacion([(1, "a")], [1], ["a"]))
    assert f != Funcion([(1, "a")], [1], ["a", "b"])


def test_repr_reconstruye_la_funcion():
    f = Funcion([(1, "a"), (2, "b")], [1, 2], ["a", "b"])
    entorno = {"Funcion": Funcion, "Conjunto": Conjunto}
    assert eval(repr(f), entorno) == f


def test_llamar_la_funcion(suma_uno):
    assert suma_uno(1) == 2 and suma_uno(3) == 4


def test_llamar_fuera_del_dominio(suma_uno):
    with pytest.raises(FueraDeDominioError):
        suma_uno(99)
    with pytest.raises(FueraDeDominioError):
        suma_uno([1])


def test_desde_diccionario():
    f = Funcion.desde_diccionario({1: "a", 2: "b"})
    assert f(2) == "b" and f.codominio == Conjunto(["a", "b"])
    assert f.es_biyectiva()


def test_desde_diccionario_con_codominio_mayor():
    f = Funcion.desde_diccionario({1: "a"}, codominio=["a", "b"])
    assert f.es_inyectiva() and not f.es_sobreyectiva()


def test_desde_diccionario_invalido():
    with pytest.raises(FuncionInvalidaError):
        Funcion.desde_diccionario([(1, "a")])
    with pytest.raises(RelacionInvalidaError):
        Funcion.desde_diccionario({1: "z"}, codominio=["a"])


def test_desde_regla():
    f = Funcion.desde_regla(range(-2, 3), lambda x: x * x)
    assert f.imagen() == Conjunto([0, 1, 4]) and f.codominio == f.imagen()
    assert f(-2) == f(2) == 4


def test_desde_regla_con_codominio():
    f = Funcion.desde_regla(range(3), lambda x: x * x, range(10))
    assert not f.es_sobreyectiva()
    with pytest.raises(RelacionInvalidaError):
        Funcion.desde_regla(range(5), lambda x: x * x, range(10))


def test_desde_regla_no_definida():
    with pytest.raises(FuncionInvalidaError, match="0"):
        Funcion.desde_regla(range(-1, 2), lambda x: 1 / x)


def test_desde_regla_no_invocable():
    with pytest.raises(FuncionInvalidaError):
        Funcion.desde_regla([1, 2], 5)


@pytest.mark.parametrize(
    "dominio, regla, codominio, inyectiva, sobreyectiva",
    [
        (range(-2, 3), lambda x: x * x, range(5), False, False),
        (range(-2, 3), lambda x: x * x, [0, 1, 4], False, True),
        ([1, 2, 3], lambda x: x + 1, [2, 3, 4], True, True),
        ([1, 2], lambda x: x, [1, 2, 3], True, False),
        ([1, 2, 3], lambda x: 0, [0], False, True),
        ([1, 2, 3], lambda x: 0, [0, 1], False, False),
        ([], lambda x: x, [], True, True),
        ([], lambda x: x, [1], True, False),
    ],
)
def test_clasificacion(dominio, regla, codominio, inyectiva, sobreyectiva):
    f = Funcion.desde_regla(dominio, regla, codominio)
    assert f.es_inyectiva() is inyectiva
    assert f.es_sobreyectiva() is sobreyectiva
    assert f.es_biyectiva() is (inyectiva and sobreyectiva)


@pytest.mark.parametrize(
    "n, m, inyectivas, sobreyectivas, total",
    [(3, 3, 6, 6, 27), (3, 2, 0, 6, 8), (2, 3, 6, 0, 9), (1, 1, 1, 1, 1)],
)
def test_conteo_de_funciones(n, m, inyectivas, sobreyectivas, total):
    funciones = _todas_las_funciones(list(range(n)), list(range(m)))
    assert len(funciones) == total
    assert sum(f.es_inyectiva() for f in funciones) == inyectivas
    assert sum(f.es_sobreyectiva() for f in funciones) == sobreyectivas
    assert sum(f.es_biyectiva() for f in funciones) == (
        inyectivas if n == m else 0
    )


def test_inyectiva_coincide_con_la_definicion():
    for f in _todas_las_funciones([0, 1, 2], [0, 1, 2]):
        por_definicion = all(
            f(a) != f(b) for a in f.dominio for b in f.dominio if a != b
        )
        assert f.es_inyectiva() == por_definicion


def test_funcion_inversa(suma_uno):
    inversa = suma_uno.funcion_inversa()
    assert isinstance(inversa, Funcion)
    assert inversa.dominio == suma_uno.codominio
    assert all(inversa(suma_uno(a)) == a for a in suma_uno.dominio)
    assert all(suma_uno(inversa(b)) == b for b in suma_uno.codominio)
    assert inversa.funcion_inversa() == suma_uno


def test_funcion_inversa_de_no_inyectiva():
    f = Funcion.desde_regla([1, 2], lambda x: 0, [0])
    with pytest.raises(NoBiyectivaError):
        f.funcion_inversa()


def test_funcion_inversa_de_no_sobreyectiva():
    f = Funcion.desde_regla([1, 2], lambda x: x, [1, 2, 3])
    with pytest.raises(NoBiyectivaError):
        f.funcion_inversa()


def test_relacion_inversa_siempre_existe():
    f = Funcion.desde_regla([1, 2], lambda x: 0, [0])
    inversa = f.inversa()
    assert type(inversa) is Relacion
    assert not inversa.es_funcion()


def test_composicion_de_funciones():
    f = Funcion.desde_regla([1, 2, 3], lambda x: x + 1, [2, 3, 4])
    g = Funcion.desde_regla([2, 3, 4], lambda x: x * 10, [20, 30, 40])
    h = g.composicion(f)
    assert isinstance(h, Funcion)
    assert h.dominio == f.dominio and h.codominio == g.codominio
    assert all(h(x) == g(f(x)) for x in f.dominio)


def test_composicion_con_codominio_contenido_en_el_dominio():
    f = Funcion.desde_regla([1, 2], lambda x: x, [1, 2])
    g = Funcion.desde_regla([1, 2, 3], lambda x: x * 2, [2, 4, 6])
    assert g.composicion(f)(2) == 4


def test_composicion_invalida():
    f = Funcion.desde_regla([1, 2], lambda x: x, [1, 2, 3])
    g = Funcion.desde_regla([1, 2], lambda x: x, [1, 2])
    with pytest.raises(ComposicionInvalidaError):
        g.composicion(f)


def test_composicion_con_relacion_devuelve_relacion():
    f = Funcion.desde_regla([1, 2], lambda x: x, [1, 2])
    R = Relacion([(1, 1), (1, 2)], [1, 2])
    resultado = f.composicion(R)
    assert type(resultado) is Relacion
    assert resultado == R


def test_identidad_es_neutra():
    f = Funcion.desde_regla([1, 2, 3], lambda x: x + 1, [2, 3, 4])
    id_dominio = Funcion.desde_regla([1, 2, 3], lambda x: x)
    id_codominio = Funcion.desde_regla([2, 3, 4], lambda x: x)
    assert f.composicion(id_dominio) == f
    assert id_codominio.composicion(f) == f


def test_inversa_compuesta_es_identidad(suma_uno):
    identidad = suma_uno.funcion_inversa().composicion(suma_uno)
    assert all(identidad(a) == a for a in suma_uno.dominio)


def test_composicion_es_asociativa_en_funciones_aleatorias():
    rng = random.Random(5)
    universo = list(range(5))

    def aleatoria():
        mapa = {x: rng.choice(universo) for x in universo}
        return Funcion.desde_diccionario(mapa, universo)

    for _ in range(30):
        f, g, h = aleatoria(), aleatoria(), aleatoria()
        assert h.composicion(g.composicion(f)) == h.composicion(g).composicion(f)


def test_composicion_de_inyectivas_es_inyectiva_y_de_sobreyectivas_es_sobreyectiva():
    for f in _todas_las_funciones([0, 1, 2], [0, 1, 2]):
        for g in _todas_las_funciones([0, 1, 2], [0, 1, 2]):
            h = g.composicion(f)
            if f.es_inyectiva() and g.es_inyectiva():
                assert h.es_inyectiva()
            if f.es_sobreyectiva() and g.es_sobreyectiva():
                assert h.es_sobreyectiva()
