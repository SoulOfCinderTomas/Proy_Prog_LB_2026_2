from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable, Iterable, Optional

from .conjunto import Conjunto, como_conjunto
from .exceptions import (
    FueraDeDominioError,
    FuncionInvalidaError,
    NoBiyectivaError,
)
from .relacion import Relacion


class Funcion(Relacion):
    __slots__ = ()

    def __init__(
        self,
        pares: Iterable[Any],
        dominio: Iterable[Any],
        codominio: Iterable[Any],
    ) -> None:
        """Construye una función f: A → B, es decir una relación donde cada a ∈ A tiene una sola imagen.

        Entrada: pares (iterable), pares ordenados (a, f(a)); dominio (iterable), conjunto A; codominio (iterable), conjunto B.
        Salida: None, crea la Funcion. Lanza FuncionInvalidaError si algún elemento de A no tiene imagen o tiene varias, y RelacionInvalidaError si los pares no son válidos o salen de A × B.
        """
        super().__init__(pares, dominio, codominio)
        conflictos = self._conflictos_de_funcion()
        if conflictos:
            a = conflictos[0]
            cantidad = len(self._tabla.get(a, ()))
            detalle = (
                "no tiene imagen"
                if cantidad == 0
                else f"tiene {cantidad} imágenes: {self.imagenes(a)}"
            )
            raise FuncionInvalidaError(f"No es una función: {a!r} {detalle}.")

    @classmethod
    def desde_diccionario(
        cls, mapa: Mapping, codominio: Optional[Iterable[Any]] = None
    ) -> "Funcion":
        """Construye una función a partir de un diccionario clave → valor.

        Entrada: mapa (Mapping), diccionario donde las claves forman el dominio y los valores las imágenes; codominio (iterable, opcional), conjunto B, que por defecto son los valores del diccionario.
        Salida: Funcion, con un par (clave, valor) por entrada. Lanza FuncionInvalidaError si mapa no es un diccionario, y RelacionInvalidaError si algún valor queda fuera del codominio.
        """
        if not isinstance(mapa, Mapping):
            raise FuncionInvalidaError(
                f"Se esperaba un diccionario, se recibió {type(mapa).__name__}."
            )
        dominio = Conjunto(mapa.keys())
        cod = Conjunto(mapa.values()) if codominio is None else como_conjunto(codominio)
        return cls(mapa.items(), dominio, cod)

    @classmethod
    def desde_regla(
        cls,
        dominio: Iterable[Any],
        regla: Callable[[Any], Any],
        codominio: Optional[Iterable[Any]] = None,
    ) -> "Funcion":
        """Construye una función evaluando una regla f(a) en cada elemento del dominio.

        Entrada: dominio (iterable), conjunto A; regla (callable), función de un argumento; codominio (iterable, opcional), conjunto B, que por defecto es la imagen de la regla.
        Salida: Funcion, con los pares (a, regla(a)). Lanza FuncionInvalidaError si regla no es invocable o no está definida en algún elemento (por ejemplo 1/0), y RelacionInvalidaError si algún valor queda fuera del codominio.
        """
        if not callable(regla):
            raise FuncionInvalidaError("La regla debe ser invocable.")
        dom = como_conjunto(dominio)
        pares = []
        for a in dom:
            try:
                pares.append((a, regla(a)))
            except (ArithmeticError, ValueError, TypeError) as error:
                raise FuncionInvalidaError(
                    f"La regla no está definida en {a!r}: {error}"
                ) from error
        cod = Conjunto(b for _, b in pares) if codominio is None else como_conjunto(codominio)
        return cls(pares, dom, cod)

    def __call__(self, elemento: Any) -> Any:
        """Evalúa la función en un elemento, f(a).

        Entrada: elemento (Any), elemento a del dominio.
        Salida: Any, la única imagen de a. Lanza FueraDeDominioError si a no está en el dominio.
        """
        if elemento not in self._dominio:
            raise FueraDeDominioError(
                f"{elemento!r} no pertenece al dominio {self._dominio}."
            )
        (valor,) = self._tabla[elemento]
        return valor

    def es_inyectiva(self) -> bool:
        """Evalúa si elementos distintos del dominio tienen imágenes distintas.

        Entrada: ninguna.
        Salida: bool, True si |imagen| = |dominio|.
        """
        return self.imagen().cardinal == self._dominio.cardinal

    def es_sobreyectiva(self) -> bool:
        """Evalúa si todo elemento del codominio es imagen de alguno del dominio.

        Entrada: ninguna.
        Salida: bool, True si la imagen es igual al codominio.
        """
        return self.imagen() == self._codominio

    def es_biyectiva(self) -> bool:
        """Evalúa si la función es inyectiva y sobreyectiva a la vez.

        Entrada: ninguna.
        Salida: bool, True si es biyectiva.
        """
        return self.es_inyectiva() and self.es_sobreyectiva()

    def funcion_inversa(self) -> "Funcion":
        """Calcula la función inversa f⁻¹: B → A, que solo existe si f es biyectiva.

        Entrada: ninguna.
        Salida: Funcion, de B en A. Lanza NoBiyectivaError si f no es biyectiva (la relación inversa sí existe y se obtiene con inversa()).
        """
        if not self.es_biyectiva():
            raise NoBiyectivaError(
                "La función no es biyectiva, no tiene función inversa; "
                "usa inversa() para obtener la relación inversa."
            )
        inversa = self.inversa()
        return Funcion(inversa.pares, inversa.dominio, inversa.codominio)

    def composicion(self, anterior: Relacion) -> Relacion:
        """Calcula la composición g ∘ f, donde g es esta función y f es la que se aplica primero.

        Entrada: anterior (Relacion o Funcion), f de A en B, cuyo codominio debe estar contenido en el dominio de g.
        Salida: Funcion si f también es función, o Relacion en otro caso; va de A al codominio de g. Lanza ComposicionInvalidaError si anterior no es Relacion o si su codominio no cabe en el dominio de g.
        """
        compuesta = super().composicion(anterior)
        if isinstance(anterior, Funcion):
            return Funcion(compuesta.pares, compuesta.dominio, compuesta.codominio)
        return compuesta
