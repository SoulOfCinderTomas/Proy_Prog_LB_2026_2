import pytest

from teoria_conjuntos_toolkit import exceptions as exc


@pytest.mark.parametrize(
    "clase",
    [
        exc.ConjuntoInvalidoError,
        exc.ElementoNoHashableError,
        exc.OperacionInvalidaError,
        exc.UniversoInvalidoError,
        exc.ConjuntoDemasiadoGrandeError,
        exc.FamiliaInvalidaError,
        exc.FamiliaVaciaError,
        exc.NaturalInvalidoError,
    ],
)
def test_todas_heredan_de_la_base(clase):
    assert issubclass(clase, exc.TeoriaConjuntosError)


def test_compatibilidad_con_excepciones_estandar():
    assert issubclass(exc.ConjuntoInvalidoError, ValueError)
    assert issubclass(exc.ElementoNoHashableError, TypeError)
    assert issubclass(exc.UniversoInvalidoError, ValueError)
    assert issubclass(exc.NaturalInvalidoError, ValueError)
