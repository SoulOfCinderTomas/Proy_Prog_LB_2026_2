import random
import re
from itertools import product

import pytest

from teoria_conjuntos_toolkit import (
    Conjunto,
    FamiliaDeConjuntos,
    FamiliaInvalidaError,
    FueraDeDominioError,
    NoEsEquivalenciaError,
    ParticionInvalidaError,
    Relacion,
    RelacionInvalidaError,
    RelacionNoHomogeneaError,
    clase_de,
    generar_particion,
    relacion_desde_particion,
    validar_equivalencia,
    validar_particion,
)


@pytest.fixture
def congruencia_mod_3():
    """Crea la relación de congruencia módulo 3 sobre {0, ..., 5}.

    Entrada: ninguna.
    Salida: Relacion, de equivalencia con las clases {0, 3}, {1, 4} y {2, 5}.
    """
    return Relacion.desde_predicado(range(6), lambda a, b: (a - b) % 3 == 0)


def _como_conjunto_de_bloques(familia):
    return {bloque.elementos for bloque in familia}


def _particion_aleatoria(rng, n):
    etiquetas = {x: rng.randint(0, 3) for x in range(n)}
    grupos = {}
    for x, etiqueta in etiquetas.items():
        grupos.setdefault(etiqueta, []).append(x)
    return list(grupos.values())


def _relacion_aleatoria(rng, n):
    todos = list(product(range(n), repeat=2))
    return Relacion(rng.sample(todos, rng.randint(0, len(todos))), range(n))


def test_validar_equivalencia_devuelve_la_misma_relacion(congruencia_mod_3):
    assert validar_equivalencia(congruencia_mod_3) is congruencia_mod_3


@pytest.mark.parametrize(
    "pares, faltan",
    [
        ([(1, 1), (2, 2), (1, 2)], "simétrica"),
        ([(1, 1), (1, 2), (2, 1), (2, 3), (3, 2), (3, 3)], "transitiva"),
        ([(1, 2), (2, 1), (1, 1), (2, 2)], "reflexiva"),
        ([], "reflexiva"),
    ],
)
def test_validar_equivalencia_indica_que_propiedad_falla(pares, faltan):
    with pytest.raises(NoEsEquivalenciaError, match=faltan):
        validar_equivalencia(Relacion(pares, [1, 2, 3]))


def test_validar_equivalencia_rechaza_lo_que_no_es_relacion():
    with pytest.raises(RelacionInvalidaError):
        validar_equivalencia({(1, 1)})


def test_validar_equivalencia_exige_relacion_homogenea():
    with pytest.raises(RelacionNoHomogeneaError):
        validar_equivalencia(Relacion([(1, "a")], [1], ["a"]))


def test_clase_de(congruencia_mod_3):
    assert clase_de(congruencia_mod_3, 0) == Conjunto([0, 3])
    assert clase_de(congruencia_mod_3, 4) == Conjunto([1, 4])
    assert clase_de(congruencia_mod_3, 3) == clase_de(congruencia_mod_3, 0)


def test_clase_de_contiene_al_elemento_y_a_sus_equivalentes(congruencia_mod_3):
    for a in congruencia_mod_3.dominio:
        clase = clase_de(congruencia_mod_3, a)
        assert a in clase
        assert all((a, b) in congruencia_mod_3 for b in clase)


def test_clase_de_fuera_del_dominio(congruencia_mod_3):
    with pytest.raises(FueraDeDominioError):
        clase_de(congruencia_mod_3, 99)


def test_clase_de_exige_equivalencia():
    orden = Relacion.desde_predicado(range(1, 4), lambda a, b: a <= b)
    with pytest.raises(NoEsEquivalenciaError):
        clase_de(orden, 1)


def test_generar_particion(congruencia_mod_3):
    P = generar_particion(congruencia_mod_3)
    assert isinstance(P, FamiliaDeConjuntos)
    assert list(P) == [Conjunto([0, 3]), Conjunto([1, 4]), Conjunto([2, 5])]
    assert P.es_particion_de(range(6))


def test_generar_particion_de_la_relacion_total_y_de_la_diagonal():
    total = Relacion.desde_predicado(range(4), lambda a, b: True)
    diagonal = Relacion.desde_predicado(range(4), lambda a, b: a == b)
    assert list(generar_particion(total)) == [Conjunto(range(4))]
    assert list(generar_particion(diagonal)) == [Conjunto([x]) for x in range(4)]


def test_generar_particion_de_conjunto_vacio():
    P = generar_particion(Relacion([], []))
    assert len(P) == 0 and P.es_particion_de([])


def test_generar_particion_exige_equivalencia():
    with pytest.raises(NoEsEquivalenciaError):
        generar_particion(Relacion([(1, 2)], [1, 2]))


def test_numero_de_clases_de_congruencia_modulo_n():
    for n in range(1, 6):
        R = Relacion.desde_predicado(range(12), lambda a, b: (a - b) % n == 0)
        assert len(generar_particion(R)) == n


def test_validar_particion_acepta_y_devuelve_familia():
    P = validar_particion([[1, 2], [3]], [1, 2, 3])
    assert isinstance(P, FamiliaDeConjuntos) and len(P) == 2
    familia = FamiliaDeConjuntos([[1], [2]])
    assert validar_particion(familia, [1, 2]) is familia


def test_validar_particion_vacia():
    assert len(validar_particion([], [])) == 0


def test_validar_particion_bloque_vacio():
    with pytest.raises(ParticionInvalidaError, match="vacío"):
        validar_particion([[1], [], [2]], [1, 2])


def test_validar_particion_bloques_traslapados():
    with pytest.raises(ParticionInvalidaError, match=re.escape("traslapan en {2}")):
        validar_particion([[1, 2], [2, 3]], [1, 2, 3])


def test_validar_particion_sin_cubrir():
    with pytest.raises(ParticionInvalidaError, match=re.escape("faltan por cubrir {3}")):
        validar_particion([[1], [2]], [1, 2, 3])


def test_validar_particion_con_elementos_fuera_del_universo():
    with pytest.raises(ParticionInvalidaError, match=re.escape("fuera del universo {3}")):
        validar_particion([[1], [2, 3]], [1, 2])


def test_particion_invalida_es_familia_invalida():
    with pytest.raises(FamiliaInvalidaError):
        validar_particion([[1], [1]], [1])


@pytest.mark.parametrize("mala", ["abc", 5, [[1], 7]])
def test_validar_particion_datos_que_no_son_familia(mala):
    with pytest.raises(FamiliaInvalidaError):
        validar_particion(mala, [1])


def test_relacion_desde_particion():
    R = relacion_desde_particion([[1, 2], [3]], [1, 2, 3])
    assert R == Relacion([(1, 1), (1, 2), (2, 1), (2, 2), (3, 3)], [1, 2, 3])
    assert R.es_relacion_equivalencia()


def test_relacion_desde_particion_invalida():
    with pytest.raises(ParticionInvalidaError):
        relacion_desde_particion([[1, 2], [2, 3]], [1, 2, 3])


def test_relacion_desde_particion_vacia():
    R = relacion_desde_particion([], [])
    assert len(R) == 0 and R.es_relacion_equivalencia()


def test_relacion_desde_particion_tiene_suma_de_cuadrados_de_pares():
    rng = random.Random(3)
    for _ in range(40):
        bloques = _particion_aleatoria(rng, 8)
        R = relacion_desde_particion(bloques, range(8))
        assert len(R) == sum(len(b) ** 2 for b in bloques)


def test_particion_a_relacion_a_particion():
    rng = random.Random(5)
    for _ in range(60):
        bloques = _particion_aleatoria(rng, 8)
        original = FamiliaDeConjuntos(bloques)
        R = relacion_desde_particion(bloques, range(8))
        regenerada = generar_particion(R)
        assert _como_conjunto_de_bloques(regenerada) == _como_conjunto_de_bloques(
            original
        )
        assert regenerada.es_particion_de(range(8))


def test_relacion_a_particion_a_relacion():
    rng = random.Random(7)
    for _ in range(60):
        base = _relacion_aleatoria(rng, 6)
        equivalencia = (
            base.cerradura_reflexiva().cerradura_simetrica().cerradura_transitiva()
        )
        particion = generar_particion(equivalencia)
        assert particion.es_particion_de(range(6))
        assert relacion_desde_particion(particion, range(6)) == equivalencia


def test_las_clases_son_iguales_o_disjuntas():
    rng = random.Random(11)
    for _ in range(40):
        R = relacion_desde_particion(_particion_aleatoria(rng, 7), range(7))
        for a in R.dominio:
            for b in R.dominio:
                ca, cb = clase_de(R, a), clase_de(R, b)
                if (a, b) in R:
                    assert ca == cb
                else:
                    assert ca.es_disjunto(cb)
