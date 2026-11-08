from abc import ABC, abstractmethod
from datetime import datetime


class ErrorSistema(Exception):
    pass


class DatoInvalidoError(ErrorSistema):
    pass


class ParametroFaltanteError(ErrorSistema):
    pass


class ReservaInvalidaError(ErrorSistema):
    pass


class ServicioNoDisponibleError(ErrorSistema):
    pass


class EstadoInvalidoError(ErrorSistema):
    pass


class RegistroLogs:
    ARCHIVO = "sistema_fj_logs.txt"

    @classmethod
    def _escribir(cls, nivel, mensaje):
        marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{marca}] [{nivel}] {mensaje}\n"
        try:
            with open(cls.ARCHIVO, "a", encoding="utf-8") as f:
                f.write(linea)
        except Exception:
            pass

    @classmethod
    def info(cls, mensaje):
        cls._escribir("INFO", mensaje)

    @classmethod
    def error(cls, mensaje):
        cls._escribir("ERROR", mensaje)

    @classmethod
    def advertencia(cls, mensaje):
        cls._escribir("ADVERTENCIA", mensaje)


class EntidadBase(ABC):

    @abstractmethod
    def validar_datos(self):
        pass

    @abstractmethod
    def __str__(self):
        pass


class Cliente(EntidadBase):
    def __init__(self, identificacion, nombre, correo, telefono):
        self.__identificacion = identificacion
        self.__nombre = nombre
        self.__correo = correo
        self.__telefono = telefono
        self.validar_datos()

    @property
    def identificacion(self):
        return self.__identificacion

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def validar_datos(self):
        errores = []
        if not self.__identificacion or len(self.__identificacion.strip()) < 4:
            errores.append("Identificación muy corta o vacía")
        if not self.__nombre or len(self.__nombre.strip()) < 3:
            errores.append("Nombre debe tener al menos 3 caracteres")
        if "@" not in self.__correo or "." not in self.__correo:
            errores.append("Formato de correo inválido")
        if len(self.__telefono) < 7:
            errores.append("Teléfono incompleto")
        if errores:
            mensaje = " | ".join(errores)
            RegistroLogs.error(f"Datos inválidos en cliente: {mensaje}")
            raise DatoInvalidoError(f"No se pudo registrar cliente: {mensaje}")

    def __str__(self):
        return f"Cliente: {self.__nombre} | ID: {self.__identificacion} | Correo: {self.__correo}"


class Servicio(EntidadBase):
    def __init__(self, codigo, nombre, tarifa_base, disponible=True):
        self.codigo = codigo
        self.nombre = nombre
        self.tarifa_base = float(tarifa_base) if tarifa_base else 0
        self.disponible = disponible
        self.validar_datos()

    def validar_datos(self):
        if not self.codigo or not self.nombre:
            raise ParametroFaltanteError("Código y nombre del servicio son obligatorios")
        if self.tarifa_base < 0:
            raise DatoInvalidoError("La tarifa no puede ser negativa")

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        pass

    @abstractmethod
    def describir(self):
        pass

    def __str__(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return f"[{self.codigo}] {self.nombre} - Tarifa base: ${self.tarifa_base:,.2f} | {estado}"


class ReservaSala(Servicio):
    def __init__(self, codigo, nombre, tarifa_base, capacidad, disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        self.capacidad = capacidad

    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        if duracion <= 0:
            raise DatoInvalidoError("La duración debe ser mayor a 0 horas")
        subtotal = self.tarifa_base * duracion
        if self.capacidad > 10:
            subtotal *= 1.15
        valor_impuesto = subtotal * impuesto
        valor_descuento = subtotal * descuento
        total = subtotal + valor_impuesto - valor_descuento
        return max(total, 0)

    def describir(self):
        return f"Sala: {self.nombre} | Capacidad: {self.capacidad} personas | Tarifa/hora: ${self.tarifa_base:,.2f}"

    def __str__(self):
        return f"{super().__str__()} | Capacidad: {self.capacidad} personas"


class AlquilerEquipos(Servicio):
    def __init__(self, codigo, nombre, tarifa_base, cantidad_equipos, seguro_incluido=True, disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        self.cantidad_equipos = cantidad_equipos
        self.seguro_incluido = seguro_incluido

    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        if duracion <= 0:
            raise DatoInvalidoError("Días de alquiler deben ser mayor a 0")
        subtotal = self.tarifa_base * duracion * self.cantidad_equipos
        if not self.seguro_incluido:
            subtotal += 50000 * self.cantidad_equipos
        valor_impuesto = subtotal * impuesto
        valor_descuento = subtotal * descuento
        total = subtotal + valor_impuesto - valor_descuento
        return max(total, 0)

    def describir(self):
        seguro = "con seguro incluido" if self.seguro_incluido else "sin seguro"
        return f"Equipos: {self.nombre} | Cantidad: {self.cantidad_equipos} | {seguro} | Tarifa/día: ${self.tarifa_base:,.2f}"

    def __str__(self):
        return f"{super().__str__()} | Equipos: {self.cantidad_equipos}"


class AsesoriaEspecializada(Servicio):
    def __init__(self, codigo, nombre, tarifa_base, especialista, area_conocimiento, disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        self.especialista = especialista
        self.area_conocimiento = area_conocimiento

    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        if duracion <= 0:
            raise DatoInvalidoError("Horas de asesoría deben ser mayores a 0")
        subtotal = self.tarifa_base * duracion
        if "Senior" in self.especialista:
            subtotal *= 1.25
        valor_impuesto = subtotal * impuesto
        valor_descuento = subtotal * descuento
        total = subtotal + valor_impuesto - valor_descuento
        return max(total, 0)

    def describir(self):
        return f"Asesoría: {self.nombre} | Especialista: {self.especialista} | Área: {self.area_conocimiento} | Valor/hora: ${self.tarifa_base:,.2f}"

    def __str__(self):
        return f"{super().__str__()} | Especialista: {self.especialista}"


class Reserva:
    ESTADOS = {"PENDIENTE", "CONFIRMADA", "CANCELADA", "COMPLETADA"}

    def __init__(self, cliente, servicio, duracion, impuesto=0.19, descuento=0.0):
        if not cliente:
            raise ParametroFaltanteError("Se requiere un cliente para la reserva")
        if not servicio:
            raise ParametroFaltanteError("Se requiere un servicio para la reserva")
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.impuesto = impuesto
        self.descuento = descuento
        self.estado = "PENDIENTE"
        self.monto_total = 0.0
        self._validar_creacion()

    def _validar_creacion(self):
        try:
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio {self.servicio.nombre} no está disponible")
            if self.duracion <= 0:
                raise DatoInvalidoError("El tiempo solicitado debe ser mayor a cero")
            self.monto_total = self.servicio.calcular_costo(
                self.duracion, self.impuesto, self.descuento
            )
            RegistroLogs.info(f"Reserva creada: {self.cliente.nombre} -> {self.servicio.nombre}")
        except (DatoInvalidoError, ServicioNoDisponibleError) as e:
            RegistroLogs.error(f"Fallo al crear reserva: {e}")
            raise ReservaInvalidaError(f"No se pudo crear la reserva: {e}") from e

    def confirmar(self):
        try:
            if self.estado != "PENDIENTE":
                raise EstadoInvalidoError(f"No se puede confirmar: estado actual es {self.estado}")
            self.estado = "CONFIRMADA"
            RegistroLogs.info(f"Reserva confirmada: {self.cliente.nombre} - {self.servicio.nombre}")
            return f"Reserva confirmada | Total: ${self.monto_total:,.2f}"
        except EstadoInvalidoError as e:
            RegistroLogs.error(f"Error al confirmar: {e}")
            raise

    def cancelar(self, motivo="No especificado"):
        try:
            if self.estado in ["COMPLETADA", "CANCELADA"]:
                raise EstadoInvalidoError(f"No se puede cancelar una reserva {self.estado}")
            self.estado = "CANCELADA"
            RegistroLogs.advertencia(
                f"Reserva cancelada: {self.cliente.nombre} | Motivo: {motivo}"
            )
            return f"Reserva cancelada: {motivo}"
        except EstadoInvalidoError as e:
            RegistroLogs.error(f"Fallo cancelación: {e}")
            raise

    def __str__(self):
        return (
            "====================================\n"
            f"RESERVA | Estado: {self.estado}\n"
            f"Cliente: {self.cliente.nombre} ({self.cliente.identificacion})\n"
            f"Servicio: {self.servicio.nombre}\n"
            f"Duración: {self.duracion} horas/días\n"
            f"Monto Total: ${self.monto_total:,.2f}\n"
            "===================================="
        )


class SistemaFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []
        RegistroLogs.info("INICIO DEL SISTEMA Software FJ")

    def registrar_cliente(self, identificacion, nombre, correo, telefono):
        try:
            cliente = Cliente(identificacion, nombre, correo, telefono)
            self.clientes.append(cliente)
            return f"Cliente registrado: {nombre}"
        except DatoInvalidoError as e:
            return f"Error registro cliente: {e}"

    def registrar_servicio(self, tipo, **datos):
        try:
            servicio = None
            if tipo == "sala":
                servicio = ReservaSala(**datos)
            elif tipo == "equipos":
                servicio = AlquilerEquipos(**datos)
            elif tipo == "asesoria":
                servicio = AsesoriaEspecializada(**datos)
            else:
                raise DatoInvalidoError(f"Tipo de servicio desconocido: {tipo}")
            self.servicios.append(servicio)
            return f"Servicio registrado: {servicio.nombre}"
        except (ParametroFaltanteError, DatoInvalidoError) as e:
            return f"Error registro servicio: {e}"

    def crear_reserva(self, id_cliente, cod_servicio, duracion, impuesto=0.19, descuento=0.0):
        try:
            cliente_encontrado = None
            for c in self.clientes:
                if c.identificacion == id_cliente:
                    cliente_encontrado = c
                    break
            if not cliente_encontrado:
                raise ParametroFaltanteError(f"Cliente con identificación {id_cliente} no existe")

            servicio_encontrado = None
            for s in self.servicios:
                if s.codigo == cod_servicio:
                    servicio_encontrado = s
                    break
            if not servicio_encontrado:
                raise ParametroFaltanteError(f"Servicio con código {cod_servicio} no existe")

            reserva = Reserva(cliente_encontrado, servicio_encontrado, duracion, impuesto, descuento)
            self.reservas.append(reserva)
            return reserva

        except (ParametroFaltanteError, ReservaInvalidaError) as e:
            RegistroLogs.error(f"Fallo creación reserva: {e}")
            return f"Error creando reserva: {e}"
        except Exception as e:
            RegistroLogs.error(f"Error inesperado en reserva: {e}")
            return f"Error inesperado: {e}"


if __name__ == "__main__":
    sistema = SistemaFJ()

    print("=== Operación 1: Registrar cliente válido ===")
    print(sistema.registrar_cliente("1001234567", "María López", "maria@correo.com", "3001234567"))

    print("\n=== Operación 2: Registrar cliente con datos inválidos ===")
    print(sistema.registrar_cliente("123", "Ma", "correo_invalido", "12345"))

    print("\n=== Operación 3: Registrar segundo cliente válido ===")
    print(sistema.registrar_cliente("1002345678", "Carlos Pérez", "carlos@correo.com", "3109876543"))

    print("\n=== Operación 4: Registrar servicio Sala válido ===")
    print(sistema.registrar_servicio("sala", codigo="SAL001", nombre="Sala de Conferencias A", tarifa_base=150000, capacidad=15))

    print("\n=== Operación 5: Registrar servicio con tarifa negativa ===")
    print(sistema.registrar_servicio("sala", codigo="SAL002", nombre="Sala Pequeña", tarifa_base=-5000, capacidad=5))

    print("\n=== Operación 6: Registrar servicio Alquiler Equipos ===")
    print(sistema.registrar_servicio("equipos", codigo="EQP001", nombre="Equipos de Edición", tarifa_base=25000, cantidad_equipos=5, seguro_incluido=True))

    print("\n=== Operación 7: Registrar servicio Asesoría ===")
    print(sistema.registrar_servicio("asesoria", codigo="ASE001", nombre="Asesoría en Programación", tarifa_base=80000, especialista="Ing. Ana Senior", area_conocimiento="Desarrollo de Software"))

    print("\n=== Operación 8: Crear reserva válida ===")
    reserva1 = sistema.crear_reserva("1001234567", "SAL001", 3, descuento=0.10)
    if isinstance(reserva1, Reserva):
        print(reserva1)
        print(reserva1.confirmar())
    else:
        print(reserva1)

    print("\n=== Operación 9: Crear reserva con cliente inexistente ===")
    print(sistema.crear_reserva("9999999999", "SAL001", 2))

    print("\n=== Operación 10: Crear reserva con duración inválida ===")
    print(sistema.crear_reserva("1002345678", "EQP001", 0))

    print("\n=== Operación 11: Cancelar reserva válida ===")
    reserva2 = sistema.crear_reserva("1002345678", "ASE001", 2)
    if isinstance(reserva2, Reserva):
        print(reserva2.cancelar("Cambio de horario"))
    else:
        print(reserva2)

    print("\n=== Operación 12: Intentar confirmar reserva ya cancelada ===")
    try:
        if isinstance(reserva2, Reserva):
            print(reserva2.confirmar())
    except EstadoInvalidoError as e:
        print(f"Resultado esperado: {e}")

    print("\n=== Fin de las operaciones ===")
    print(f"Clientes registrados: {len(sistema.clientes)}")
    print(f"Servicios registrados: {len(sistema.servicios)}")
    print(f"Reservas procesadas: {len(sistema.reservas)}")