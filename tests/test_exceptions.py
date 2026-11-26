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
        exc.RelacionInvalidaError,
        exc.RelacionNoHomogeneaError,
        exc.FueraDeDominioError,
        exc.ComposicionInvalidaError,
        exc.FuncionInvalidaError,
        exc.NoBiyectivaError,
        exc.NoEsEquivalenciaError,
        exc.ParticionInvalidaError,
    ],
)
def test_todas_heredan_de_la_base(clase):
    assert issubclass(clase, exc.TeoriaConjuntosError)


def test_compatibilidad_con_excepciones_estandar():
    assert issubclass(exc.ConjuntoInvalidoError, ValueError)
    assert issubclass(exc.ElementoNoHashableError, TypeError)
    assert issubclass(exc.UniversoInvalidoError, ValueError)
    assert issubclass(exc.NaturalInvalidoError, ValueError)


def test_jerarquia_de_relaciones_y_funciones():
    assert issubclass(exc.RelacionInvalidaError, ValueError)
    assert issubclass(exc.FuncionInvalidaError, exc.RelacionInvalidaError)
    assert issubclass(exc.RelacionNoHomogeneaError, exc.OperacionInvalidaError)
    assert issubclass(exc.FueraDeDominioError, exc.OperacionInvalidaError)
    assert issubclass(exc.ComposicionInvalidaError, exc.OperacionInvalidaError)
    assert issubclass(exc.NoBiyectivaError, exc.OperacionInvalidaError)


def test_jerarquia_de_equivalencia_y_particiones():
    assert issubclass(exc.NoEsEquivalenciaError, exc.OperacionInvalidaError)
    assert issubclass(exc.ParticionInvalidaError, exc.FamiliaInvalidaError)
    assert issubclass(exc.ParticionInvalidaError, ValueError)
