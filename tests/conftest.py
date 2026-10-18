import pytest

from teoria_conjuntos_toolkit import Conjunto


@pytest.fixture
def a():
    """Crea el conjunto de prueba A.

    Entrada: ninguna.
    Salida: Conjunto, {1, 2, 3}.
    """
    return Conjunto([1, 2, 3])


@pytest.fixture
def b():
    """Crea el conjunto de prueba B.

    Entrada: ninguna.
    Salida: Conjunto, {3, 4, 5}.
    """
    return Conjunto([3, 4, 5])


@pytest.fixture
def universo():
    """Crea el universo de prueba U.

    Entrada: ninguna.
    Salida: Conjunto, {1, 2, 3, 4, 5, 6, 7}.
    """
    return Conjunto(range(1, 8))
