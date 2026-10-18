from __future__ import annotations

from itertools import combinations, product
from typing import Any, Iterable, Iterator, Optional

from .exceptions import (
    ConjuntoDemasiadoGrandeError,
    FamiliaVaciaError,
    OperacionInvalidaError,
    UniversoInvalidoError,
)
from .utils import a_frozenset

LIMITE_POTENCIA = 20


def _ordenar(elementos: Iterable[Any]) -> list:
    """Ordena elementos de forma determinista para iterar e imprimir.

    Entrada: elementos (iterable), elementos a ordenar (admite tipos mezclados y conjuntos anidados).
    Salida: list, elementos en orden natural o, si no existe, ordenados por (tipo, tamaño, repr).
    """
    elementos = list(elementos)
    try:
        if any(isinstance(e, (Conjunto, frozenset)) for e in elementos):
            raise TypeError
        return sorted(elementos)
    except TypeError:
        return sorted(
            elementos,
            key=lambda e: (
                type(e).__name__,
                len(e) if isinstance(e, (Conjunto, frozenset)) else 0,
                repr(e),
            ),
        )


class Conjunto:
    __slots__ = ("_elementos",)

    def __init__(self, elementos: Iterable[Any] = ()) -> None:
        """Construye un conjunto finito, inmutable y hashable.

        Entrada: elementos (iterable), elementos del conjunto; los repetidos se ignoran (no cadenas, no elementos no hashables).
        Salida: None, crea el Conjunto. Lanza ConjuntoInvalidoError o ElementoNoHashableError si los datos no son válidos.
        """
        object.__setattr__(self, "_elementos", a_frozenset(elementos))

    def __setattr__(self, nombre: str, valor: Any) -> None:
        """Impide modificar atributos para mantener el conjunto inmutable.

        Entrada: nombre (str), atributo; valor (Any), valor a asignar.
        Salida: ninguna, siempre lanza AttributeError.
        """
        raise AttributeError("Conjunto es inmutable.")

    def __delattr__(self, nombre: str) -> None:
        """Impide borrar atributos para mantener el conjunto inmutable.

        Entrada: nombre (str), atributo a borrar.
        Salida: ninguna, siempre lanza AttributeError.
        """
        raise AttributeError("Conjunto es inmutable.")

    @property
    def elementos(self) -> frozenset:
        """Da acceso al frozenset subyacente.

        Entrada: ninguna.
        Salida: frozenset, elementos del conjunto.
        """
        return self._elementos

    @property
    def cardinal(self) -> int:
        """Calcula el número de elementos |A|.

        Entrada: ninguna.
        Salida: int, cantidad de elementos.
        """
        return len(self._elementos)

    def es_vacio(self) -> bool:
        """Indica si el conjunto es el conjunto vacío.

        Entrada: ninguna.
        Salida: bool, True si no tiene elementos.
        """
        return not self._elementos

    def __len__(self) -> int:
        """Permite usar len() sobre el conjunto.

        Entrada: ninguna.
        Salida: int, cantidad de elementos.
        """
        return len(self._elementos)

    def __iter__(self) -> Iterator[Any]:
        """Recorre los elementos en orden determinista.

        Entrada: ninguna.
        Salida: iterador, elementos ordenados.
        """
        return iter(_ordenar(self._elementos))

    def __contains__(self, elemento: Any) -> bool:
        """Evalúa la pertenencia a ∈ A; un objeto no hashable nunca es elemento.

        Entrada: elemento (Any), objeto a buscar.
        Salida: bool, True si el elemento pertenece al conjunto.
        """
        try:
            return elemento in self._elementos
        except TypeError:
            return False

    def __eq__(self, otro: object) -> bool:
        """Evalúa la igualdad de conjuntos A = B.

        Entrada: otro (object), objeto a comparar (solo se compara con otro Conjunto).
        Salida: bool, True si tienen los mismos elementos; NotImplemented si otro no es Conjunto.
        """
        if not isinstance(otro, Conjunto):
            return NotImplemented
        return self._elementos == otro._elementos

    def __hash__(self) -> int:
        """Calcula el hash para poder usar el conjunto como elemento de otro.

        Entrada: ninguna.
        Salida: int, valor hash.
        """
        return hash(self._elementos)

    def __str__(self) -> str:
        """Da la representación matemática del conjunto, con ∅ para el vacío.

        Entrada: ninguna.
        Salida: str, por ejemplo "{1, 2, 3}" o "∅".
        """
        if not self._elementos:
            return "∅"
        interior = ", ".join(
            str(e) if isinstance(e, Conjunto) else repr(e)
            for e in _ordenar(self._elementos)
        )
        return "{" + interior + "}"

    def __repr__(self) -> str:
        """Da una representación que permite reconstruir el conjunto.

        Entrada: ninguna.
        Salida: str, por ejemplo "Conjunto([1, 2, 3])".
        """
        interior = ", ".join(repr(e) for e in _ordenar(self._elementos))
        return f"Conjunto([{interior}])"

    def es_subconjunto(self, otro: Iterable[Any]) -> bool:
        """Evalúa si A ⊆ B.

        Entrada: otro (iterable), conjunto B.
        Salida: bool, True si todo elemento de A está en B.
        """
        return self._elementos <= como_conjunto(otro)._elementos

    def es_subconjunto_propio(self, otro: Iterable[Any]) -> bool:
        """Evalúa si A ⊂ B (subconjunto y distinto).

        Entrada: otro (iterable), conjunto B.
        Salida: bool, True si A ⊆ B y A ≠ B.
        """
        return self._elementos < como_conjunto(otro)._elementos

    def es_disjunto(self, otro: Iterable[Any]) -> bool:
        """Evalúa si A ∩ B = ∅.

        Entrada: otro (iterable), conjunto B.
        Salida: bool, True si no comparten elementos.
        """
        return self._elementos.isdisjoint(como_conjunto(otro)._elementos)

    def __le__(self, otro: Iterable[Any]) -> bool:
        """Operador A <= B, equivale a A ⊆ B.

        Entrada: otro (iterable), conjunto B.
        Salida: bool, resultado de es_subconjunto.
        """
        return self.es_subconjunto(otro)

    def __lt__(self, otro: Iterable[Any]) -> bool:
        """Operador A < B, equivale a A ⊂ B.

        Entrada: otro (iterable), conjunto B.
        Salida: bool, resultado de es_subconjunto_propio.
        """
        return self.es_subconjunto_propio(otro)

    def __ge__(self, otro: Iterable[Any]) -> bool:
        """Operador A >= B, equivale a B ⊆ A.

        Entrada: otro (iterable), conjunto B.
        Salida: bool, True si B es subconjunto de A.
        """
        return como_conjunto(otro).es_subconjunto(self)

    def __gt__(self, otro: Iterable[Any]) -> bool:
        """Operador A > B, equivale a B ⊂ A.

        Entrada: otro (iterable), conjunto B.
        Salida: bool, True si B es subconjunto propio de A.
        """
        return como_conjunto(otro).es_subconjunto_propio(self)

    def union(self, *otros: Iterable[Any]) -> "Conjunto":
        """Calcula A ∪ B ∪ ... con uno o varios conjuntos.

        Entrada: otros (iterables), conjuntos a unir con A.
        Salida: Conjunto, unión de todos.
        """
        return union_generalizada([self, *otros])

    def interseccion(self, *otros: Iterable[Any]) -> "Conjunto":
        """Calcula A ∩ B ∩ ... con uno o varios conjuntos.

        Entrada: otros (iterables), conjuntos a intersectar con A.
        Salida: Conjunto, intersección de todos.
        """
        return interseccion_generalizada([self, *otros])

    def diferencia(self, otro: Iterable[Any]) -> "Conjunto":
        """Calcula A − B.

        Entrada: otro (iterable), conjunto B.
        Salida: Conjunto, elementos de A que no están en B.
        """
        return Conjunto(self._elementos - como_conjunto(otro)._elementos)

    def diferencia_simetrica(self, otro: Iterable[Any]) -> "Conjunto":
        """Calcula A △ B.

        Entrada: otro (iterable), conjunto B.
        Salida: Conjunto, elementos que están en exactamente uno de los dos.
        """
        return Conjunto(self._elementos ^ como_conjunto(otro)._elementos)

    def complemento(self, universo: Iterable[Any]) -> "Conjunto":
        """Calcula el complemento de A respecto a un universo U.

        Entrada: universo (iterable), conjunto U que contiene a A.
        Salida: Conjunto, U − A. Lanza UniversoInvalidoError si A no está contenido en U.
        """
        u = como_conjunto(universo)
        if not self.es_subconjunto(u):
            raise UniversoInvalidoError(
                f"{self} no está contenido en el universo {u}; "
                "el complemento no está definido."
            )
        return u.diferencia(self)

    def __or__(self, otro: Iterable[Any]) -> "Conjunto":
        """Operador A | B, equivale a la unión.

        Entrada: otro (iterable), conjunto B.
        Salida: Conjunto, A ∪ B.
        """
        return self.union(otro)

    def __and__(self, otro: Iterable[Any]) -> "Conjunto":
        """Operador A & B, equivale a la intersección.

        Entrada: otro (iterable), conjunto B.
        Salida: Conjunto, A ∩ B.
        """
        return self.interseccion(otro)

    def __sub__(self, otro: Iterable[Any]) -> "Conjunto":
        """Operador A - B, equivale a la diferencia.

        Entrada: otro (iterable), conjunto B.
        Salida: Conjunto, A − B.
        """
        return self.diferencia(otro)

    def __xor__(self, otro: Iterable[Any]) -> "Conjunto":
        """Operador A ^ B, equivale a la diferencia simétrica.

        Entrada: otro (iterable), conjunto B.
        Salida: Conjunto, A △ B.
        """
        return self.diferencia_simetrica(otro)

    def __mul__(self, otro: Iterable[Any]) -> "Conjunto":
        """Operador A * B, equivale al producto cartesiano.

        Entrada: otro (iterable), conjunto B.
        Salida: Conjunto, A × B como conjunto de tuplas.
        """
        return producto_cartesiano(self, otro)

    def conjunto_potencia(self) -> "Conjunto":
        """Calcula P(A), el conjunto de todos los subconjuntos de A.

        Entrada: ninguna.
        Salida: Conjunto, de conjuntos, con 2^|A| elementos. Lanza ConjuntoDemasiadoGrandeError si |A| supera LIMITE_POTENCIA.
        """
        n = self.cardinal
        if n > LIMITE_POTENCIA:
            raise ConjuntoDemasiadoGrandeError(
                f"P(A) tendría 2^{n} elementos; el límite es 2^{LIMITE_POTENCIA}."
            )
        base = list(self)
        return Conjunto(
            Conjunto(sub) for r in range(n + 1) for sub in combinations(base, r)
        )


def como_conjunto(objeto: Iterable[Any]) -> Conjunto:
    """Convierte un iterable en Conjunto; es la única puerta de validación de datos.

    Entrada: objeto (iterable), datos a convertir (si ya es Conjunto se devuelve igual).
    Salida: Conjunto, equivalente al objeto recibido.
    """
    if isinstance(objeto, Conjunto):
        return objeto
    return Conjunto(objeto)


def union_generalizada(conjuntos: Iterable[Iterable[Any]]) -> Conjunto:
    """Calcula la unión de una colección de conjuntos.

    Entrada: conjuntos (iterable de iterables), colección de conjuntos a unir.
    Salida: Conjunto, unión de todos; la unión de una colección vacía es ∅.
    """
    lista = [como_conjunto(c)._elementos for c in conjuntos]
    return Conjunto(frozenset().union(*lista))


def interseccion_generalizada(
    conjuntos: Iterable[Iterable[Any]], universo: Optional[Iterable[Any]] = None
) -> Conjunto:
    """Calcula la intersección de una colección de conjuntos.

    Entrada: conjuntos (iterable de iterables), colección a intersectar; universo (iterable, opcional), solo se usa si la colección está vacía.
    Salida: Conjunto, intersección de todos (el universo si la colección está vacía). Lanza FamiliaVaciaError si está vacía y no hay universo.
    """
    lista = [como_conjunto(c)._elementos for c in conjuntos]
    if not lista:
        if universo is None:
            raise FamiliaVaciaError(
                "La intersección de una familia vacía no está definida; "
                "indica un universo."
            )
        return como_conjunto(universo)
    return Conjunto(lista[0].intersection(*lista[1:]))


def producto_cartesiano(*conjuntos: Iterable[Any]) -> Conjunto:
    """Calcula el producto cartesiano A₁ × A₂ × ... × Aₙ.

    Entrada: conjuntos (iterables), uno o más conjuntos a multiplicar.
    Salida: Conjunto, de tuplas con un elemento de cada conjunto. Lanza OperacionInvalidaError si no se recibe ninguno.
    """
    if not conjuntos:
        raise OperacionInvalidaError(
            "El producto cartesiano necesita al menos un conjunto."
        )
    listas = [list(como_conjunto(c)) for c in conjuntos]
    return Conjunto(product(*listas))
