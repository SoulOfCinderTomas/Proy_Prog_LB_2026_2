from __future__ import annotations


class TeoriaConjuntosError(Exception):
    pass


class ConjuntoInvalidoError(TeoriaConjuntosError, ValueError):
    pass


class ElementoNoHashableError(ConjuntoInvalidoError, TypeError):
    pass


class OperacionInvalidaError(TeoriaConjuntosError, ValueError):
    pass


class UniversoInvalidoError(OperacionInvalidaError):
    pass


class ConjuntoDemasiadoGrandeError(OperacionInvalidaError):
    pass


class FamiliaInvalidaError(TeoriaConjuntosError, ValueError):
    pass


class FamiliaVaciaError(OperacionInvalidaError):
    pass


class NaturalInvalidoError(TeoriaConjuntosError, ValueError):
    pass
