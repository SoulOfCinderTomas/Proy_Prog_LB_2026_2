from __future__ import annotations

from typing import Any, Iterable

from .exceptions import (
    ConjuntoInvalidoError,
    ElementoNoHashableError,
    NaturalInvalidoError,
)


def es_hashable(objeto: Any) -> bool:
    """Indica si un objeto puede ser elemento de un conjunto.

    Entrada: objeto (Any), cualquier objeto de Python.
    Salida: bool, True si el objeto es hashable y False en caso contrario.
    """
    try:
        hash(objeto)
    except TypeError:
        return False
    return True


def a_frozenset(elementos: Iterable[Any], nombre: str = "elementos") -> frozenset:
    """Valida un iterable y lo convierte en frozenset sin repetidos.

    Entrada: elementos (iterable), datos a convertir (no cadenas); nombre (str), nombre del argumento para los mensajes de error.
    Salida: frozenset, elementos sin repetir. Lanza ConjuntoInvalidoError si no es iterable o es cadena, y ElementoNoHashableError si hay elementos no hashables.
    """
    if isinstance(elementos, (str, bytes)):
        raise ConjuntoInvalidoError(
            f"'{nombre}' no puede ser una cadena; usa una lista, p. ej. ['abc']."
        )
    try:
        iterador = iter(elementos)
    except TypeError:
        raise ConjuntoInvalidoError(
            f"'{nombre}' debe ser iterable, se recibió {type(elementos).__name__}."
        ) from None
    try:
        return frozenset(iterador)
    except TypeError as error:
        raise ElementoNoHashableError(
            f"'{nombre}' contiene un elemento no hashable: {error}"
        ) from error


def validar_natural(valor: Any, nombre: str = "n") -> int:
    """Valida que un valor sea un entero mayor o igual que cero.

    Entrada: valor (Any), valor a validar (bool se rechaza); nombre (str), nombre del argumento para el mensaje de error.
    Salida: int, el mismo valor ya validado. Lanza NaturalInvalidoError si no es entero o es negativo.
    """
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
        raise NaturalInvalidoError(
            f"'{nombre}' debe ser un natural (entero >= 0), se recibió {valor!r}."
        )
    return valor
