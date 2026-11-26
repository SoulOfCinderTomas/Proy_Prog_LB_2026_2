import io
import random
from math import hypot

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest
from matplotlib.axes import Axes
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

from teoria_conjuntos_toolkit import (
    Conjunto,
    ConjuntoDemasiadoGrandeError,
    FamiliaDeConjuntos,
    FamiliaInvalidaError,
    Funcion,
    GraficoInvalidoError,
    NaturalInvalidoError,
    NoEsEquivalenciaError,
    ParticionInvalidaError,
    Relacion,
    RelacionInvalidaError,
    RelacionNoHomogeneaError,
    UniversoInvalidoError,
    arbol_von_neumann,
    cajas_von_neumann,
    diagrama_sagital,
    diagrama_venn,
    grafo_relacion,
    regiones_venn,
    visualizar_particion,
)
from teoria_conjuntos_toolkit.graphic import (
    _GEOMETRIA_VENN,
    _MARGEN_VON_NEUMANN,
    _RADIO_VENN,
    LIMITE_VON_NEUMANN,
    _distribuir_islas,
)


@pytest.fixture(autouse=True)
def cerrar_figuras():
    """Cierra todas las figuras de matplotlib después de cada prueba.

    Entrada: ninguna.
    Salida: None, deja sin figuras abiertas al terminar la prueba.
    """
    yield
    plt.close("all")


def _textos(ax):
    return [t.get_text() for t in ax.texts]


def _cuantos(ax, clase):
    return sum(isinstance(p, clase) for p in ax.patches)


def _renderiza(ax):
    buffer = io.BytesIO()
    ax.figure.savefig(buffer, format="png")
    return buffer.tell()


def _tres_conjuntos_aleatorios(rng):
    return [set(rng.sample(range(12), rng.randint(0, 8))) for _ in range(3)]


def test_regiones_venn_de_dos_conjuntos():
    regiones = regiones_venn([[1, 2, 3], [3, 4]])
    assert regiones == {
        (0,): Conjunto([1, 2]),
        (1,): Conjunto([4]),
        (0, 1): Conjunto([3]),
    }


def test_regiones_venn_de_tres_conjuntos():
    regiones = regiones_venn([{1, 2, 3, 4}, {3, 4, 5, 6}, {4, 6, 7, 8}])
    assert regiones[(0,)] == Conjunto([1, 2])
    assert regiones[(0, 1)] == Conjunto([3])
    assert regiones[(0, 1, 2)] == Conjunto([4])
    assert regiones[(1, 2)] == Conjunto([6])
    assert regiones[(2,)] == Conjunto([7, 8])
    assert regiones[(0, 2)] == Conjunto()
    assert len(regiones) == 7


def test_regiones_venn_forman_una_particion_de_la_union():
    rng = random.Random(1)
    for _ in range(80):
        conjuntos = _tres_conjuntos_aleatorios(rng)
        regiones = regiones_venn(conjuntos)
        union = Conjunto(set().union(*conjuntos))
        no_vacias = [r for r in regiones.values() if not r.es_vacio()]
        assert FamiliaDeConjuntos(no_vacias).es_particion_de(union)


def test_cada_conjunto_es_la_union_de_sus_regiones():
    rng = random.Random(2)
    for _ in range(80):
        conjuntos = _tres_conjuntos_aleatorios(rng)
        regiones = regiones_venn(conjuntos)
        for i, conjunto in enumerate(conjuntos):
            suyas = [r for dentro, r in regiones.items() if i in dentro]
            assert sum(r.cardinal for r in suyas) == len(conjunto)


@pytest.mark.parametrize("cantidad", [0, 1, 4])
def test_regiones_venn_solo_acepta_dos_o_tres(cantidad):
    with pytest.raises(GraficoInvalidoError):
        regiones_venn([[i] for i in range(cantidad)])


def test_regiones_venn_datos_invalidos():
    with pytest.raises(FamiliaInvalidaError):
        regiones_venn("abc")


@pytest.mark.parametrize("n", [2, 3])
def test_cada_etiqueta_de_venn_cae_en_su_region(n):
    geometria = _GEOMETRIA_VENN[n]
    assert len(geometria["etiquetas"]) == 2**n - 1
    for dentro, (x, y) in geometria["etiquetas"].items():
        for i, (cx, cy) in enumerate(geometria["centros"]):
            distancia = hypot(x - cx, y - cy)
            assert (distancia < _RADIO_VENN) == (i in dentro)
            assert abs(distancia - _RADIO_VENN) > 0.05


def test_diagrama_venn_dos_conjuntos():
    ax = diagrama_venn([[1, 2, 3], [3, 4]])
    assert isinstance(ax, Axes)
    textos = _textos(ax)
    assert {"A", "B", "1, 2", "3", "4"} <= set(textos)
    assert _cuantos(ax, Circle) == 2
    assert _renderiza(ax) > 1000


def test_diagrama_venn_tres_conjuntos_con_nombres():
    ax = diagrama_venn(
        [{1, 2, 3, 4}, {3, 4, 5, 6}, {4, 6, 7, 8}],
        nombres=["Pares", "Multiplos", "Otros"],
        titulo="Tres",
    )
    textos = _textos(ax)
    assert {"Pares", "Multiplos", "Otros", "1, 2", "7, 8", "4"} <= set(textos)
    assert ax.get_title() == "Tres" and _cuantos(ax, Circle) == 3
    assert _renderiza(ax) > 1000


def test_diagrama_venn_con_universo():
    ax = diagrama_venn([[1, 2], [2, 3]], universo=range(1, 7))
    textos = _textos(ax)
    assert "U" in textos and "4, 5, 6" in textos
    assert _cuantos(ax, Rectangle) == 1


def test_diagrama_venn_sin_universo_no_dibuja_marco():
    ax = diagrama_venn([[1, 2], [2, 3]])
    assert "U" not in _textos(ax) and _cuantos(ax, Rectangle) == 0


def test_diagrama_venn_muestra_solo_el_cardinal_si_hay_muchos():
    ax = diagrama_venn([range(10), range(5, 12)], max_elementos=4)
    textos = _textos(ax)
    assert textos.count("(5)") == 2 and "10, 11" in textos


def test_diagrama_venn_usa_los_ejes_recibidos():
    figura, ax = plt.subplots()
    resultado = diagrama_venn([[1], [2]], ax=ax)
    assert resultado is ax and plt.get_fignums() == [figura.number]


def test_diagrama_venn_errores_no_dejan_figuras_abiertas():
    with pytest.raises(UniversoInvalidoError):
        diagrama_venn([[1, 2], [3]], universo=[1, 2])
    with pytest.raises(GraficoInvalidoError):
        diagrama_venn([[1], [2]], nombres=["solo uno"])
    with pytest.raises(GraficoInvalidoError):
        diagrama_venn([[1]])
    assert plt.get_fignums() == []


def test_grafo_relacion_dibuja_nodos_y_flechas():
    R = Relacion.desde_predicado(range(1, 5), lambda a, b: a <= b)
    ax = grafo_relacion(R, titulo="Orden")
    assert isinstance(ax, Axes) and ax.get_title() == "Orden"
    assert set(_textos(ax)) >= {"1", "2", "3", "4"}
    assert _cuantos(ax, FancyArrowPatch) == len(R)
    assert _renderiza(ax) > 1000


def test_grafo_relacion_con_bucles_y_ciclos():
    R = Relacion.desde_predicado(range(6), lambda a, b: (a - b) % 3 == 0)
    ax = grafo_relacion(R)
    assert _cuantos(ax, FancyArrowPatch) == len(R) == 12
    assert _renderiza(ax) > 1000


def test_grafo_relacion_casos_borde():
    for R in (Relacion([], [1, 2, 3]), Relacion([(1, 1)], [1]), Relacion([], [])):
        ax = grafo_relacion(R)
        assert _cuantos(ax, FancyArrowPatch) == len(R)
        assert _renderiza(ax) > 1000
        plt.close("all")


def test_grafo_relacion_con_funcion_homogenea():
    f = Funcion.desde_regla(range(4), lambda x: (x + 1) % 4, range(4))
    assert _cuantos(grafo_relacion(f), FancyArrowPatch) == 4


def test_grafo_relacion_exige_relacion_homogenea():
    with pytest.raises(RelacionNoHomogeneaError):
        grafo_relacion(Relacion([(1, "a")], [1], ["a"]))
    assert plt.get_fignums() == []


@pytest.mark.parametrize("graficador", [grafo_relacion, diagrama_sagital])
def test_graficadores_de_relaciones_rechazan_otros_objetos(graficador):
    with pytest.raises(RelacionInvalidaError):
        graficador({(1, 2)})
    assert plt.get_fignums() == []


def test_diagrama_sagital_de_una_funcion():
    f = Funcion.desde_regla([1, 2, 3, 4], lambda x: x % 3, [0, 1, 2, 3])
    ax = diagrama_sagital(f, titulo="f")
    textos = _textos(ax)
    assert {"A", "B", "1", "2", "3", "4", "0"} <= set(textos)
    assert _cuantos(ax, FancyArrowPatch) == 4
    assert _renderiza(ax) > 1000


def _huecos(ax):
    return sum(
        isinstance(p, Circle) and tuple(p.get_facecolor()) == (1.0, 1.0, 1.0, 1.0)
        for p in ax.patches
    )


def test_diagrama_sagital_marca_los_elementos_que_no_son_imagen():
    inyectiva = Funcion.desde_regla([1, 2], lambda x: x, [1, 2, 3, 4])
    assert _huecos(diagrama_sagital(inyectiva)) == 2
    plt.close("all")
    biyectiva = Funcion.desde_regla([1, 2, 3], lambda x: x + 1, [2, 3, 4])
    assert _huecos(diagrama_sagital(biyectiva)) == 0


def _alturas_por_elemento(ax):
    izquierda = {t.get_text(): t.get_position()[1] for t in ax.texts if t.get_position()[0] < -1.6}
    derecha = {t.get_text(): t.get_position()[1] for t in ax.texts if t.get_position()[0] > 1.6}
    return izquierda, derecha


@pytest.mark.parametrize(
    "relacion",
    [
        Relacion([(1, 2), (2, 3), (3, 1)], [1, 2, 3], [1, 2, 3]),
        Relacion([(1, "a"), (1, "b"), (2, "b"), (3, "c")], [1, 2, 3], ["a", "b", "c", "d"]),
        Funcion.desde_regla([1, 2, 3, 4], lambda x: x % 3, [0, 1, 2, 3]),
    ],
)
def test_las_flechas_del_diagrama_sagital_unen_cada_par(relacion):
    ax = diagrama_sagital(relacion)
    izquierda, derecha = _alturas_por_elemento(ax)
    esperadas = {(izquierda[str(a)], derecha[str(b)]) for a, b in relacion}
    dibujadas = {
        (p._posA_posB[0][1], p._posA_posB[1][1])
        for p in ax.patches
        if isinstance(p, FancyArrowPatch)
    }
    assert dibujadas == esperadas


def test_diagrama_sagital_de_relacion_con_varias_imagenes():
    R = Relacion([(1, "a"), (1, "b"), (2, "b")], [1, 2], ["a", "b", "c"])
    ax = diagrama_sagital(R)
    assert _cuantos(ax, FancyArrowPatch) == 3 and _huecos(ax) == 1


def test_diagrama_sagital_casos_borde():
    for R in (Relacion([], [], []), Relacion([], [1], [])):
        assert _renderiza(diagrama_sagital(R)) > 1000
        plt.close("all")


def test_visualizar_particion_desde_listas():
    ax = visualizar_particion([[1, 2, 3, 4, 5], [6], [7, 8]], titulo="P")
    assert _cuantos(ax, FancyBboxPatch) == 3
    assert {"[1]", "[6]", "[7]"} <= set(_textos(ax))
    assert {str(i) for i in range(1, 9)} <= set(_textos(ax))
    assert _renderiza(ax) > 1000


def test_visualizar_particion_desde_relacion_de_equivalencia():
    R = Relacion.desde_predicado(range(8), lambda a, b: (a - b) % 3 == 0)
    ax = visualizar_particion(R)
    assert _cuantos(ax, FancyBboxPatch) == 3
    assert {"[0]", "[1]", "[2]"} <= set(_textos(ax))


def test_visualizar_particion_acepta_una_familia_y_un_universo():
    familia = FamiliaDeConjuntos([[1, 2], [3]])
    ax = visualizar_particion(familia, universo=[1, 2, 3])
    assert _cuantos(ax, FancyBboxPatch) == 2


def test_visualizar_particion_vacia():
    ax = visualizar_particion([], universo=[])
    assert _cuantos(ax, FancyBboxPatch) == 0 and _renderiza(ax) > 1000


def test_visualizar_particion_invalida():
    with pytest.raises(ParticionInvalidaError):
        visualizar_particion([[1, 2], [2, 3]])
    with pytest.raises(ParticionInvalidaError):
        visualizar_particion([[1], [2]], universo=[1, 2, 3])
    with pytest.raises(FamiliaInvalidaError):
        visualizar_particion("abc")
    with pytest.raises(NoEsEquivalenciaError):
        visualizar_particion(Relacion([(1, 2)], [1, 2]))
    assert plt.get_fignums() == []


def _se_traslapan(a, b):
    xa, ya, wa, ha, _ = a
    xb, yb, wb, hb, _ = b
    return xa < xb + wb and xb < xa + wa and ya < yb + hb and yb < ya + ha


def test_las_islas_no_se_traslapan_ni_salen_de_la_cuadricula():
    rng = random.Random(4)
    for _ in range(40):
        tamanos = [rng.randint(1, 9) for _ in range(rng.randint(1, 9))]
        familia = FamiliaDeConjuntos([range(100 * i, 100 * i + t) for i, t in enumerate(tamanos)])
        islas = _distribuir_islas(familia)
        assert len(islas) == len(tamanos)
        for i, isla in enumerate(islas):
            assert isla[0] >= 0 and isla[1] >= 0
            assert all(not _se_traslapan(isla, otra) for otra in islas[:i])


def test_islas_de_familia_vacia():
    assert _distribuir_islas(FamiliaDeConjuntos()) == []


@pytest.mark.parametrize("n", range(0, LIMITE_VON_NEUMANN + 1))
def test_cantidad_de_cajas_de_von_neumann(n):
    assert len(cajas_von_neumann(n)) == 2**n


@pytest.mark.parametrize("n", range(1, LIMITE_VON_NEUMANN + 1))
def test_cada_natural_aparece_tantas_veces_como_predice_la_teoria(n):
    cajas = cajas_von_neumann(n)
    for k in range(n):
        assert sum(c.valor == k for c in cajas) == 2 ** (n - 1 - k)
    assert sum(c.valor == n for c in cajas) == 1


@pytest.mark.parametrize("n", [1, 3, 5, LIMITE_VON_NEUMANN])
def test_cajas_de_von_neumann_estan_bien_anidadas(n):
    cajas = cajas_von_neumann(n)
    raiz = cajas[0]
    assert (raiz.x, raiz.y, raiz.nivel, raiz.valor) == (0.0, 0.0, 0, n)
    for caja in cajas[1:]:
        padres = [
            p
            for p in cajas
            if p.nivel == caja.nivel - 1
            and p.x <= caja.x
            and caja.x + caja.ancho <= p.x + p.ancho
            and p.y <= caja.y
            and caja.y + caja.alto <= p.y + p.alto
        ]
        assert padres and caja.valor < padres[0].valor
    mismas_capas = [(a, b) for a in cajas for b in cajas if a is not b and a.nivel == b.nivel]
    assert all(
        not (a.x < b.x + b.ancho and b.x < a.x + a.ancho and a.y < b.y + b.alto and b.y < a.y + a.alto)
        for a, b in mismas_capas
    )


@pytest.mark.parametrize("n", [3, 5, LIMITE_VON_NEUMANN])
def test_cajas_de_la_misma_capa_dejan_margen(n):
    cajas = cajas_von_neumann(n)
    for a in cajas:
        for b in cajas:
            if a is not b and a.nivel == b.nivel:
                separacion = max(b.x - (a.x + a.ancho), a.x - (b.x + b.ancho))
                assert separacion >= _MARGEN_VON_NEUMANN - 1e-9


def test_caja_del_cero_es_una_hoja():
    cajas = cajas_von_neumann(0)
    assert len(cajas) == 1 and cajas[0].valor == 0


@pytest.mark.parametrize("malo", [-1, 2.5, "3", None, True])
def test_von_neumann_rechaza_no_naturales(malo):
    with pytest.raises(NaturalInvalidoError):
        cajas_von_neumann(malo)
    with pytest.raises(NaturalInvalidoError):
        arbol_von_neumann(malo)


def test_von_neumann_rechaza_naturales_demasiado_grandes():
    with pytest.raises(ConjuntoDemasiadoGrandeError):
        arbol_von_neumann(LIMITE_VON_NEUMANN + 1)
    assert plt.get_fignums() == []


@pytest.mark.parametrize("n", [0, 1, 3, LIMITE_VON_NEUMANN])
def test_arbol_von_neumann(n):
    ax = arbol_von_neumann(n)
    assert isinstance(ax, Axes)
    assert _cuantos(ax, Rectangle) == 2**n
    assert len(_textos(ax)) == 2**n
    assert ax.get_title() == f"Natural {n} de Von Neumann"
    assert _renderiza(ax) > 1000


def test_arbol_von_neumann_con_titulo_y_ejes_propios():
    figura, ax = plt.subplots()
    assert arbol_von_neumann(2, ax=ax, titulo="Dos") is ax
    assert ax.get_title() == "Dos" and plt.get_fignums() == [figura.number]
