from __future__ import annotations

from itertools import combinations
from typing import Any, Iterable

from .conjunto import (
    Conjunto,
    como_conjunto,
    producto_cartesiano,
    union_generalizada,
)
from .exceptions import NoEsEquivalenciaError, ParticionInvalidaError
from .familia import FamiliaDeConjuntos
from .relacion import Relacion, validar_relacion


def validar_equivalencia(relacion: Relacion) -> Relacion:
    """Verifica que una relación sea de equivalencia (reflexiva, simétrica y transitiva).

    Entrada: relacion (Relacion), relación sobre un conjunto A.
    Salida: Relacion, la misma relación recibida. Lanza RelacionInvalidaError si no es una Relacion, RelacionNoHomogeneaError si dominio y codominio difieren, y NoEsEquivalenciaError (indicando qué propiedades faltan) si no es de equivalencia.
    """
    validar_relacion(relacion)
    if not relacion.es_relacion_equivalencia():
        propiedades = (
            ("reflexiva", relacion.es_reflexiva()),
            ("simétrica", relacion.es_simetrica()),
            ("transitiva", relacion.es_transitiva()),
        )
        faltantes = ", ".join(nombre for nombre, cumple in propiedades if not cumple)
        raise NoEsEquivalenciaError(
            f"La relación no es de equivalencia: no es {faltantes}."
        )
    return relacion


def clase_de(relacion: Relacion, elemento: Any) -> Conjunto:
    """Calcula la clase de equivalencia [a] = {x ∈ A | a R x}.

    Entrada: relacion (Relacion), relación de equivalencia sobre A; elemento (Any), elemento a de A.
    Salida: Conjunto, la clase de a. Lanza NoEsEquivalenciaError si la relación no es de equivalencia y FueraDeDominioError si a no está en A.
    """
    validar_equivalencia(relacion)
    return relacion.imagenes(elemento)


def generar_particion(relacion: Relacion) -> FamiliaDeConjuntos:
    """Calcula la partición A/R formada por todas las clases de equivalencia distintas.

    Entrada: relacion (Relacion), relación de equivalencia sobre A.
    Salida: FamiliaDeConjuntos, con una clase por bloque, ordenadas por su menor representante. Lanza NoEsEquivalenciaError si la relación no es de equivalencia.
    """
    validar_equivalencia(relacion)
    clases = []
    cubiertos = set()
    for a in relacion.dominio:
        if a not in cubiertos:
            clase = relacion.imagenes(a)
            clases.append(clase)
            cubiertos.update(clase.elementos)
    return FamiliaDeConjuntos(clases)


def validar_particion(
    familia: Iterable[Iterable[Any]], universo: Iterable[Any]
) -> FamiliaDeConjuntos:
    """Verifica que una familia sea una partición de un universo y explica por qué falla si no lo es.

    Entrada: familia (iterable de iterables), bloques candidatos; universo (iterable), conjunto U a particionar.
    Salida: FamiliaDeConjuntos, la familia ya validada. Lanza FamiliaInvalidaError si los datos no forman una familia, y ParticionInvalidaError si hay un bloque vacío, dos bloques que se traslapan, elementos de U sin cubrir o elementos fuera de U.
    """
    bloques = (
        familia if isinstance(familia, FamiliaDeConjuntos) else FamiliaDeConjuntos(familia)
    )
    u = como_conjunto(universo)
    if bloques.es_particion_de(u):
        return bloques
    for posicion, bloque in enumerate(bloques):
        if bloque.es_vacio():
            raise ParticionInvalidaError(
                f"No es una partición: el bloque en la posición {posicion} es vacío."
            )
    for a, b in combinations(bloques, 2):
        comunes = a.interseccion(b)
        if not comunes.es_vacio():
            raise ParticionInvalidaError(
                f"No es una partición: los bloques {a} y {b} se traslapan en {comunes}."
            )
    sin_cubrir = u.diferencia(bloques.union())
    if not sin_cubrir.es_vacio():
        raise ParticionInvalidaError(
            f"No es una partición de {u}: faltan por cubrir {sin_cubrir}."
        )
    sobrantes = bloques.union().diferencia(u)
    raise ParticionInvalidaError(
        f"No es una partición de {u}: hay elementos fuera del universo {sobrantes}."
    )


def relacion_desde_particion(
    particion: Iterable[Iterable[Any]], universo: Iterable[Any]
) -> Relacion:
    """Construye la relación de equivalencia inducida por una partición: a ~ b si están en el mismo bloque.

    Entrada: particion (iterable de iterables), bloques de la partición; universo (iterable), conjunto U que particiona.
    Salida: Relacion, sobre U, igual a la unión de B × B para cada bloque B. Lanza FamiliaInvalidaError o ParticionInvalidaError si no es una partición válida de U.
    """
    bloques = validar_particion(particion, universo)
    u = como_conjunto(universo)
    pares = union_generalizada(producto_cartesiano(b, b) for b in bloques)
    return Relacion(pares, u, u)
