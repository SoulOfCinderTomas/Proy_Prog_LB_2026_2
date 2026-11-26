import matplotlib.pyplot as plt

from teoria_conjuntos_toolkit import (
    Funcion,
    Relacion,
    arbol_von_neumann,
    diagrama_sagital,
    diagrama_venn,
    grafo_relacion,
    visualizar_particion,
)


def main() -> None:
    """Dibuja un ejemplo de cada gráfico de la librería y los muestra en pantalla.

    Entrada: ninguna.
    Salida: None, abre las ventanas de matplotlib con los cinco gráficos.
    """
    diagrama_venn(
        [{2,3,5,7}, {1,3,5,7,9}, {1,4,9}],
        nombres=["Primos", "Impares", "Cuadrados"],
        universo=range(1, 11),
        titulo="Diagrama de Venn",
    )
    congruencia = Relacion.desde_predicado(range(6), lambda a, b: (a - b) % 3 == 0)
    grafo_relacion(congruencia, titulo="Congruencia módulo 3")
    f = Funcion.desde_regla([1, 2, 3, 4], lambda x: x % 3, [0, 1, 2, 3])
    diagrama_sagital(f, titulo="f(x) = x mod 3")
    visualizar_particion(congruencia, titulo="Partición inducida")
    arbol_von_neumann(4)
    plt.show()


if __name__ == "__main__":
    main()
