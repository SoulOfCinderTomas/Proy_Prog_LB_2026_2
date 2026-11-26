from __future__ import annotations

from itertools import combinations
from math import ceil, sqrt
from typing import Any, Iterable, NamedTuple, Optional

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.axes import Axes
from matplotlib.colors import to_rgba
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle

from .conjunto import (
    Conjunto,
    como_conjunto,
    interseccion_generalizada,
    union_generalizada,
)
from .equivalencia import generar_particion, validar_particion
from .exceptions import (
    ConjuntoDemasiadoGrandeError,
    GraficoInvalidoError,
    RelacionNoHomogeneaError,
    UniversoInvalidoError,
)
from .familia import FamiliaDeConjuntos, numero_von_neumann
from .relacion import Relacion, validar_relacion
from .utils import validar_natural

LIMITE_VON_NEUMANN = 6

_PALETA = (
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#E45756",
    "#72B7B2",
    "#B279A2",
    "#EECA3B",
    "#9D755D",
)

_RADIO_VENN = 1.0

_GEOMETRIA_VENN = {
    2: {
        "centros": [(-0.55, 0.0), (0.55, 0.0)],
        "nombres": [(-1.1, 1.22), (1.1, 1.22)],
        "etiquetas": {(0,): (-1.0, 0.0), (1,): (1.0, 0.0), (0, 1): (0.0, 0.0)},
        "marco": (-2.1, -1.5, 4.2, 3.3),
        "fuera": (2.0, -1.4),
        "xlim": (-2.3, 2.3),
        "ylim": (-1.7, 1.95),
    },
    3: {
        "centros": [(-0.55, 0.32), (0.55, 0.32), (0.0, -0.63)],
        "nombres": [(-1.3, 1.5), (1.3, 1.5), (0.0, -1.85)],
        "etiquetas": {
            (0,): (-0.95, 0.65),
            (1,): (0.95, 0.65),
            (2,): (0.0, -1.2),
            (0, 1): (0.0, 0.85),
            (0, 2): (-0.62, -0.28),
            (1, 2): (0.62, -0.28),
            (0, 1, 2): (0.0, 0.12),
        },
        "marco": (-2.1, -2.2, 4.2, 4.2),
        "fuera": (2.0, -2.1),
        "xlim": (-2.3, 2.3),
        "ylim": (-2.4, 2.2),
    },
}

_MARGEN_VON_NEUMANN = 0.3
_BANDA_VON_NEUMANN = 0.55


class Caja(NamedTuple):
    valor: int
    x: float
    y: float
    ancho: float
    alto: float
    nivel: int


def _relleno(color: str, transparencia: float = 0.35) -> tuple:
    """Convierte un color en una tupla RGBA con transparencia.

    Entrada: color (str), color en cualquier formato de matplotlib; transparencia (float), opacidad entre 0 y 1.
    Salida: tuple, color RGBA.
    """
    return to_rgba(color, transparencia)


def _preparar_ejes(
    ax: Optional[Axes], titulo: Optional[str], tamano: tuple
) -> Axes:
    """Crea (si hace falta) y configura unos ejes sin marco con proporción 1:1.

    Entrada: ax (Axes, opcional), ejes donde dibujar; titulo (str, opcional), título del gráfico; tamano (tuple), tamaño (ancho, alto) en pulgadas de la figura nueva.
    Salida: Axes, los ejes recibidos o unos nuevos, ya configurados.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=tamano)
    ax.set_axis_off()
    ax.set_aspect("equal")
    if titulo:
        ax.set_title(titulo)
    return ax


def _texto_elementos(conjunto: Conjunto, max_elementos: int) -> str:
    """Escribe los elementos de un conjunto en filas de a tres, o su cardinal si son muchos.

    Entrada: conjunto (Conjunto), conjunto a escribir; max_elementos (int), máximo de elementos que se listan.
    Salida: str, "" si es vacío, los elementos separados por comas si caben, o "(n)" con el cardinal si no.
    """
    if conjunto.es_vacio():
        return ""
    if conjunto.cardinal > max_elementos:
        return f"({conjunto.cardinal})"
    elementos = [str(e) for e in conjunto]
    filas = [", ".join(elementos[i : i + 3]) for i in range(0, len(elementos), 3)]
    return "\n".join(filas)


def _como_familia(conjuntos: Iterable[Iterable[Any]]) -> FamiliaDeConjuntos:
    """Convierte una colección de conjuntos en FamiliaDeConjuntos.

    Entrada: conjuntos (iterable de iterables), colección de conjuntos.
    Salida: FamiliaDeConjuntos, la misma si ya lo era. Lanza FamiliaInvalidaError si los datos no forman una familia.
    """
    if isinstance(conjuntos, FamiliaDeConjuntos):
        return conjuntos
    return FamiliaDeConjuntos(conjuntos)


def regiones_venn(conjuntos: Iterable[Iterable[Any]]) -> dict:
    """Calcula las regiones de un diagrama de Venn de 2 o 3 conjuntos.

    Entrada: conjuntos (iterable de iterables), dos o tres conjuntos.
    Salida: dict, cuya clave es la tupla de posiciones de los conjuntos que contienen la región (por ejemplo (0, 2) es A ∩ C sin B) y cuyo valor es el Conjunto de elementos exclusivos de esa región. Lanza GraficoInvalidoError si no son 2 o 3 conjuntos y FamiliaInvalidaError si los datos no son válidos.
    """
    familia = _como_familia(conjuntos)
    n = len(familia)
    if n not in _GEOMETRIA_VENN:
        raise GraficoInvalidoError(
            f"El diagrama de Venn admite 2 o 3 conjuntos, se recibieron {n}."
        )
    regiones = {}
    for tamano in range(1, n + 1):
        for dentro in combinations(range(n), tamano):
            fuera = [j for j in range(n) if j not in dentro]
            comun = interseccion_generalizada(familia[i] for i in dentro)
            regiones[dentro] = comun.diferencia(
                union_generalizada(familia[j] for j in fuera)
            )
    return regiones


def diagrama_venn(
    conjuntos: Iterable[Iterable[Any]],
    nombres: Optional[Iterable[str]] = None,
    universo: Optional[Iterable[Any]] = None,
    ax: Optional[Axes] = None,
    titulo: Optional[str] = None,
    max_elementos: int = 6,
) -> Axes:
    """Dibuja el diagrama de Venn de 2 o 3 conjuntos, con los elementos de cada región.

    Entrada: conjuntos (iterable de iterables), dos o tres conjuntos; nombres (iterable de str, opcional), nombres de los conjuntos, por defecto A, B y C; universo (iterable, opcional), si se da se dibuja el rectángulo U con los elementos que quedan fuera; ax (Axes, opcional), ejes donde dibujar; titulo (str, opcional), título; max_elementos (int), si una región tiene más elementos se escribe solo su cardinal.
    Salida: Axes, los ejes con el dibujo. Lanza GraficoInvalidoError si no son 2 o 3 conjuntos o los nombres no coinciden en cantidad, UniversoInvalidoError si algún conjunto no cabe en el universo, y FamiliaInvalidaError si los datos no son válidos.
    """
    familia = _como_familia(conjuntos)
    regiones = regiones_venn(familia)
    n = len(familia)
    etiquetas = list("ABC"[:n]) if nombres is None else [str(m) for m in nombres]
    if len(etiquetas) != n:
        raise GraficoInvalidoError(
            f"Se esperaban {n} nombres, se recibieron {len(etiquetas)}."
        )
    u = None
    if universo is not None:
        u = como_conjunto(universo)
        if not familia.union().es_subconjunto(u):
            raise UniversoInvalidoError(
                f"Hay elementos fuera del universo {u}: "
                f"{familia.union().diferencia(u)}."
            )
    geometria = _GEOMETRIA_VENN[n]
    ax = _preparar_ejes(ax, titulo, (6, 5))
    ax.set_xlim(*geometria["xlim"])
    ax.set_ylim(*geometria["ylim"])
    for i, (centro, etiqueta) in enumerate(zip(geometria["centros"], etiquetas)):
        color = _PALETA[i]
        ax.add_patch(
            Circle(
                centro,
                _RADIO_VENN,
                facecolor=_relleno(color),
                edgecolor=color,
                linewidth=2,
            )
        )
        ax.text(
            *geometria["nombres"][i],
            etiqueta,
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold",
            color=color,
        )
    for dentro, region in regiones.items():
        ax.text(
            *geometria["etiquetas"][dentro],
            _texto_elementos(region, max_elementos),
            ha="center",
            va="center",
            fontsize=10,
        )
    if u is not None:
        x0, y0, ancho, alto = geometria["marco"]
        ax.add_patch(
            Rectangle((x0, y0), ancho, alto, fill=False, edgecolor="#444444", linewidth=1.5)
        )
        ax.text(x0 + 0.12, y0 + alto - 0.12, "U", ha="left", va="top", fontsize=13, fontweight="bold")
        afuera = u.diferencia(familia.union())
        ax.text(
            *geometria["fuera"],
            _texto_elementos(afuera, max_elementos),
            ha="right",
            va="bottom",
            fontsize=10,
        )
    return ax


def grafo_relacion(
    relacion: Relacion, ax: Optional[Axes] = None, titulo: Optional[str] = None
) -> Axes:
    """Dibuja una relación sobre un conjunto como grafo dirigido: un nodo por elemento y una flecha por cada par.

    Entrada: relacion (Relacion), relación con dominio igual a codominio; ax (Axes, opcional), ejes donde dibujar; titulo (str, opcional), título.
    Salida: Axes, los ejes con el dibujo; los pares (a, a) se ven como bucles. Lanza RelacionInvalidaError si no es una Relacion y RelacionNoHomogeneaError si dominio y codominio difieren (en ese caso usa diagrama_sagital).
    """
    validar_relacion(relacion)
    if not relacion.es_homogenea():
        raise RelacionNoHomogeneaError(
            "grafo_relacion requiere dominio igual a codominio; "
            "para relaciones entre conjuntos distintos usa diagrama_sagital."
        )
    ax = _preparar_ejes(ax, titulo, (6, 6))
    grafo = nx.DiGraph()
    grafo.add_nodes_from(relacion.dominio)
    grafo.add_edges_from(relacion.pares.elementos)
    posiciones = nx.circular_layout(grafo)
    tamano = 900 if len(grafo) <= 8 else 450
    nx.draw_networkx_nodes(
        grafo,
        posiciones,
        ax=ax,
        node_size=tamano,
        node_color="#cfe3f7",
        edgecolors=_PALETA[0],
    )
    nx.draw_networkx_labels(
        grafo, posiciones, ax=ax, labels={a: str(a) for a in grafo.nodes}
    )
    nx.draw_networkx_edges(
        grafo,
        posiciones,
        ax=ax,
        node_size=tamano,
        arrowsize=16,
        edge_color="#333333",
        connectionstyle="arc3,rad=0.18",
    )
    ax.margins(0.15)
    return ax


def diagrama_sagital(
    relacion: Relacion, ax: Optional[Axes] = None, titulo: Optional[str] = None
) -> Axes:
    """Dibuja una relación entre dos conjuntos como diagrama sagital: dominio a la izquierda, codominio a la derecha y una flecha por cada par.

    Entrada: relacion (Relacion o Funcion), relación de A en B; ax (Axes, opcional), ejes donde dibujar; titulo (str, opcional), título.
    Salida: Axes, los ejes con el dibujo; los elementos del codominio que son imagen se ven rellenos y los demás vacíos. Lanza RelacionInvalidaError si no es una Relacion.
    """
    validar_relacion(relacion)
    ax = _preparar_ejes(ax, titulo, (6, 5))
    filas = max(relacion.dominio.cardinal, relacion.codominio.cardinal, 1)
    posiciones = {}
    columnas = (
        ("A", -1.5, relacion.dominio, 0),
        ("B", 1.5, relacion.codominio, 1),
    )
    for nombre, x, conjunto, i in columnas:
        color = _PALETA[i]
        ax.add_patch(
            Ellipse(
                (x, 0.0),
                1.5,
                filas + 1.2,
                facecolor=_relleno(color, 0.15),
                edgecolor=color,
                linewidth=2,
            )
        )
        ax.text(
            x, (filas + 1.2) / 2 + 0.25, nombre,
            ha="center", va="bottom", fontsize=14, fontweight="bold", color=color,
        )
        for j, elemento in enumerate(conjunto):
            y = (conjunto.cardinal - 1) / 2 - j
            posiciones[(i, elemento)] = (x, y)
    imagen = relacion.imagen()
    for (i, elemento), (x, y) in posiciones.items():
        llena = i == 0 or elemento in imagen
        ax.add_patch(
            Circle(
                (x, y),
                0.09,
                facecolor=_PALETA[i] if llena else "white",
                edgecolor=_PALETA[i],
                linewidth=1.5,
                zorder=3,
            )
        )
        desplazamiento = -0.2 if i == 0 else 0.2
        ax.text(
            x + desplazamiento, y, str(elemento),
            ha="right" if i == 0 else "left", va="center", fontsize=11,
        )
    for a, b in relacion.pares.elementos:
        (xa, ya), (xb, yb) = posiciones[(0, a)], posiciones[(1, b)]
        ax.add_patch(
            FancyArrowPatch(
                (xa + 0.1, ya),
                (xb - 0.1, yb),
                arrowstyle="-|>",
                mutation_scale=14,
                color="#333333",
                linewidth=1.2,
                shrinkA=0,
                shrinkB=0,
                zorder=2,
            )
        )
    ax.set_xlim(-2.9, 2.9)
    ax.set_ylim(-(filas + 1.2) / 2 - 0.3, (filas + 1.2) / 2 + 0.9)
    return ax


def _distribuir_islas(familia: FamiliaDeConjuntos) -> list:
    """Calcula dónde colocar cada bloque de una partición en una cuadrícula sin que se traslapen.

    Entrada: familia (FamiliaDeConjuntos), bloques a distribuir.
    Salida: list, con una tupla (x, y, ancho, alto, columnas) por bloque, donde (x, y) es la esquina inferior izquierda y columnas es el número de elementos por fila dentro de la isla.
    """
    medidas = []
    for bloque in familia:
        columnas = min(max(bloque.cardinal, 1), 3)
        filas = max(ceil(bloque.cardinal / columnas), 1)
        medidas.append((columnas, columnas * 0.9 + 0.5, filas * 0.8 + 0.9))
    ancho_celda = max((m[1] for m in medidas), default=0) + 0.5
    alto_celda = max((m[2] for m in medidas), default=0) + 0.5
    por_fila = max(ceil(sqrt(len(medidas))), 1)
    filas_totales = ceil(len(medidas) / por_fila) if medidas else 0
    islas = []
    for i, (columnas, ancho, alto) in enumerate(medidas):
        fila, columna = divmod(i, por_fila)
        x = columna * ancho_celda + (ancho_celda - ancho) / 2
        y = (filas_totales - 1 - fila) * alto_celda + (alto_celda - alto) / 2
        islas.append((x, y, ancho, alto, columnas))
    return islas


def visualizar_particion(
    particion: Any,
    universo: Optional[Iterable[Any]] = None,
    ax: Optional[Axes] = None,
    titulo: Optional[str] = None,
) -> Axes:
    """Dibuja una partición como islas de colores, una por bloque, con sus elementos dentro.

    Entrada: particion (iterable de iterables, o Relacion de equivalencia), bloques de la partición o relación que los genera; universo (iterable, opcional), conjunto que se particiona, por defecto la unión de los bloques; ax (Axes, opcional), ejes donde dibujar; titulo (str, opcional), título.
    Salida: Axes, los ejes con el dibujo; cada isla se titula [a], con a su menor elemento. Lanza ParticionInvalidaError si no es una partición válida, NoEsEquivalenciaError si recibe una relación que no es de equivalencia, y FamiliaInvalidaError si los datos no son válidos.
    """
    if isinstance(particion, Relacion):
        bloques = generar_particion(particion)
    else:
        familia = _como_familia(particion)
        u = familia.union() if universo is None else como_conjunto(universo)
        bloques = validar_particion(familia, u)
    islas = _distribuir_islas(bloques)
    ax = _preparar_ejes(ax, titulo, (6, 5))
    for i, (bloque, (x, y, ancho, alto, columnas)) in enumerate(zip(bloques, islas)):
        color = _PALETA[i % len(_PALETA)]
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                ancho,
                alto,
                boxstyle="round,pad=0,rounding_size=0.35",
                facecolor=_relleno(color, 0.3),
                edgecolor=color,
                linewidth=2,
            )
        )
        etiqueta = f"[{next(iter(bloque))}]" if not bloque.es_vacio() else "∅"
        ax.text(
            x + ancho / 2, y + alto - 0.35, etiqueta,
            ha="center", va="center", fontsize=12, fontweight="bold", color=color,
        )
        for j, elemento in enumerate(bloque):
            fila, columna = divmod(j, columnas)
            cx = x + (ancho - columnas * 0.9) / 2 + 0.9 * (columna + 0.5)
            cy = y + alto - 0.7 - 0.8 * (fila + 0.5)
            ax.add_patch(
                Circle((cx, cy), 0.3, facecolor="white", edgecolor=color, linewidth=1.5, zorder=3)
            )
            ax.text(cx, cy, str(elemento), ha="center", va="center", fontsize=10, zorder=4)
    if islas:
        ax.set_xlim(-0.3, max(x + ancho for x, _, ancho, _, _ in islas) + 0.3)
        ax.set_ylim(-0.3, max(y + alto for _, y, _, alto, _ in islas) + 0.3)
    return ax


def _medidas_von_neumann(conjunto: Conjunto, memoria: dict) -> tuple:
    """Calcula el ancho y el alto de la caja que dibuja un natural de Von Neumann con todo lo que contiene.

    Entrada: conjunto (Conjunto), natural de Von Neumann; memoria (dict), medidas ya calculadas por conjunto.
    Salida: tuple, (ancho, alto) de la caja, que es la suma de las cajas de sus elementos más márgenes.
    """
    if conjunto in memoria:
        return memoria[conjunto]
    if conjunto.es_vacio():
        medida = (1.0, 1.0)
    else:
        hijos = [_medidas_von_neumann(h, memoria) for h in conjunto]
        ancho = sum(w for w, _ in hijos) + _MARGEN_VON_NEUMANN * (len(hijos) + 1)
        alto = max(h for _, h in hijos) + _MARGEN_VON_NEUMANN + _BANDA_VON_NEUMANN
        medida = (ancho, alto)
    memoria[conjunto] = medida
    return medida


def _colocar_von_neumann(
    conjunto: Conjunto, x: float, y: float, nivel: int, memoria: dict, cajas: list
) -> None:
    """Coloca la caja de un natural y, dentro de ella y de izquierda a derecha, las cajas de sus elementos.

    Entrada: conjunto (Conjunto), natural de Von Neumann; x (float), y (float), esquina inferior izquierda de su caja; nivel (int), profundidad de anidamiento; memoria (dict), medidas ya calculadas; cajas (list), lista donde se agregan las Caja resultantes.
    Salida: None, agrega a cajas una Caja por el conjunto y una por cada conjunto anidado.
    """
    ancho, alto = _medidas_von_neumann(conjunto, memoria)
    cajas.append(Caja(conjunto.cardinal, x, y, ancho, alto, nivel))
    cursor = x + _MARGEN_VON_NEUMANN
    for hijo in conjunto:
        ancho_hijo, _ = _medidas_von_neumann(hijo, memoria)
        _colocar_von_neumann(
            hijo, cursor, y + _MARGEN_VON_NEUMANN, nivel + 1, memoria, cajas
        )
        cursor += ancho_hijo + _MARGEN_VON_NEUMANN


def cajas_von_neumann(n: int) -> list:
    """Calcula las cajas anidadas que representan el natural n de Von Neumann.

    Entrada: n (int), natural a representar (entero entre 0 y LIMITE_VON_NEUMANN).
    Salida: list, de Caja (valor, x, y, ancho, alto, nivel) con una caja por cada aparición de un natural dentro de n, empezando por la caja de n. Lanza NaturalInvalidoError si n no es un natural y ConjuntoDemasiadoGrandeError si n supera LIMITE_VON_NEUMANN.
    """
    validar_natural(n)
    if n > LIMITE_VON_NEUMANN:
        raise ConjuntoDemasiadoGrandeError(
            f"El natural {n} tendría {2 ** n} cajas; el límite es {LIMITE_VON_NEUMANN}."
        )
    cajas = []
    _colocar_von_neumann(numero_von_neumann(n), 0.0, 0.0, 0, {}, cajas)
    return cajas


def arbol_von_neumann(
    n: int, ax: Optional[Axes] = None, titulo: Optional[str] = None
) -> Axes:
    """Dibuja el natural n de Von Neumann como cajas anidadas: cada natural contiene a todos los anteriores.

    Entrada: n (int), natural a dibujar (entero entre 0 y LIMITE_VON_NEUMANN); ax (Axes, opcional), ejes donde dibujar; titulo (str, opcional), título, por defecto el natural dibujado.
    Salida: Axes, los ejes con el dibujo; cada caja lleva el natural que representa y el mismo natural siempre tiene el mismo color. Lanza NaturalInvalidoError si n no es un natural y ConjuntoDemasiadoGrandeError si n supera LIMITE_VON_NEUMANN.
    """
    cajas = cajas_von_neumann(n)
    raiz = cajas[0]
    ancho_figura = min(14.0, max(6.0, raiz.ancho * 0.55))
    alto_figura = min(8.0, max(4.0, raiz.alto * 0.9))
    ax = _preparar_ejes(
        ax, titulo or f"Natural {n} de Von Neumann", (ancho_figura, alto_figura)
    )
    tamano_letra = max(7, 13 - n)
    for caja in cajas:
        color = _PALETA[caja.valor % len(_PALETA)]
        ax.add_patch(
            Rectangle(
                (caja.x, caja.y),
                caja.ancho,
                caja.alto,
                facecolor=_relleno(color, 0.45),
                edgecolor=color,
                linewidth=1.5,
                zorder=caja.nivel,
            )
        )
        ax.text(
            caja.x + caja.ancho / 2 if caja.valor == 0 else caja.x + 0.12,
            caja.y + caja.alto / 2 if caja.valor == 0 else caja.y + caja.alto - 0.08,
            str(caja.valor),
            ha="center" if caja.valor == 0 else "left",
            va="center" if caja.valor == 0 else "top",
            fontsize=tamano_letra,
            fontweight="bold",
            zorder=caja.nivel + 0.5,
        )
    ax.set_xlim(-0.3, raiz.ancho + 0.3)
    ax.set_ylim(-0.3, raiz.alto + 0.3)
    return ax
