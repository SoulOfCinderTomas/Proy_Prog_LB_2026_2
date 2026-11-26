from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator, Optional

from .conjunto import Conjunto, como_conjunto
from .exceptions import (
    ComposicionInvalidaError,
    ConjuntoInvalidoError,
    FueraDeDominioError,
    OperacionInvalidaError,
    RelacionInvalidaError,
    RelacionNoHomogeneaError,
)


def validar_pares(
    pares: Iterable[Any], dominio: Conjunto, codominio: Conjunto
) -> Conjunto:
    """Valida que una colección sea un conjunto de pares ordenados de dominio × codominio.

    Entrada: pares (iterable), pares (a, b) a validar; dominio (Conjunto), conjunto de las primeras componentes; codominio (Conjunto), conjunto de las segundas componentes.
    Salida: Conjunto, de tuplas ya validadas. Lanza RelacionInvalidaError si no son pares, si no son hashables o si alguna componente cae fuera de dominio o codominio.
    """
    try:
        conjunto_pares = como_conjunto(pares)
    except ConjuntoInvalidoError as error:
        raise RelacionInvalidaError(f"Los pares no son válidos: {error}") from error
    for par in conjunto_pares:
        if not isinstance(par, tuple) or len(par) != 2:
            raise RelacionInvalidaError(
                f"{par!r} no es un par ordenado (tupla de 2 elementos)."
            )
        a, b = par
        if a not in dominio:
            raise RelacionInvalidaError(
                f"En el par {par!r}, {a!r} no pertenece al dominio {dominio}."
            )
        if b not in codominio:
            raise RelacionInvalidaError(
                f"En el par {par!r}, {b!r} no pertenece al codominio {codominio}."
            )
    return conjunto_pares


def warshall(matriz: list) -> list:
    """Calcula la cerradura transitiva de una matriz booleana con el algoritmo de Warshall.

    Entrada: matriz (list de listas de bool), matriz de adyacencia cuadrada n × n.
    Salida: list, nueva matriz n × n donde [i][j] es True si existe un camino de i a j; la matriz de entrada no se modifica. Lanza OperacionInvalidaError si no es cuadrada.
    """
    n = len(matriz)
    if any(len(fila) != n for fila in matriz):
        raise OperacionInvalidaError("Warshall requiere una matriz cuadrada.")
    cierre = [[bool(valor) for valor in fila] for fila in matriz]
    for k in range(n):
        for i in range(n):
            if cierre[i][k]:
                for j in range(n):
                    if cierre[k][j]:
                        cierre[i][j] = True
    return cierre


class Relacion:
    __slots__ = ("_dominio", "_codominio", "_pares", "_tabla")

    def __init__(
        self,
        pares: Iterable[Any],
        dominio: Iterable[Any],
        codominio: Optional[Iterable[Any]] = None,
    ) -> None:
        """Construye una relación binaria R ⊆ A × B, inmutable y hashable.

        Entrada: pares (iterable), pares ordenados (a, b); dominio (iterable), conjunto A; codominio (iterable, opcional), conjunto B, que por defecto es A (relación sobre un conjunto).
        Salida: None, crea la Relacion. Lanza RelacionInvalidaError si los pares no son válidos o salen de A × B, y ConjuntoInvalidoError si dominio o codominio no son conjuntos válidos.
        """
        dom = como_conjunto(dominio)
        cod = dom if codominio is None else como_conjunto(codominio)
        conjunto_pares = validar_pares(pares, dom, cod)
        grupos: dict = {}
        for a, b in conjunto_pares.elementos:
            grupos.setdefault(a, set()).add(b)
        object.__setattr__(self, "_dominio", dom)
        object.__setattr__(self, "_codominio", cod)
        object.__setattr__(self, "_pares", conjunto_pares)
        object.__setattr__(
            self, "_tabla", {a: frozenset(bs) for a, bs in grupos.items()}
        )

    @classmethod
    def desde_predicado(
        cls,
        dominio: Iterable[Any],
        predicado: Callable[[Any, Any], bool],
        codominio: Optional[Iterable[Any]] = None,
    ) -> "Relacion":
        """Construye la relación formada por los pares (a, b) que cumplen un predicado.

        Entrada: dominio (iterable), conjunto A; predicado (callable), función (a, b) -> bool; codominio (iterable, opcional), conjunto B, que por defecto es A.
        Salida: Relacion, con todos los (a, b) de A × B donde predicado(a, b) es verdadero. Lanza RelacionInvalidaError si predicado no es invocable.
        """
        if not callable(predicado):
            raise RelacionInvalidaError("El predicado debe ser invocable.")
        dom = como_conjunto(dominio)
        cod = dom if codominio is None else como_conjunto(codominio)
        pares = [(a, b) for a in dom for b in cod if predicado(a, b)]
        return cls(pares, dom, cod)

    @classmethod
    def desde_matriz(
        cls,
        matriz: list,
        dominio: Iterable[Any],
        codominio: Optional[Iterable[Any]] = None,
    ) -> "Relacion":
        """Construye una relación a partir de su matriz booleana.

        Entrada: matriz (list de listas de bool), con una fila por elemento del dominio y una columna por elemento del codominio, ambos en orden ascendente; dominio (iterable), conjunto A; codominio (iterable, opcional), conjunto B, que por defecto es A.
        Salida: Relacion, con el par (aᵢ, bⱼ) cuando matriz[i][j] es verdadero. Lanza RelacionInvalidaError si las dimensiones no coinciden.
        """
        dom = como_conjunto(dominio)
        cod = dom if codominio is None else como_conjunto(codominio)
        filas, columnas = list(dom), list(cod)
        if (
            not isinstance(matriz, (list, tuple))
            or len(matriz) != len(filas)
            or any(
                not isinstance(fila, (list, tuple)) or len(fila) != len(columnas)
                for fila in matriz
            )
        ):
            raise RelacionInvalidaError(
                f"La matriz debe ser de {len(filas)} filas por {len(columnas)} columnas."
            )
        pares = [
            (filas[i], columnas[j])
            for i, fila in enumerate(matriz)
            for j, valor in enumerate(fila)
            if valor
        ]
        return cls(pares, dom, cod)

    @property
    def dominio(self) -> Conjunto:
        """Da acceso al dominio A de la relación.

        Entrada: ninguna.
        Salida: Conjunto, conjunto A.
        """
        return self._dominio

    @property
    def codominio(self) -> Conjunto:
        """Da acceso al codominio B de la relación.

        Entrada: ninguna.
        Salida: Conjunto, conjunto B.
        """
        return self._codominio

    @property
    def pares(self) -> Conjunto:
        """Da acceso a los pares ordenados de la relación.

        Entrada: ninguna.
        Salida: Conjunto, de tuplas (a, b).
        """
        return self._pares

    def __setattr__(self, nombre: str, valor: Any) -> None:
        """Impide modificar atributos para mantener la relación inmutable.

        Entrada: nombre (str), atributo; valor (Any), valor a asignar.
        Salida: ninguna, siempre lanza AttributeError.
        """
        raise AttributeError(f"{type(self).__name__} es inmutable.")

    def __delattr__(self, nombre: str) -> None:
        """Impide borrar atributos para mantener la relación inmutable.

        Entrada: nombre (str), atributo a borrar.
        Salida: ninguna, siempre lanza AttributeError.
        """
        raise AttributeError(f"{type(self).__name__} es inmutable.")

    def __len__(self) -> int:
        """Permite usar len() sobre la relación.

        Entrada: ninguna.
        Salida: int, cantidad de pares.
        """
        return self._pares.cardinal

    def __iter__(self) -> Iterator[tuple]:
        """Recorre los pares en orden determinista.

        Entrada: ninguna.
        Salida: iterador, pares (a, b) ordenados.
        """
        return iter(self._pares)

    def __contains__(self, par: Any) -> bool:
        """Evalúa si (a, b) ∈ R.

        Entrada: par (Any), objeto a buscar, normalmente una tupla (a, b).
        Salida: bool, True si el par pertenece a la relación.
        """
        return par in self._pares

    def __eq__(self, otro: object) -> bool:
        """Evalúa la igualdad de relaciones: mismo dominio, mismo codominio y mismos pares.

        Entrada: otro (object), objeto a comparar.
        Salida: bool, True si son iguales; NotImplemented si otro no es una Relacion.
        """
        if not isinstance(otro, Relacion):
            return NotImplemented
        return (
            self._dominio == otro._dominio
            and self._codominio == otro._codominio
            and self._pares == otro._pares
        )

    def __hash__(self) -> int:
        """Calcula el hash de la relación.

        Entrada: ninguna.
        Salida: int, valor hash.
        """
        return hash((self._dominio, self._codominio, self._pares))

    def __str__(self) -> str:
        """Da la representación matemática de la relación como conjunto de pares.

        Entrada: ninguna.
        Salida: str, por ejemplo "{(1, 2), (2, 3)}".
        """
        return str(self._pares)

    def __repr__(self) -> str:
        """Da una representación que permite reconstruir la relación.

        Entrada: ninguna.
        Salida: str, por ejemplo "Relacion([(1, 2)], dominio=Conjunto([1, 2]), codominio=Conjunto([1, 2]))".
        """
        return (
            f"{type(self).__name__}({list(self._pares)!r}, "
            f"dominio={self._dominio!r}, codominio={self._codominio!r})"
        )

    def imagenes(self, elemento: Any) -> Conjunto:
        """Calcula los elementos b tales que (a, b) ∈ R.

        Entrada: elemento (Any), elemento a del dominio.
        Salida: Conjunto, de los b relacionados con a (puede ser vacío). Lanza FueraDeDominioError si a no está en el dominio.
        """
        if elemento not in self._dominio:
            raise FueraDeDominioError(
                f"{elemento!r} no pertenece al dominio {self._dominio}."
            )
        return Conjunto(self._tabla.get(elemento, ()))

    def imagen(self) -> Conjunto:
        """Calcula el conjunto de segundas componentes que realmente aparecen en R.

        Entrada: ninguna.
        Salida: Conjunto, subconjunto del codominio.
        """
        return Conjunto(b for _, b in self._pares.elementos)

    def _exigir_homogenea(self) -> None:
        """Verifica que la relación sea sobre un solo conjunto (dominio igual a codominio).

        Entrada: ninguna.
        Salida: None. Lanza RelacionNoHomogeneaError si dominio y codominio son distintos.
        """
        if self._dominio != self._codominio:
            raise RelacionNoHomogeneaError(
                "Esta operación requiere una relación sobre un solo conjunto: "
                f"dominio {self._dominio} y codominio {self._codominio} son distintos."
            )

    def es_reflexiva(self) -> bool:
        """Evalúa si ∀a ∈ A: (a, a) ∈ R.

        Entrada: ninguna.
        Salida: bool, True si todo elemento se relaciona consigo mismo. Lanza RelacionNoHomogeneaError si dominio y codominio difieren.
        """
        self._exigir_homogenea()
        pares = self._pares.elementos
        return all((a, a) in pares for a in self._dominio.elementos)

    def es_simetrica(self) -> bool:
        """Evalúa si (a, b) ∈ R implica (b, a) ∈ R.

        Entrada: ninguna.
        Salida: bool, True si R es igual a su relación inversa. Lanza RelacionNoHomogeneaError si dominio y codominio difieren.
        """
        self._exigir_homogenea()
        return self._pares == self.inversa()._pares

    def es_antisimetrica(self) -> bool:
        """Evalúa si (a, b) ∈ R y (b, a) ∈ R implican a = b.

        Entrada: ninguna.
        Salida: bool, True si no hay idas y vueltas entre elementos distintos. Lanza RelacionNoHomogeneaError si dominio y codominio difieren.
        """
        self._exigir_homogenea()
        pares = self._pares.elementos
        return all(a == b for a, b in pares if (b, a) in pares)

    def es_transitiva(self) -> bool:
        """Evalúa si (a, b) ∈ R y (b, c) ∈ R implican (a, c) ∈ R.

        Entrada: ninguna.
        Salida: bool, True si R ∘ R ⊆ R. Lanza RelacionNoHomogeneaError si dominio y codominio difieren.
        """
        self._exigir_homogenea()
        return self.composicion(self)._pares.es_subconjunto(self._pares)

    def es_relacion_orden(self) -> bool:
        """Evalúa si R es una relación de orden parcial.

        Entrada: ninguna.
        Salida: bool, True si es reflexiva, antisimétrica y transitiva. Lanza RelacionNoHomogeneaError si dominio y codominio difieren.
        """
        return self.es_reflexiva() and self.es_antisimetrica() and self.es_transitiva()

    def es_relacion_equivalencia(self) -> bool:
        """Evalúa si R es una relación de equivalencia.

        Entrada: ninguna.
        Salida: bool, True si es reflexiva, simétrica y transitiva. Lanza RelacionNoHomogeneaError si dominio y codominio difieren.
        """
        return self.es_reflexiva() and self.es_simetrica() and self.es_transitiva()

    def _conflictos_de_funcion(self) -> list:
        """Busca los elementos del dominio que no tienen exactamente una imagen.

        Entrada: ninguna.
        Salida: list, elementos del dominio con cero o varias imágenes, en orden ascendente.
        """
        return [a for a in self._dominio if len(self._tabla.get(a, ())) != 1]

    def es_funcion(self) -> bool:
        """Evalúa si R es una función de A en B: cada a ∈ A tiene exactamente un b con (a, b) ∈ R.

        Entrada: ninguna.
        Salida: bool, True si todo elemento del dominio tiene una única imagen.
        """
        return not self._conflictos_de_funcion()

    def inversa(self) -> "Relacion":
        """Calcula la relación inversa R⁻¹ = {(b, a) | (a, b) ∈ R}, que siempre existe.

        Entrada: ninguna.
        Salida: Relacion, de B en A con los pares invertidos.
        """
        return Relacion(
            ((b, a) for a, b in self._pares.elementos),
            self._codominio,
            self._dominio,
        )

    def composicion(self, anterior: "Relacion") -> "Relacion":
        """Calcula la composición S ∘ R, donde S es esta relación y R es la que se aplica primero.

        Entrada: anterior (Relacion), relación R de A en B, cuyo codominio debe estar contenido en el dominio de S.
        Salida: Relacion, de A en el codominio de S, con (a, c) cuando existe b con (a, b) ∈ R y (b, c) ∈ S. Lanza ComposicionInvalidaError si anterior no es Relacion o si su codominio no cabe en el dominio de S.
        """
        if not isinstance(anterior, Relacion):
            raise ComposicionInvalidaError(
                f"Solo se pueden componer relaciones, se recibió {type(anterior).__name__}."
            )
        if not anterior._codominio.es_subconjunto(self._dominio):
            raise ComposicionInvalidaError(
                f"El codominio {anterior._codominio} no está contenido en el "
                f"dominio {self._dominio}; la composición no está definida."
            )
        pares = {
            (a, c)
            for a, b in anterior._pares.elementos
            for c in self._tabla.get(b, ())
        }
        return Relacion(pares, anterior._dominio, self._codominio)

    def matriz(self) -> list:
        """Calcula la matriz booleana de la relación.

        Entrada: ninguna.
        Salida: list, de listas de bool con una fila por elemento del dominio y una columna por elemento del codominio, ambos en orden ascendente; [i][j] es True si (aᵢ, bⱼ) ∈ R.
        """
        pares = self._pares.elementos
        columnas = list(self._codominio)
        return [[(a, b) in pares for b in columnas] for a in self._dominio]

    def cerradura_reflexiva(self) -> "Relacion":
        """Calcula la cerradura reflexiva: R más los pares (a, a) que falten.

        Entrada: ninguna.
        Salida: Relacion, la menor relación reflexiva que contiene a R. Lanza RelacionNoHomogeneaError si dominio y codominio difieren.
        """
        self._exigir_homogenea()
        diagonal = [(a, a) for a in self._dominio]
        return Relacion(
            self._pares.union(diagonal), self._dominio, self._codominio
        )

    def cerradura_simetrica(self) -> "Relacion":
        """Calcula la cerradura simétrica: R más los pares inversos que falten.

        Entrada: ninguna.
        Salida: Relacion, la menor relación simétrica que contiene a R. Lanza RelacionNoHomogeneaError si dominio y codominio difieren.
        """
        self._exigir_homogenea()
        return Relacion(
            self._pares.union(self.inversa()._pares),
            self._dominio,
            self._codominio,
        )

    def cerradura_transitiva(self) -> "Relacion":
        """Calcula la cerradura transitiva con el algoritmo de Warshall.

        Entrada: ninguna.
        Salida: Relacion, la menor relación transitiva que contiene a R. Lanza RelacionNoHomogeneaError si dominio y codominio difieren.
        """
        self._exigir_homogenea()
        return Relacion.desde_matriz(warshall(self.matriz()), self._dominio)
