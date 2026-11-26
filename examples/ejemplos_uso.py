from teoria_conjuntos_toolkit import (
    Conjunto,
    FamiliaDeConjuntos,
    Funcion,
    Relacion,
    TeoriaConjuntosError,
    clase_de,
    es_natural_von_neumann,
    generar_particion,
    interseccion_generalizada,
    naturales_von_neumann,
    numero_von_neumann,
    producto_cartesiano,
    relacion_desde_particion,
    sucesor,
    union_generalizada,
    validar_particion,
)


def titulo(texto: str) -> None:
    """Imprime un encabezado de sección.

    Entrada: texto (str), nombre de la sección.
    Salida: None, escribe el encabezado en pantalla.
    """
    print(f"\n=== {texto} ===")


def ejemplo_conjuntos() -> None:
    """Muestra la creación y las operaciones básicas entre conjuntos.

    Entrada: ninguna.
    Salida: None, imprime los resultados.
    """
    titulo("Conjuntos")
    a = Conjunto([1, 2, 3, 4])
    b = Conjunto([3, 4, 5, 6])
    universo = range(1, 9)
    print("A =", a, "| B =", b)
    print("A ∪ B =", a.union(b))
    print("A ∩ B =", a.interseccion(b))
    print("A - B =", a.diferencia(b))
    print("A Δ B =", a.diferencia_simetrica(b))
    print("A^c en U =", a.complemento(universo))
    print("|A| =", a.cardinal)
    print("{1, 2} ⊆ A:", Conjunto([1, 2]).es_subconjunto(a))
    print("A y {7, 8} disjuntos:", a.es_disjunto([7, 8]))
    print("P({1, 2}) =", Conjunto([1, 2]).conjunto_potencia())
    print("{1, 2} × {'x', 'y'} =", producto_cartesiano([1, 2], ["x", "y"]))


def ejemplo_familias() -> None:
    """Muestra operaciones generalizadas y números de Von Neumann.

    Entrada: ninguna.
    Salida: None, imprime los resultados.
    """
    titulo("Familias de conjuntos")
    familia = FamiliaDeConjuntos([{1, 2, 3}, {2, 3, 4}, {3, 4, 5}])
    print("Familia:", familia)
    print("Unión generalizada:", familia.union())
    print("Intersección generalizada:", familia.interseccion())
    print("Disjunta dos a dos:", familia.es_disjunta_dos_a_dos())
    print("Recubre {1..5}:", familia.recubre(range(1, 6)))
    print("Función suelta:", union_generalizada([{1}, {2}]), interseccion_generalizada([{1, 2}, {2, 3}]))

    titulo("Naturales de Von Neumann")
    print("0 =", numero_von_neumann(0))
    print("3 =", numero_von_neumann(3))
    print("S(2) =", sucesor(numero_von_neumann(2)))
    print("Naturales de 0 a 4:", naturales_von_neumann(4))
    print("¿{∅} es natural?", es_natural_von_neumann(numero_von_neumann(1)))
    print("¿{1, 2} es natural?", es_natural_von_neumann({1, 2}))


def ejemplo_relaciones() -> None:
    """Muestra propiedades, cerraduras y composición de relaciones.

    Entrada: ninguna.
    Salida: None, imprime los resultados.
    """
    titulo("Relaciones")
    menor_igual = Relacion.desde_predicado(range(1, 5), lambda a, b: a <= b)
    print("Reflexiva:", menor_igual.es_reflexiva())
    print("Simétrica:", menor_igual.es_simetrica())
    print("Antisimétrica:", menor_igual.es_antisimetrica())
    print("Transitiva:", menor_igual.es_transitiva())
    print("Es orden:", menor_igual.es_relacion_orden())
    print("Es equivalencia:", menor_igual.es_relacion_equivalencia())
    print("Matriz:", menor_igual.matriz())

    titulo("Cerraduras")
    cadena = Relacion([(1, 2), (2, 3), (3, 4)], range(1, 5))
    print("R =", cadena.pares)
    print("Reflexiva:", cadena.cerradura_reflexiva().pares)
    print("Simétrica:", cadena.cerradura_simetrica().pares)
    print("Transitiva:", cadena.cerradura_transitiva().pares)

    titulo("Inversa y composición")
    r = Relacion([(1, "a"), (2, "b")], [1, 2], ["a", "b"])
    s = Relacion([("a", "X"), ("b", "Y")], ["a", "b"], ["X", "Y"])
    print("R⁻¹ =", r.inversa().pares)
    print("S∘R =", s.composicion(r).pares)


def ejemplo_funciones() -> None:
    """Muestra clasificación, inversa y composición de funciones.

    Entrada: ninguna.
    Salida: None, imprime los resultados.
    """
    titulo("Funciones")
    f = Funcion.desde_regla([1, 2, 3], lambda x: x * 2, [2, 4, 6])
    print("f(2) =", f(2))
    print("Inyectiva:", f.es_inyectiva())
    print("Sobreyectiva:", f.es_sobreyectiva())
    print("Biyectiva:", f.es_biyectiva())
    print("f⁻¹ =", f.funcion_inversa().pares)

    g = Funcion.desde_diccionario({2: "a", 4: "b", 6: "c"}, ["a", "b", "c"])
    print("g∘f =", g.composicion(f).pares)

    modulo = Funcion.desde_regla([1, 2, 3, 4], lambda x: x % 2, [0, 1, 2])
    print("x mod 2 -> inyectiva:", modulo.es_inyectiva(), "| sobreyectiva:", modulo.es_sobreyectiva())


def ejemplo_equivalencia() -> None:
    """Muestra el teorema entre relaciones de equivalencia y particiones.

    Entrada: ninguna.
    Salida: None, imprime los resultados.
    """
    titulo("Equivalencia y particiones")
    congruencia = Relacion.desde_predicado(range(7), lambda a, b: (a - b) % 3 == 0)
    print("Es equivalencia:", congruencia.es_relacion_equivalencia())
    print("Clase de 1:", clase_de(congruencia, 1))
    particion = generar_particion(congruencia)
    print("Partición:", particion)
    print("Es partición de 0..6:", particion.es_particion_de(range(7)))
    reconstruida = relacion_desde_particion(particion, range(7))
    print("Relación reconstruida igual:", reconstruida.pares == congruencia.pares)
    print("Validar partición:", validar_particion([{0, 3, 6}, {1, 4}, {2, 5}], range(7)))


def ejemplo_errores() -> None:
    """Muestra cómo la librería reporta entradas inválidas.

    Entrada: ninguna.
    Salida: None, imprime el tipo y el mensaje de cada error capturado.
    """
    titulo("Manejo de errores")
    casos = [
        lambda: Conjunto([[1, 2], 3]),
        lambda: Conjunto("hola"),
        lambda: numero_von_neumann(-1),
        lambda: Relacion([(1, 9)], [1, 2]),
        lambda: Funcion.desde_diccionario({1: "a", 2: "a"}, ["a", "b"]).funcion_inversa(),
        lambda: generar_particion(Relacion([(1, 2)], [1, 2])),
        lambda: validar_particion([{1, 2}, {2, 3}], [1, 2, 3]),
    ]
    for caso in casos:
        try:
            caso()
        except TeoriaConjuntosError as error:
            print(f"{type(error).__name__}: {error}")


def main() -> None:
    """Ejecuta todos los ejemplos de uso de la librería en orden.

    Entrada: ninguna.
    Salida: None, imprime los resultados de cada sección.
    """
    ejemplo_conjuntos()
    ejemplo_familias()
    ejemplo_relaciones()
    ejemplo_funciones()
    ejemplo_equivalencia()
    ejemplo_errores()


if __name__ == "__main__":
    main()
