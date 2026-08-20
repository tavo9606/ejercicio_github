# -*- coding: utf-8 -*-
"""
=======================================================================
TAREA CAPACITACIÓN CALIDAD Y TESTING
5 refactorizaciones NO triviales del catálogo de refactoring.guru
Lenguaje: Python 3
=======================================================================

Fuente del catálogo: https://refactoring.guru/refactoring/techniques

Técnicas elegidas:
  1. Replace Conditional with Polymorphism   (Simplifying Conditional Expressions)
  2. Replace Type Code with State/Strategy   (Organizing Data)
  3. Replace Method with Method Object       (Composing Methods)
  4. Form Template Method                    (Dealing with Generalization)
  5. Replace Inheritance with Delegation     (Dealing with Generalization)

Estructura de cada bloque:
    - Código ANTES   -> el código "mal escrito" (el olor / code smell)
    - Código DESPUÉS -> el código ya refactorizado
    - Comentario     -> qué se hizo, por qué y qué se gana

Ejecutar con:  python3 refactorizaciones.py
"""

from abc import ABC, abstractmethod


# =====================================================================
# 1) REPLACE CONDITIONAL WITH POLYMORPHISM
#    (Reemplazar condiciona se hizo el cambio) se hizo otro cambio
# =====================================================================
#
# PROBLEMA (olor): un condicional (if/elif) que se ramifica según el TIPO
# de objeto y ejecuta acciones distintas en cada rama. Cada vez que
# aparece un tipo nuevo hay que tocar TODOS los métodos que tienen ese
# mismo if -> se rompe el principio Abierto/Cerrado (SOLID) y es muy
# fácil olvidar una rama.
# ---------------------------------------------------------------------

# ---------------------------- ANTES ----------------------------------
class AveMal:
    """MAL: una sola clase con if/elif repetidos para cada especie."""

    def __init__(self, tipo, num_cocos=0, esta_enferma=False):
        self.tipo = tipo                    # "europeo" | "africano" | "noruego"
        self.num_cocos = num_cocos
        self.esta_enferma = esta_enferma

    def velocidad(self):
        # Primer condicional gigante sobre el tipo...
        if self.tipo == "europeo":
            return 35
        elif self.tipo == "africano":
            return 40 - 2 * self.num_cocos
        elif self.tipo == "noruego":
            return 0 if self.esta_enferma else 30
        raise ValueError("Tipo de ave desconocido")

    def plumaje(self):
        # ...y aquí ESTÁ REPETIDO el mismo condicional. Si mañana agrego
        # el ave "australiana" tengo que acordarme de editar los dos.
        if self.tipo == "europeo":
            return "promedio"
        elif self.tipo == "africano":
            return "gastado" if self.num_cocos > 2 else "promedio"
        elif self.tipo == "noruego":
            return "mojado" if self.esta_enferma else "brillante"
        raise ValueError("Tipo de ave desconocido")


# --------------------------- DESPUÉS ---------------------------------
class Ave(ABC):
    """
    BIEN: clase base abstracta. Cada especie es una subclase y cada rama
    del if se convirtió en una implementación del método.
    """

    @abstractmethod
    def velocidad(self):
        ...

    @abstractmethod
    def plumaje(self):
        ...


class AveEuropea(Ave):
    def velocidad(self):
        return 35

    def plumaje(self):
        return "promedio"


class AveAfricana(Ave):
    def __init__(self, num_cocos=0):
        self.num_cocos = num_cocos

    def velocidad(self):
        return 40 - 2 * self.num_cocos

    def plumaje(self):
        return "gastado" if self.num_cocos > 2 else "promedio"


class AveNoruega(Ave):
    def __init__(self, esta_enferma=False):
        self.esta_enferma = esta_enferma

    def velocidad(self):
        return 0 if self.esta_enferma else 30

    def plumaje(self):
        return "mojado" if self.esta_enferma else "brillante"


# COMENTARIO / EXPLICACIÓN 1 --------------------------------------------
# Qué se hizo: se creó la jerarquía Ave -> AveEuropea / AveAfricana /
#   AveNoruega y cada rama del if se movió al método sobrescrito de la
#   subclase correspondiente. El condicional desaparece: quien llama
#   simplemente hace ave.velocidad() y el despacho lo hace Python.
# Por qué: el condicional estaba DUPLICADO en dos métodos y crecía con
#   cada especie nueva (código escopeta / shotgun surgery).
# Qué se gana:
#   - Agregar una especie = agregar una clase, sin tocar código existente
#     (principio Abierto/Cerrado).
#   - Cada clase queda con sólo los atributos que usa (num_cocos ya no
#     existe en las aves noruegas).
#   - Para testing: se puede probar cada especie de forma aislada y un
#     test doble (mock) de Ave es trivial de construir.
# Cuándo NO aplicarla: si hay una sola rama o el condicional no depende
#   del tipo, el polimorfismo agrega complejidad innecesaria.
# ----------------------------------------------------------------------


# =====================================================================
# 2) REPLACE TYPE CODE WITH STATE/STRATEGY
#    (Reemplazar código de tipo con estado/estrategia)
# =====================================================================
#
# PROBLEMA (olor): un atributo "código de tipo" (una constante o string)
# que afecta el comportamiento del objeto Y que puede CAMBIAR durante la
# vida del objeto. No se puede usar herencia (Replace Type Code with
# Subclasses) porque un objeto no puede cambiar de clase; entonces el
# tipo se extrae a un objeto colaborador intercambiable.
# ---------------------------------------------------------------------

# ---------------------------- ANTES ----------------------------------
class EmpleadoMal:
    """MAL: el 'tipo' es un entero mágico y el cálculo es un if enorme."""

    INGENIERO = 0
    VENDEDOR = 1
    GERENTE = 2

    def __init__(self, tipo, salario_base, ventas=0, personas_a_cargo=0):
        self.tipo = tipo
        self.salario_base = salario_base
        self.ventas = ventas
        self.personas_a_cargo = personas_a_cargo

    def pago_mensual(self):
        if self.tipo == EmpleadoMal.INGENIERO:
            return self.salario_base
        elif self.tipo == EmpleadoMal.VENDEDOR:
            return self.salario_base + 0.05 * self.ventas
        elif self.tipo == EmpleadoMal.GERENTE:
            return self.salario_base + 100_000 * self.personas_a_cargo
        raise ValueError("Tipo de empleado inválido")

    def ascender(self, nuevo_tipo):
        # El empleado CAMBIA de tipo -> por eso no sirven las subclases.
        self.tipo = nuevo_tipo


# --------------------------- DESPUÉS ---------------------------------
class TipoEmpleado(ABC):
    """Estrategia: encapsula el comportamiento que dependía del 'tipo'."""

    @abstractmethod
    def pago(self, empleado):
        ...


class Ingeniero(TipoEmpleado):
    def pago(self, empleado):
        return empleado.salario_base


class Vendedor(TipoEmpleado):
    def pago(self, empleado):
        return empleado.salario_base + 0.05 * empleado.ventas


class Gerente(TipoEmpleado):
    def pago(self, empleado):
        return empleado.salario_base + 100_000 * empleado.personas_a_cargo


class Empleado:
    """
    BIEN: Empleado ya no sabe nada de tipos; delega en una estrategia
    que puede reemplazarse en tiempo de ejecución.
    """

    def __init__(self, tipo, salario_base, ventas=0, personas_a_cargo=0):
        self._tipo = tipo                   # instancia de TipoEmpleado
        self.salario_base = salario_base
        self.ventas = ventas
        self.personas_a_cargo = personas_a_cargo

    def pago_mensual(self):
        return self._tipo.pago(self)        # sin ningún if

    def ascender(self, nuevo_tipo):
        self._tipo = nuevo_tipo             # cambiar de estado = cambiar objeto


# COMENTARIO / EXPLICACIÓN 2 --------------------------------------------
# Qué se hizo: el atributo entero `tipo` (0/1/2) se reemplazó por un
#   objeto de la jerarquía TipoEmpleado. El if de pago_mensual() se
#   repartió entre Ingeniero, Vendedor y Gerente, y Empleado sólo delega.
# Por qué NO se usó "Replace Type Code with Subclasses": porque el tipo
#   cambia durante la vida del objeto (ascender()) y un objeto en Python
#   no debería cambiar de clase; con State/Strategy sólo se reemplaza el
#   objeto colaborador.
# Qué se gana:
#   - Se eliminan los números mágicos y el ValueError por tipo inválido.
#   - Agregar "Practicante" no obliga a modificar la clase Empleado.
#   - Para testing: cada regla salarial se prueba por separado con un
#     objeto Empleado falso, sin construir toda la nómina.
# Diferencia State vs Strategy: es el MISMO refactor; se llama State si
#   el objeto representa una fase del ciclo de vida (y él mismo decide la
#   transición), y Strategy si es un algoritmo intercambiable desde fuera.
# ----------------------------------------------------------------------


# =====================================================================
# 3) REPLACE METHOD WITH METHOD OBJECT
#    (Reemplazar método con objeto-método)
# =====================================================================
#
# PROBLEMA (olor): un método largo con muchas variables locales
# entrelazadas. No se puede aplicar Extract Method porque habría que
# pasar 6 u 8 parámetros a cada submétodo. Solución: convertir el método
# entero en una clase, donde las variables locales pasan a ser campos y
# los pasos pasan a ser métodos privados.
# ---------------------------------------------------------------------

# ---------------------------- ANTES ----------------------------------
class PedidoMal:
    def __init__(self, items, cliente_vip, pais, cupon=None):
        self.items = items                  # [(nombre, precio, cantidad)]
        self.cliente_vip = cliente_vip
        self.pais = pais
        self.cupon = cupon

    def calcular_total(self):
        """MAL: método largo, con 6 temporales que dependen entre sí."""
        subtotal = 0
        unidades = 0
        for _nombre, precio, cantidad in self.items:
            subtotal += precio * cantidad
            unidades += cantidad

        descuento = 0
        if self.cliente_vip:
            descuento += subtotal * 0.10
        if unidades >= 10:
            descuento += subtotal * 0.05
        if self.cupon == "BIENVENIDA":
            descuento += 10_000
        descuento = min(descuento, subtotal * 0.30)   # tope del 30%

        base_gravable = subtotal - descuento
        iva = base_gravable * (0.19 if self.pais == "CO" else 0.0)

        envio = 0 if base_gravable > 150_000 else 12_000
        if self.pais != "CO":
            envio += 45_000

        return round(base_gravable + iva + envio, 2)


# --------------------------- DESPUÉS ---------------------------------
class Pedido:
    def __init__(self, items, cliente_vip, pais, cupon=None):
        self.items = items
        self.cliente_vip = cliente_vip
        self.pais = pais
        self.cupon = cupon

    def calcular_total(self):
        # El método original queda como una sola línea que delega.
        return CalculadoraDeTotal(self).calcular()


class CalculadoraDeTotal:
    """
    BIEN: objeto-método. Las variables locales del método largo ahora son
    atributos de esta clase, así que cada paso es un método pequeño sin
    listas interminables de parámetros.
    """

    def __init__(self, pedido):
        self.pedido = pedido
        self.subtotal = 0
        self.unidades = 0
        self.descuento = 0
        self.base_gravable = 0
        self.iva = 0
        self.envio = 0

    def calcular(self):
        self._sumar_items()
        self._aplicar_descuentos()
        self._calcular_impuestos()
        self._calcular_envio()
        return round(self.base_gravable + self.iva + self.envio, 2)

    def _sumar_items(self):
        for _nombre, precio, cantidad in self.pedido.items:
            self.subtotal += precio * cantidad
            self.unidades += cantidad

    def _aplicar_descuentos(self):
        if self.pedido.cliente_vip:
            self.descuento += self.subtotal * 0.10
        if self.unidades >= 10:
            self.descuento += self.subtotal * 0.05
        if self.pedido.cupon == "BIENVENIDA":
            self.descuento += 10_000
        self.descuento = min(self.descuento, self.subtotal * 0.30)
        self.base_gravable = self.subtotal - self.descuento

    def _calcular_impuestos(self):
        self.iva = self.base_gravable * (0.19 if self.pedido.pais == "CO" else 0.0)

    def _calcular_envio(self):
        self.envio = 0 if self.base_gravable > 150_000 else 12_000
        if self.pedido.pais != "CO":
            self.envio += 45_000


# COMENTARIO / EXPLICACIÓN 3 --------------------------------------------
# Qué se hizo: el método largo calcular_total() se convirtió en la clase
#   CalculadoraDeTotal. Sus temporales (subtotal, unidades, descuento,
#   base_gravable, iva, envio) son ahora campos, y cada etapa del cálculo
#   es un método privado. Pedido.calcular_total() sólo delega.
# Por qué: Extract Method directo era inviable —cada paso necesitaba 3 o
#   4 temporales de entrada y devolvía otros tantos—. Al subirlos a
#   campos, los submétodos quedan sin parámetros.
# Qué se gana:
#   - Métodos de 3-5 líneas, legibles y con nombre que documenta el paso.
#   - Se pueden testear las etapas por separado (calcular sólo el envío)
#     y afinar reglas de negocio sin releer 25 líneas.
#   - La clase Pedido deja de cargar con la complejidad del cálculo
#     (menos responsabilidades, más cohesión).
# Precaución: el objeto-método es de un solo uso (guarda estado del
#   cálculo); se crea uno nuevo por cada invocación, como aquí.
# ----------------------------------------------------------------------


# =====================================================================
# 4) FORM TEMPLATE METHOD
#    (Formar método plantilla)
# =====================================================================
#
# PROBLEMA (olor): dos subclases ejecutan los MISMOS pasos, en el mismo
# orden, pero con detalles distintos. El algoritmo está duplicado; si
# cambia el orden hay que corregirlo en todas las subclases.
# ---------------------------------------------------------------------

# ---------------------------- ANTES ----------------------------------
class ReporteHTMLMal:
    """MAL: el algoritmo (encabezado -> cuerpo -> pie) está duplicado."""

    def generar(self, filas):
        salida = "<h1>Reporte de ventas</h1>\n"
        for f in filas:
            salida += "<p>%s: %s</p>\n" % (f[0], f[1])
        salida += "<footer>Total: %d filas</footer>" % len(filas)
        return salida


class ReporteTextoMal:
    """MAL: mismo orden de pasos, copiado y pegado con otro formato."""

    def generar(self, filas):
        salida = "REPORTE DE VENTAS\n"
        for f in filas:
            salida += "%s: %s\n" % (f[0], f[1])
        salida += "Total: %d filas" % len(filas)
        return salida


# --------------------------- DESPUÉS ---------------------------------
class Reporte(ABC):
    """
    BIEN: la superclase define el ESQUELETO del algoritmo (el template
    method) y deja los pasos variables como métodos abstractos.
    """

    def generar(self, filas):          # <- método plantilla: NO se sobrescribe
        partes = [self.encabezado()]
        partes += [self.linea(f) for f in filas]
        partes.append(self.pie(len(filas)))
        return "".join(partes)

    @abstractmethod
    def encabezado(self):
        ...

    @abstractmethod
    def linea(self, fila):
        ...

    @abstractmethod
    def pie(self, total):
        ...


class ReporteHTML(Reporte):
    def encabezado(self):
        return "<h1>Reporte de ventas</h1>\n"

    def linea(self, fila):
        return "<p>%s: %s</p>\n" % (fila[0], fila[1])

    def pie(self, total):
        return "<footer>Total: %d filas</footer>" % total


class ReporteTexto(Reporte):
    def encabezado(self):
        return "REPORTE DE VENTAS\n"

    def linea(self, fila):
        return "%s: %s\n" % (fila[0], fila[1])

    def pie(self, total):
        return "Total: %d filas" % total


# COMENTARIO / EXPLICACIÓN 4 --------------------------------------------
# Qué se hizo: se identificaron los pasos comunes (encabezado, línea por
#   fila, pie), se extrajo cada uno a un método y el orden de ejecución
#   subió a la superclase Reporte.generar(), que queda como "template
#   method". Las subclases sólo aportan el formato.
# Por qué: el algoritmo estaba duplicado en dos clases; un cambio (por
#   ejemplo, agregar la fecha al pie) obligaba a editar ambas y era fácil
#   que quedaran inconsistentes.
# Qué se gana:
#   - Una sola definición del flujo -> se elimina duplicación estructural.
#   - Un formato nuevo (CSV, Markdown) = una subclase de 3 métodos.
#   - Para testing: el flujo se prueba una vez con una subclase falsa; de
#     cada subclase real sólo se prueban los 3 métodos de formato.
# Ojo: si el orden de los pasos NO es el mismo entre subclases, esta
#   refactorización no aplica; ahí conviene Strategy.
# ----------------------------------------------------------------------


# =====================================================================
# 5) REPLACE INHERITANCE WITH DELEGATION
#    (Reemplazar herencia con delegación)
# =====================================================================
#
# PROBLEMA (olor): una subclase hereda de otra clase sólo para reutilizar
# código, pero NO cumple la relación "es-un". Hereda métodos que no tienen
# sentido y que rompen el invariante de la subclase (violación del
# principio de sustitución de Liskov).
# ---------------------------------------------------------------------

# ---------------------------- ANTES ----------------------------------
class ListaMal(list):
    pass


class PilaMal(ListaMal):
    """
    MAL: Pila hereda de list para reusar append/pop, pero así también
    hereda insert(), remove(), sort(), __getitem__... y cualquiera puede
    meter un elemento por la mitad, rompiendo la semántica LIFO.
    """

    def apilar(self, x):
        self.append(x)

    def desapilar(self):
        return self.pop()


# --------------------------- DESPUÉS ---------------------------------
class Pila:
    """
    BIEN: Pila TIENE una lista (composición) en lugar de SER una lista.
    Sólo se expone la interfaz que corresponde a una pila.
    """

    def __init__(self):
        self._items = []                    # delegado, privado

    def apilar(self, x):
        self._items.append(x)

    def desapilar(self):
        if not self._items:
            raise IndexError("La pila está vacía")
        return self._items.pop()

    def cima(self):
        return self._items[-1]

    def __len__(self):                      # se delega sólo lo que aplica
        return len(self._items)


# COMENTARIO / EXPLICACIÓN 5 --------------------------------------------
# Qué se hizo: se eliminó la herencia `class Pila(list)` y en su lugar la
#   Pila guarda una lista como atributo privado (_items) y delega en ella
#   sólo las operaciones válidas: apilar, desapilar, cima y len().
# Por qué: la herencia era por conveniencia, no por tipo. `PilaMal` es
#   sustituible por una lista sólo en apariencia: al heredar insert() y
#   sort() permite violar el orden LIFO, que es justamente el invariante
#   que la clase debe garantizar (LSP, la L de SOLID).
# Qué se gana:
#   - Interfaz mínima y honesta: lo que no es una operación de pila no
#     existe; el mal uso deja de compilar en vez de fallar en producción.
#   - Se puede cambiar la estructura interna (deque, lista enlazada) sin
#     afectar a los clientes.
#   - Control de errores propio (desapilar() sobre pila vacía da un
#     mensaje claro) y superficie de pruebas mucho más pequeña.
# Refactorización inversa: Replace Delegation with Inheritance, útil
#   cuando la clase termina delegando TODOS los métodos sin agregar nada.
# ----------------------------------------------------------------------


# =====================================================================
# DEMO / VERIFICACIÓN
# Una refactorización es válida sólo si el comportamiento observable no
# cambia. Aquí se ejecuta la versión ANTES y la DESPUÉS y se comparan.
# =====================================================================
def main():
    ok = True

    def comparar(titulo, antes, despues):
        nonlocal ok
        igual = antes == despues
        ok = ok and igual
        estado = "OK " if igual else "FALLA"
        print("[%s] %-42s antes=%s | despues=%s" % (estado, titulo, antes, despues))

    print("=" * 78)
    print("1) Replace Conditional with Polymorphism")
    print("=" * 78)
    comparar("europeo.velocidad()", AveMal("europeo").velocidad(), AveEuropea().velocidad())
    comparar("africano(3).plumaje()",
             AveMal("africano", num_cocos=3).plumaje(), AveAfricana(3).plumaje())
    comparar("noruego(enfermo).velocidad()",
             AveMal("noruego", esta_enferma=True).velocidad(), AveNoruega(True).velocidad())

    print()
    print("=" * 78)
    print("2) Replace Type Code with State/Strategy")
    print("=" * 78)
    v_mal = EmpleadoMal(EmpleadoMal.VENDEDOR, 2_000_000, ventas=10_000_000)
    v_ok = Empleado(Vendedor(), 2_000_000, ventas=10_000_000)
    comparar("pago vendedor", v_mal.pago_mensual(), v_ok.pago_mensual())

    v_mal.ascender(EmpleadoMal.GERENTE)
    v_mal.personas_a_cargo = 4
    v_ok.ascender(Gerente())
    v_ok.personas_a_cargo = 4
    comparar("pago tras ascenso a gerente", v_mal.pago_mensual(), v_ok.pago_mensual())

    print()
    print("=" * 78)
    print("3) Replace Method with Method Object")
    print("=" * 78)
    items = [("teclado", 120_000, 2), ("mouse", 60_000, 9)]
    comparar("total pedido CO (VIP, cupón)",
             PedidoMal(items, True, "CO", "BIENVENIDA").calcular_total(),
             Pedido(items, True, "CO", "BIENVENIDA").calcular_total())
    comparar("total pedido exterior",
             PedidoMal([("mouse", 60_000, 1)], False, "PE").calcular_total(),
             Pedido([("mouse", 60_000, 1)], False, "PE").calcular_total())

    print()
    print("=" * 78)
    print("4) Form Template Method")
    print("=" * 78)
    filas = [("Enero", 1200), ("Febrero", 980)]
    comparar("reporte HTML", ReporteHTMLMal().generar(filas), ReporteHTML().generar(filas))
    comparar("reporte texto", ReporteTextoMal().generar(filas), ReporteTexto().generar(filas))

    print()
    print("=" * 78)
    print("5) Replace Inheritance with Delegation")
    print("=" * 78)
    p_mal, p_ok = PilaMal(), Pila()
    for x in (1, 2, 3):
        p_mal.apilar(x)
        p_ok.apilar(x)
    comparar("desapilar()", p_mal.desapilar(), p_ok.desapilar())
    comparar("len() tras desapilar", len(p_mal), len(p_ok))

    # El punto de la refactorización 5: la versión heredada permite algo
    # que una pila NO debería permitir.
    p_mal.insert(0, 99)          # heredado de list: rompe el orden LIFO
    print("  -> PilaMal permite insert(0, 99) y queda %s  (LIFO roto)" % list(p_mal))
    print("  -> Pila no expone insert():", not hasattr(p_ok, "insert"))

    print()
    print("RESULTADO GLOBAL:", "todas las refactorizaciones preservan el comportamiento"
          if ok else "hay diferencias de comportamiento")


if __name__ == "__main__":
    main()