from __future__ import annotations

from itertools import combinations
from typing import Any, Iterable, Iterator, Optional

from .conjunto import (
    Conjunto,
    como_conjunto,
    interseccion_generalizada,
    union_generalizada,
)
from .exceptions import ConjuntoInvalidoError, FamiliaInvalidaError
from .utils import validar_natural


class FamiliaDeConjuntos:
    __slots__ = ("_conjuntos",)

    def __init__(self, conjuntos: Iterable[Iterable[Any]] = ()) -> None:
        """Construye una familia indexada de conjuntos que conserva orden y repetidos.

        Entrada: conjuntos (iterable de iterables), miembros de la familia; cada uno se convierte a Conjunto.
        Salida: None, crea la familia. Lanza FamiliaInvalidaError si no es iterable, es una cadena o algún miembro no es válido.
        """
        if isinstance(conjuntos, (str, bytes)):
            raise FamiliaInvalidaError(
                "Una familia no puede construirse desde una cadena."
            )
        try:
            iterador = iter(conjuntos)
        except TypeError:
            raise FamiliaInvalidaError(
                f"Una familia debe ser iterable, se recibió {type(conjuntos).__name__}."
            ) from None
        try:
            miembros = tuple(como_conjunto(c) for c in iterador)
        except ConjuntoInvalidoError as error:
            raise FamiliaInvalidaError(
                f"Un miembro de la familia no es un conjunto válido: {error}"
            ) from error
        object.__setattr__(self, "_conjuntos", miembros)

    def __setattr__(self, nombre: str, valor: Any) -> None:
        """Impide modificar atributos para mantener la familia inmutable.

        Entrada: nombre (str), atributo; valor (Any), valor a asignar.
        Salida: ninguna, siempre lanza AttributeError.
        """
        raise AttributeError("FamiliaDeConjuntos es inmutable.")

    def __delattr__(self, nombre: str) -> None:
        """Impide borrar atributos para mantener la familia inmutable.

        Entrada: nombre (str), atributo a borrar.
        Salida: ninguna, siempre lanza AttributeError.
        """
        raise AttributeError("FamiliaDeConjuntos es inmutable.")

    @property
    def conjuntos(self) -> tuple:
        """Da acceso a los miembros de la familia.

        Entrada: ninguna.
        Salida: tuple, conjuntos de la familia en orden.
        """
        return self._conjuntos

    def __len__(self) -> int:
        """Permite usar len() sobre la familia.

        Entrada: ninguna.
        Salida: int, cantidad de miembros.
        """
        return len(self._conjuntos)

    def __iter__(self) -> Iterator[Conjunto]:
        """Recorre los miembros de la familia en orden.

        Entrada: ninguna.
        Salida: iterador, conjuntos de la familia.
        """
        return iter(self._conjuntos)

    def __getitem__(self, indice: int) -> Conjunto:
        """Obtiene el miembro en una posición.

        Entrada: indice (int), posición del miembro.
        Salida: Conjunto, miembro en esa posición.
        """
        return self._conjuntos[indice]

    def __eq__(self, otro: object) -> bool:
        """Evalúa si dos familias tienen los mismos miembros en el mismo orden.

        Entrada: otro (object), objeto a comparar.
        Salida: bool, True si son iguales; NotImplemented si otro no es FamiliaDeConjuntos.
        """
        if not isinstance(otro, FamiliaDeConjuntos):
            return NotImplemented
        return self._conjuntos == otro._conjuntos

    def __hash__(self) -> int:
        """Calcula el hash de la familia.

        Entrada: ninguna.
        Salida: int, valor hash.
        """
        return hash(self._conjuntos)

    def __repr__(self) -> str:
        """Da una representación que permite reconstruir la familia.

        Entrada: ninguna.
        Salida: str, por ejemplo "FamiliaDeConjuntos([Conjunto([1]), Conjunto([2])])".
        """
        return f"FamiliaDeConjuntos([{', '.join(repr(c) for c in self._conjuntos)}])"

    def __str__(self) -> str:
        """Da la representación matemática de la familia.

        Entrada: ninguna.
        Salida: str, por ejemplo "[{1}, {2, 3}]".
        """
        return "[" + ", ".join(str(c) for c in self._conjuntos) + "]"

    def union(self) -> Conjunto:
        """Calcula la unión generalizada de la familia.

        Entrada: ninguna.
        Salida: Conjunto, unión de todos los miembros; ∅ si la familia es vacía.
        """
        return union_generalizada(self._conjuntos)

    def interseccion(self, universo: Optional[Iterable[Any]] = None) -> Conjunto:
        """Calcula la intersección generalizada de la familia.

        Entrada: universo (iterable, opcional), solo se usa si la familia es vacía.
        Salida: Conjunto, intersección de todos los miembros. Lanza FamiliaVaciaError si la familia es vacía y no hay universo.
        """
        return interseccion_generalizada(self._conjuntos, universo)

    def es_disjunta_dos_a_dos(self) -> bool:
        """Evalúa si todo par de miembros en posiciones distintas es disjunto.

        Entrada: ninguna.
        Salida: bool, True si ningún par de miembros comparte elementos.
        """
        return all(a.es_disjunto(b) for a, b in combinations(self._conjuntos, 2))

    def recubre(self, universo: Iterable[Any]) -> bool:
        """Evalúa si la familia cubre un universo, es decir U ⊆ ⋃ Aᵢ.

        Entrada: universo (iterable), conjunto U a cubrir.
        Salida: bool, True si todo elemento de U está en algún miembro.
        """
        return como_conjunto(universo).es_subconjunto(self.union())

    def es_particion_de(self, universo: Iterable[Any]) -> bool:
        """Evalúa si la familia es una partición de un universo.

        Entrada: universo (iterable), conjunto U a particionar.
        Salida: bool, True si los miembros son no vacíos, disjuntos dos a dos y su unión es U.
        """
        return (
            all(not c.es_vacio() for c in self._conjuntos)
            and self.es_disjunta_dos_a_dos()
            and self.union() == como_conjunto(universo)
        )


def sucesor(conjunto: Iterable[Any]) -> Conjunto:
    """Calcula el sucesor S(x) = x ∪ {x}.

    Entrada: conjunto (iterable), conjunto x.
    Salida: Conjunto, x ∪ {x}.
    """
    x = como_conjunto(conjunto)
    return x.union(Conjunto([x]))


def numero_von_neumann(n: int) -> Conjunto:
    """Construye el natural n como conjunto, con 0 = ∅ y n+1 = S(n).

    Entrada: n (int), natural a construir (entero >= 0).
    Salida: Conjunto, natural n de Von Neumann con n elementos. Lanza NaturalInvalidoError si n no es un entero >= 0.
    """
    validar_natural(n)
    actual = Conjunto()
    for _ in range(n):
        actual = sucesor(actual)
    return actual


def naturales_von_neumann(n: int) -> FamiliaDeConjuntos:
    """Construye los naturales 0, 1, ..., n de Von Neumann (n inclusive).

    Entrada: n (int), último natural a construir (entero >= 0); para imprimir o graficar conviene n <= 10.
    Salida: FamiliaDeConjuntos, con los n+1 naturales en orden. Lanza NaturalInvalidoError si n no es un entero >= 0.
    """
    validar_natural(n)
    actual = Conjunto()
    lista = [actual]
    for _ in range(n):
        actual = sucesor(actual)
        lista.append(actual)
    return FamiliaDeConjuntos(lista)


def es_natural_von_neumann(conjunto: Iterable[Any]) -> bool:
    """Evalúa si un conjunto es exactamente el natural |x| de Von Neumann.

    Entrada: conjunto (iterable), conjunto x a verificar.
    Salida: bool, True si x = {0, 1, ..., |x| − 1}.
    """
    x = como_conjunto(conjunto)
    return x == numero_von_neumann(x.cardinal)
