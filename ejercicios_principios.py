"""
PRINCIPIO KISS - Keep It Simple, Stupid
=======================================
"""

import json


# ---------------------------------------------------------------------------
# EJEMPLO 1: mal - complejidad innecesaria
# ---------------------------------------------------------------------------

def es_par_complicado(numero):
    """Decide si un numero es par... dando muchas vueltas."""
    resultado = None
    contador = 0
    while contador <= abs(numero):
        if contador == abs(numero):
            if contador % 2 == 0:
                resultado = True
            else:
                resultado = False
        contador += 1
    if resultado is True:
        return True
    elif resultado is False:
        return False


# EJEMPLO 1: bien - la version simple
def es_par(numero):
    """Decide si un numero es par."""
    return numero % 2 == 0



"""
PRINCIPIO DRY - Don't Repeat Yourself
=======================================
"""


# ---------------------------------------------------------------------------
# EJEMPLO 2: mal - la misma logica copiada tres veces
# ---------------------------------------------------------------------------

def precio_final_estudiante(precio):
    """Aplica 20% de descuento y suma el 19% de IVA."""
    descuento = precio * 0.20
    subtotal = precio - descuento
    iva = subtotal * 0.19
    return round(subtotal + iva, 2)


def precio_final_jubilado(precio):
    """Aplica 30% de descuento y suma el 19% de IVA."""
    descuento = precio * 0.30
    subtotal = precio - descuento
    iva = subtotal * 0.19
    return round(subtotal + iva, 2)


def precio_final_normal(precio):
    """Sin descuento, suma el 19% de IVA."""
    descuento = precio * 0.0
    subtotal = precio - descuento
    iva = subtotal * 0.19
    return round(subtotal + iva, 2)


# El problema: si manana el IVA sube al 21%, hay que tocar TRES funciones.
# Si te olvidas de una, el sistema cobra mal y nadie se entera hasta el cierre.


# ---------------------------------------------------------------------------
# EJEMPLO 2: bien - una sola fuente de verdad
# ---------------------------------------------------------------------------

IVA = 0.19

DESCUENTOS = {
    "estudiante": 0.20,
    "jubilado": 0.30,
    "normal": 0.0,
}


def precio_final(precio, tipo_cliente="normal"):
    """Aplica el descuento del tipo de cliente y suma el IVA."""
    descuento = DESCUENTOS[tipo_cliente]
    subtotal = precio * (1 - descuento)
    return round(subtotal * (1 + IVA), 2)


# Ahora el IVA vive en un solo lugar y agregar un tipo de cliente nuevo
# es una linea en el diccionario, no una funcion entera copiada.



"""
PRINCIPIO YAGNI - You Aren't Gonna Need It
==========================================
"""


# ---------------------------------------------------------------------------
# EJEMPLO 3: mal - construir para un futuro que nadie pidio
# ---------------------------------------------------------------------------

# Pedido real: "guardar la lista de contactos en un archivo".

class GuardadorDeContactos:
    """Guarda contactos... en cualquier formato, algun dia, quizas."""

    def __init__(self, formato="json", compresion=None, encriptado=False,
                 destino_remoto=None, reintentos=3, version_esquema=1):
        self.formato = formato
        self.compresion = compresion
        self.encriptado = encriptado
        self.destino_remoto = destino_remoto
        self.reintentos = reintentos
        self.version_esquema = version_esquema

    def guardar(self, contactos, ruta):
        datos = self._serializar(contactos)
        if self.compresion:
            datos = self._comprimir(datos)
        if self.encriptado:
            datos = self._encriptar(datos)
        if self.destino_remoto:
            return self._subir_con_reintentos(datos)
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(datos)

    def _serializar(self, contactos):
        if self.formato == "json":
            return json.dumps(contactos, ensure_ascii=False)
        raise NotImplementedError("xml y csv se implementan cuando hagan falta")

    def _comprimir(self, datos):
        raise NotImplementedError("todavia nadie pidio comprimir")

    def _encriptar(self, datos):
        raise NotImplementedError("todavia nadie pidio encriptar")

    def _subir_con_reintentos(self, datos):
        raise NotImplementedError("todavia no hay servidor remoto")


# El problema: seis parametros, cuatro metodos y solo UNO funciona.
# El resto es codigo muerto que hay que leer, testear y mantener,
# y cuando de verdad pidan encriptado, el requisito no va a coincidir
# con lo que imaginaste hoy.


# ---------------------------------------------------------------------------
# EJEMPLO 3: bien - resolver lo que se pidio
# ---------------------------------------------------------------------------

def guardar_contactos(contactos, ruta):
    """Guarda la lista de contactos como JSON."""
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(contactos, archivo, ensure_ascii=False, indent=2)


# Cuatro lineas, cero ramas muertas. El dia que pidan comprimir o subir
# a un servidor, se agrega ahi con el requisito real sobre la mesa.



"""
PRINCIPIOS SOLID
================
S - Single Responsibility  (una sola razon para cambiar)
O - Open/Closed            (abierto a extension, cerrado a modificacion)
L - Liskov Substitution    (el hijo debe poder reemplazar al padre)
I - Interface Segregation   (interfaces chicas y especificas)
D - Dependency Inversion   (depender de abstracciones, no de concretos)
"""


# ---------------------------------------------------------------------------
# S - SINGLE RESPONSIBILITY: mal - una clase que hace de todo
# ---------------------------------------------------------------------------

class FacturaTodoEnUno:
    """Calcula, guarda en la base y manda el mail. Tres trabajos, una clase."""

    def __init__(self, items, cliente):
        self.items = items
        self.cliente = cliente

    def calcular_total(self):
        return sum(item["precio"] * item["cantidad"] for item in self.items)

    def guardar_en_base(self, conexion):
        conexion.execute(
            "INSERT INTO facturas (cliente, total) VALUES (?, ?)",
            (self.cliente, self.calcular_total()),
        )

    def enviar_por_email(self, servidor_smtp):
        cuerpo = f"Total a pagar: {self.calcular_total()}"
        servidor_smtp.send(self.cliente["email"], cuerpo)


# El problema: esta clase cambia si cambian las reglas de facturacion,
# si cambia el motor de base de datos O si cambia el proveedor de email.
# Tres motivos distintos para tocar el mismo archivo, tres equipos pisandose.


# S - SINGLE RESPONSIBILITY: bien - cada clase con un solo motivo de cambio
class Factura:
    """Solo sabe de facturacion."""

    def __init__(self, items, cliente):
        self.items = items
        self.cliente = cliente

    def calcular_total(self):
        return sum(item["precio"] * item["cantidad"] for item in self.items)


class RepositorioFacturas:
    """Solo sabe de persistencia."""

    def __init__(self, conexion):
        self.conexion = conexion

    def guardar(self, factura):
        self.conexion.execute(
            "INSERT INTO facturas (cliente, total) VALUES (?, ?)",
            (factura.cliente, factura.calcular_total()),
        )


class NotificadorFacturas:
    """Solo sabe de notificaciones."""

    def __init__(self, servidor_smtp):
        self.servidor_smtp = servidor_smtp

    def notificar(self, factura):
        cuerpo = f"Total a pagar: {factura.calcular_total()}"
        self.servidor_smtp.send(factura.cliente["email"], cuerpo)


# ---------------------------------------------------------------------------
# O - OPEN/CLOSED: mal - hay que editar la funcion por cada transportista nuevo
# ---------------------------------------------------------------------------

def costo_envio_malo(pedido, transportista):
    if transportista == "correo":
        return pedido["peso"] * 1.5
    elif transportista == "andreani":
        return pedido["peso"] * 2.0 + 300
    elif transportista == "oca":
        return pedido["peso"] * 1.8 + 150
    # ... y cada transportista nuevo obliga a abrir y modificar esta funcion,
    # arriesgando romper los que ya funcionaban.
    raise ValueError("transportista desconocido")


# O - OPEN/CLOSED: bien - se extiende agregando, no modificando
class EnvioCorreo:
    def costo(self, pedido):
        return pedido["peso"] * 1.5


class EnvioAndreani:
    def costo(self, pedido):
        return pedido["peso"] * 2.0 + 300


class EnvioOca:
    def costo(self, pedido):
        return pedido["peso"] * 1.8 + 150


def costo_envio(pedido, transportista):
    """Calcula el envio delegando en la estrategia del transportista."""
    return transportista.costo(pedido)


# Sumar "EnvioViaCargo" es crear una clase nueva. El codigo ya probado
# no se toca, asi que no se puede romper.


# ---------------------------------------------------------------------------
# L - LISKOV: mal - el hijo rompe el contrato del padre
# ---------------------------------------------------------------------------

class Rectangulo:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto

    def set_ancho(self, ancho):
        self.ancho = ancho

    def set_alto(self, alto):
        self.alto = alto

    def area(self):
        return self.ancho * self.alto


class Cuadrado(Rectangulo):
    """Un cuadrado ES un rectangulo... en geometria, no en codigo."""

    def set_ancho(self, ancho):
        self.ancho = ancho
        self.alto = ancho          # efecto colateral que el padre no promete

    def set_alto(self, alto):
        self.ancho = alto
        self.alto = alto


def test_area(rectangulo):
    """Codigo que funciona con Rectangulo y explota con Cuadrado."""
    rectangulo.set_ancho(5)
    rectangulo.set_alto(4)
    return rectangulo.area()       # espera 20; con Cuadrado devuelve 16


# L - LISKOV: bien - no forzar la herencia, modelar lo que de verdad comparten
class Figura:
    def area(self):
        raise NotImplementedError


class RectanguloOk(Figura):
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto

    def area(self):
        return self.ancho * self.alto


class CuadradoOk(Figura):
    def __init__(self, lado):
        self.lado = lado

    def area(self):
        return self.lado ** 2


# Ahora cualquier codigo que reciba una Figura y llame area() funciona
# con las dos, sin sorpresas.


# ---------------------------------------------------------------------------
# I - INTERFACE SEGREGATION: mal - una interfaz gorda que obliga a mentir
# ---------------------------------------------------------------------------

class DispositivoMultifuncion:
    """Toda impresora debe imprimir, escanear y mandar fax. Segun quien?"""

    def imprimir(self, documento):
        raise NotImplementedError

    def escanear(self, documento):
        raise NotImplementedError

    def enviar_fax(self, documento):
        raise NotImplementedError


class ImpresoraSimple(DispositivoMultifuncion):
    def imprimir(self, documento):
        print(f"imprimiendo {documento}")

    def escanear(self, documento):
        raise NotImplementedError("esta impresora no escanea")

    def enviar_fax(self, documento):
        raise NotImplementedError("esta impresora no manda fax")


# El problema: ImpresoraSimple hereda metodos que no puede cumplir.
# Quien la use tiene que saber de antemano cuales explotan.


# I - INTERFACE SEGREGATION: bien - interfaces chicas, se combinan las que hagan falta
class Imprimible:
    def imprimir(self, documento):
        raise NotImplementedError


class Escaneable:
    def escanear(self, documento):
        raise NotImplementedError


class ImpresoraBasica(Imprimible):
    def imprimir(self, documento):
        print(f"imprimiendo {documento}")


class ImpresoraConEscaner(Imprimible, Escaneable):
    def imprimir(self, documento):
        print(f"imprimiendo {documento}")

    def escanear(self, documento):
        print(f"escaneando {documento}")


# ---------------------------------------------------------------------------
# D - DEPENDENCY INVERSION: mal - la logica de negocio clavada a un detalle
# ---------------------------------------------------------------------------

class ConexionMySQL:
    def query(self, sql):
        return [{"id": 1, "nombre": "Ana"}]


class ServicioUsuariosMalo:
    def __init__(self):
        self.base = ConexionMySQL()    # se instancia sola: imposible de cambiar

    def buscar_activos(self):
        return self.base.query("SELECT * FROM usuarios WHERE activo = 1")


# El problema: migrar a Postgres obliga a editar la logica de negocio,
# y para testear necesitas una base MySQL levantada de verdad.


# D - DEPENDENCY INVERSION: bien - la dependencia entra desde afuera
class ServicioUsuarios:
    """Depende de 'algo que sepa hacer query()', no de MySQL."""

    def __init__(self, repositorio):
        self.repositorio = repositorio

    def buscar_activos(self):
        return self.repositorio.query("SELECT * FROM usuarios WHERE activo = 1")


class RepositorioFalso:
    """Para los tests: sin base de datos, sin red, instantaneo."""

    def query(self, sql):
        return [{"id": 99, "nombre": "usuario de prueba"}]


# servicio = ServicioUsuarios(ConexionMySQL())     -> produccion
# servicio = ServicioUsuarios(RepositorioFalso())  -> tests

