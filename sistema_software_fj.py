from abc import ABC, abstractmethod
from datetime import datetime
from functools import singledispatchmethod
import re
from typing import Any, Dict, List, Optional


# ==============================================================================
# 1. JERARQUÍA DE EXCEPCIONES PERSONALIZADAS
# ==============================================================================


class ErrorSistemaFJ(Exception):
    """Excepción base para todos los errores del sistema de Software FJ."""

    def __init__(self, mensaje: str, codigo: str = "ERR-GENERAL"):
        self.codigo = codigo
        super().__init__(f"[{codigo}] {mensaje}")


class DatoInvalidoError(ErrorSistemaFJ):
    """Se lanza cuando un dato no cumple con el formato o rango esperado."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR-DATO-INVALIDO")


class ParametroFaltanteError(ErrorSistemaFJ):
    """Se lanza cuando faltan parámetros obligatorios o son nulos/vacíos."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR-PARAM-FALTANTE")


class OperacionNoPermitidaError(ErrorSistemaFJ):
    """Se lanza al intentar ejecutar una acción inválida según el estado actual."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR-OPERACION-NO-PERMITIDA")


class ReservaInvalidaError(ErrorSistemaFJ):
    """Se lanza cuando falla el proceso de creación o gestión de una reserva."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR-RESERVA-INVALIDA")


class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Se lanza cuando el servicio solicitado está ocupado o inactivo."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR-SERVICIO-NO-DISPONIBLE")


class CalculoInconsistenteError(ErrorSistemaFJ):
    """Se lanza cuando los parámetros financieros arrojan valores ilógicos."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR-CALCULO-INCONSISTENTE")


# ==============================================================================
# 2. GESTOR DE ARCHIVO DE LOGS (PERSISTENCIA DE EVENTOS Y ERRORES)
# ==============================================================================


class GestorLogs:
    """Administra el registro en archivo plano de eventos y excepciones."""

    def __init__(self, ruta_archivo: str = "software_fj_eventos.log"):
        self.ruta_archivo = ruta_archivo
        self._escribir_cabecera()

    def _escribir_cabecera(self) -> None:
        with open(self.ruta_archivo, mode="a", encoding="utf-8") as archivo:
            archivo.write("\n" + "=" * 80 + "\n")
            archivo.write(
                f"INICIO DE SESIÓN DEL SISTEMA SOFTWARE FJ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            archivo.write("=" * 80 + "\n")

    def registrar_evento(self, nivel: str, modulo: str, mensaje: str) -> None:
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{marca_tiempo}] [{nivel.upper()}] [{modulo}] {mensaje}\n"
        with open(self.ruta_archivo, mode="a", encoding="utf-8") as archivo:
            archivo.write(linea)

    def registrar_error(
        self, modulo: str, error: Exception, contexto: str = ""
    ) -> None:
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        causa = f" | Causa raíz: {repr(error.__cause__)}" if error.__cause__ else ""
        detalle_ctx = f" | Contexto: {contexto}" if contexto else ""
        linea = (
            f"[{marca_tiempo}] [ERROR] [{modulo}] "
            f"{type(error).__name__}: {error}{detalle_ctx}{causa}\n"
        )
        with open(self.ruta_archivo, mode="a", encoding="utf-8") as archivo:
            archivo.write(linea)


# ==============================================================================
# 3. CLASE ABSTRACTA BASE DEL SISTEMA
# ==============================================================================


class EntidadSistema(ABC):
    """Clase abstracta que representa cualquier entidad gestionable en Software FJ."""

    def __init__(self, entidad_id: str):
        if not entidad_id or not str(entidad_id).strip():
            raise ParametroFaltanteError("El identificador de la entidad es obligatorio.")
        self._id: str = str(entidad_id).strip()
        self._fecha_creacion: datetime = datetime.now()

    @property
    def id(self) -> str:
        return self._id

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    @abstractmethod
    def validar(self) -> None:
        """Valida la integridad interna de la entidad."""
        pass

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Devuelve una representación legible de la entidad."""
        pass


# ==============================================================================
# 4. CLASE CLIENTE (ENCAPSULACIÓN Y VALIDACIONES ESTRICTAS)
# ==============================================================================


class Cliente(EntidadSistema):
    """Representa un cliente corporativo o individual de Software FJ."""

    def __init__(
        self, cliente_id: str, documento: str, nombre: str, correo: str, telefono: str
    ):
        super().__init__(cliente_id)
        self.documento = documento
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.validar()

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El documento del cliente no puede estar vacío.")
        valor_limpio = str(valor).strip()
        if not re.match(r"^[A-Za-z0-9\-]{5,20}$", valor_limpio):
            raise DatoInvalidoError(
                f"Documento '{valor_limpio}' inválido. Debe tener entre 5 y 20 caracteres alfanuméricos."
            )
        self.__documento = valor_limpio

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El nombre del cliente es obligatorio.")
        valor_limpio = str(valor).strip()
        if len(valor_limpio) < 3 or any(char.isdigit() for char in valor_limpio):
            raise DatoInvalidoError(
                f"Nombre '{valor_limpio}' inválido. Debe tener al menos 3 letras y no contener números."
            )
        self.__nombre = valor_limpio

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El correo electrónico es obligatorio.")
        valor_limpio = str(valor).strip().lower()
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", valor_limpio):
            raise DatoInvalidoError(f"Formato de correo electrónico inválido: '{valor}'.")
        self.__correo = valor_limpio

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El teléfono de contacto es obligatorio.")
        valor_limpio = str(valor).strip()
        if not re.match(r"^\+?[0-9]{7,15}$", valor_limpio):
            raise DatoInvalidoError(
                f"Teléfono '{valor_limpio}' inválido. Debe contener entre 7 y 15 dígitos."
            )
        self.__telefono = valor_limpio

    def validar(self) -> None:
        _ = (self.__documento, self.__nombre, self.__correo, self.__telefono)

    def obtener_resumen(self) -> str:
        return (
            f"Cliente [{self.id}] | {self.nombre} (Doc: {self.documento}) | "
            f"Email: {self.correo} | Tel: {self.telefono}"
        )


# ==============================================================================
# 5. CLASE ABSTRACTA SERVICIO Y ESPECIALIZACIONES (POLIMORFISMO Y SOBRECARGA)
# ==============================================================================


class Servicio(EntidadSistema):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(self, servicio_id: str, nombre: str, tarifa_hora: Any):
        super().__init__(servicio_id)
        if not nombre or not str(nombre).strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        self._nombre: str = str(nombre).strip()

        try:
            tarifa_convertida = float(tarifa_hora)
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError(
                f"La tarifa por hora '{tarifa_hora}' debe ser un valor numérico."
            ) from exc

        if tarifa_convertida <= 0:
            raise DatoInvalidoError(
                f"La tarifa por hora ({tarifa_convertida}) debe ser mayor que cero."
            )

        self._tarifa_hora: float = tarifa_convertida
        self._disponible: bool = True

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        if not isinstance(estado, bool):
            raise DatoInvalidoError("El estado de disponibilidad debe ser booleano.")
        self._disponible = estado

    @abstractmethod
    def validar_parametros(self) -> None:
        """Valida los parámetros específicos de cada tipo de servicio."""
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Retorna la descripción detallada según el tipo de servicio."""
        pass

    @abstractmethod
    def calcular_costo_base(self, duracion_horas: float) -> float:
        """Calcula el costo base aplicando reglas propias de cada servicio."""
        pass

    # --- Métodos sobrecargados para el cálculo financiero ---

    @singledispatchmethod
    def calcular_costo_final(self, parametro: Any, **kwargs) -> float:
        """Método sobrecargado según el tipo de parámetro recibido."""
        raise DatoInvalidoError(
            f"Tipo de parámetro no soportado para cálculo de costo: {type(parametro).__name__}"
        )

    @calcular_costo_final.register
    def _(
        self,
        duracion_horas: int,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        recargo_fijo: float = 0.0,
    ) -> float:
        """Sobrecarga 1: Cálculo estándar a partir de horas enteras."""
        return self._ejecutar_formula_financiera(
            float(duracion_horas), impuesto, descuento, recargo_fijo
        )

    @calcular_costo_final.register
    def _(
        self,
        duracion_horas: float,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        recargo_fijo: float = 0.0,
    ) -> float:
        """Sobrecarga 2: Cálculo preciso a partir de fracciones de hora."""
        return self._ejecutar_formula_financiera(
            duracion_horas, impuesto, descuento, recargo_fijo
        )

    @calcular_costo_final.register
    def _(self, configuracion: dict) -> float:
        """Sobrecarga 3: Cálculo mediante diccionario de parámetros."""
        if "duracion" not in configuracion:
            raise ParametroFaltanteError(
                "El diccionario de cálculo debe incluir la clave 'duracion'."
            )
        return self._ejecutar_formula_financiera(
            float(configuracion["duracion"]),
            float(configuracion.get("impuesto", 0.19)),
            float(configuracion.get("descuento", 0.0)),
            float(configuracion.get("recargo_fijo", 0.0)),
        )

    def _ejecutar_formula_financiera(
        self,
        duracion: float,
        impuesto: float,
        descuento: float,
        recargo_fijo: float,
    ) -> float:
        if duracion <= 0:
            raise CalculoInconsistenteError("La duración para el cálculo debe ser > 0.")
        if not (0 <= impuesto <= 1):
            raise CalculoInconsistenteError(
                f"El impuesto ({impuesto}) debe estar entre 0.0 y 1.0."
            )
        if not (0 <= descuento < 1):
            raise CalculoInconsistenteError(
                f"El descuento ({descuento}) debe estar entre 0.0 y 0.99."
            )
        if recargo_fijo < 0:
            raise CalculoInconsistenteError("El recargo fijo no puede ser negativo.")

        subtotal = self.calcular_costo_base(duracion) + recargo_fijo
        subtotal_con_descuento = subtotal * (1 - descuento)
        total = subtotal_con_descuento * (1 + impuesto)

        if total <= 0:
            raise CalculoInconsistenteError("El costo total calculado no es consistente.")

        return round(total, 2)

    def validar(self) -> None:
        self.validar_parametros()

    def obtener_resumen(self) -> str:
        estado = "Disponible" if self.disponible else "Ocupado"
        return f"Servicio [{self.id}] ({estado}) | {self.describir_servicio()}"


class ReservaSala(Servicio):
    """Servicio especializado: Reserva de salas de reuniones o capacitación."""

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        tarifa_hora: float,
        capacidad_personas: int,
        tiene_videoconferencia: bool = True,
    ):
        super().__init__(servicio_id, nombre, tarifa_hora)
        self.capacidad_personas = capacidad_personas
        self.tiene_videoconferencia = tiene_videoconferencia
        self.validar()

    def validar_parametros(self) -> None:
        if not isinstance(self.capacidad_personas, int) or self.capacidad_personas <= 0:
            raise DatoInvalidoError(
                "La capacidad de la sala debe ser un entero positivo."
            )
        if self.capacidad_personas > 100:
            raise DatoInvalidoError(
                "La capacidad máxima permitida para salas es de 100 personas."
            )

    def describir_servicio(self) -> str:
        equipo_av = "con Videoconferencia" if self.tiene_videoconferencia else "Básica"
        return (
            f"Sala '{self.nombre}' | Capacidad: {self.capacidad_personas} pers. "
            f"({equipo_av}) | Tarifa: ${self.tarifa_hora:,.2f}/h"
        )

    def calcular_costo_base(self, duracion_horas: float) -> float:
        costo = self.tarifa_hora * duracion_horas
        if self.tiene_videoconferencia:
            costo += 15.0 * duracion_horas  # Suplemento técnico por hora
        return costo


class AlquilerEquipo(Servicio):
    """Servicio especializado: Alquiler de hardware y equipos tecnológicos."""

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        tarifa_hora: float,
        categoria_equipo: str,
        serial: str,
        deposito_seguridad: float = 50.0,
    ):
        super().__init__(servicio_id, nombre, tarifa_hora)
        self.categoria_equipo = categoria_equipo
        self.serial = serial
        self.deposito_seguridad = deposito_seguridad
        self.validar()

    def validar_parametros(self) -> None:
        if not self.categoria_equipo or not str(self.categoria_equipo).strip():
            raise ParametroFaltanteError("La categoría del equipo es obligatoria.")
        if not self.serial or len(str(self.serial).strip()) < 4:
            raise DatoInvalidoError("El número de serial del equipo es inválido.")
        if self.deposito_seguridad < 0:
            raise DatoInvalidoError("El depósito de seguridad no puede ser negativo.")

    def describir_servicio(self) -> str:
        return (
            f"Equipo '{self.nombre}' [{self.categoria_equipo} - S/N: {self.serial}] | "
            f"Tarifa: ${self.tarifa_hora:,.2f}/h + Depósito: ${self.deposito_seguridad:,.2f}"
        )

    def calcular_costo_base(self, duracion_horas: float) -> float:
        # Si se alquila más de 8 horas, se aplica tarifa reducida del 10% en el alquiler
        tarifa_efectiva = (
            self.tarifa_hora * 0.90 if duracion_horas > 8 else self.tarifa_hora
        )
        return (tarifa_efectiva * duracion_horas) + self.deposito_seguridad


class AsesoriaEspecializada(Servicio):
    """Servicio especializado: Consultoría técnica, arquitectura e ingeniería."""

    NIVELES_VALIDOS = {"JUNIOR", "SENIOR", "ARQUITECTO"}

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        tarifa_hora: float,
        especialidad: str,
        nivel_consultor: str,
    ):
        super().__init__(servicio_id, nombre, tarifa_hora)
        self.especialidad = especialidad
        self.nivel_consultor = (
            str(nivel_consultor).strip().upper() if nivel_consultor else ""
        )
        self.validar()

    def validar_parametros(self) -> None:
        if not self.especialidad or not str(self.especialidad).strip():
            raise ParametroFaltanteError("La especialidad de la asesoría es obligatoria.")
        if self.nivel_consultor not in self.NIVELES_VALIDOS:
            raise DatoInvalidoError(
                f"Nivel de consultor '{self.nivel_consultor}' no válido. "
                f"Opciones: {', '.join(self.NIVELES_VALIDOS)}."
            )

    def describir_servicio(self) -> str:
        return (
            f"Asesoría '{self.nombre}' | Área: {self.especialidad} "
            f"(Nivel: {self.nivel_consultor}) | Tarifa: ${self.tarifa_hora:,.2f}/h"
        )

    def calcular_costo_base(self, duracion_horas: float) -> float:
        multiplicadores = {"JUNIOR": 1.0, "SENIOR": 1.25, "ARQUITECTO": 1.5}
        factor = multiplicadores[self.nivel_consultor]
        return self.tarifa_hora * duracion_horas * factor


# ==============================================================================
# 6. CLASE RESERVA (GESTIÓN DE ESTADOS Y PROCESAMIENTO)
# ==============================================================================


class Reserva(EntidadSistema):
    """Integra Cliente, Servicio, duración y ciclo de vida de la reserva."""

    ESTADOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "COMPLETADA")

    def __init__(
        self,
        reserva_id: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: float,
        impuesto: float = 0.19,
        descuento: float = 0.0,
    ):
        super().__init__(reserva_id)
        if not isinstance(cliente, Cliente):
            raise ParametroFaltanteError("Se requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ParametroFaltanteError("Se requiere una instancia válida de Servicio.")

        try:
            duracion_num = float(duracion_horas)
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError("La duración de la reserva debe ser numérica.") from exc

        if duracion_num <= 0 or duracion_num > 240:
            raise ReservaInvalidaError(
                "La duración de la reserva debe estar entre 0.5 y 240 horas."
            )

        self._cliente: Cliente = cliente
        self._servicio: Servicio = servicio
        self._duracion_horas: float = duracion_num
        self._impuesto: float = impuesto
        self._descuento: float = descuento
        self._estado: str = "PENDIENTE"
        self._costo_total: float = 0.0
        self.validar()

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion_horas(self) -> float:
        return self._duracion_horas

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    def validar(self) -> None:
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.nombre}' ({self._servicio.id}) no está disponible."
            )

    def confirmar(self) -> None:
        """Confirma la reserva, calcula su costo y bloquea el servicio."""
        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva {self.id} en estado '{self._estado}'."
            )
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.nombre}' ya fue ocupado por otra reserva."
            )

        try:
            # Uso de método sobrecargado según tipo de dato de duración
            duracion_arg = (
                int(self._duracion_horas)
                if self._duracion_horas.is_integer()
                else self._duracion_horas
            )
            self._costo_total = self._servicio.calcular_costo_final(
                duracion_arg, impuesto=self._impuesto, descuento=self._descuento
            )
        except ErrorSistemaFJ as exc:
            raise ReservaInvalidaError(
                f"Error financiero al confirmar reserva {self.id}."
            ) from exc

        self._servicio.disponible = False
        self._estado = "CONFIRMADA"

    def cancelar(self) -> None:
        """Cancela la reserva y libera el servicio si estaba bloqueado."""
        if self._estado in ("CANCELADA", "COMPLETADA"):
            raise OperacionNoPermitidaError(
                f"No es posible cancelar la reserva {self.id} porque ya está '{self._estado}'."
            )
        if self._estado == "CONFIRMADA":
            self._servicio.disponible = True
        self._estado = "CANCELADA"

    def procesar_finalizacion(self) -> None:
        """Marca una reserva confirmada como completada y libera el recurso."""
        if self._estado != "CONFIRMADA":
            raise OperacionNoPermitidaError(
                f"Solo se pueden finalizar reservas CONFIRMADAS (estado actual: '{self._estado}')."
            )
        self._servicio.disponible = True
        self._estado = "COMPLETADA"

    def obtener_resumen(self) -> str:
        return (
            f"Reserva [{self.id}] | Estado: {self.estado} | "
            f"Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre} | "
            f"Duración: {self.duracion_horas}h | Total: ${self.costo_total:,.2f}"
        )


# ==============================================================================
# 7. CONTROLADOR CENTRAL DEL SISTEMA (GESTIÓN EN MEMORIA SIN BD)
# ==============================================================================


class SistemaGestionSoftwareFJ:
    """Orquesta clientes, servicios y reservas en memoria con manejo resiliente de errores."""

    def __init__(self, archivo_log: str = "software_fj_eventos.log"):
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        self._logger = GestorLogs(archivo_log)

    def registrar_cliente(
        self, cliente_id: str, documento: str, nombre: str, correo: str, telefono: str
    ) -> Optional[Cliente]:
        """Registra un cliente utilizando bloque try / except / else."""
        try:
            if any(c.id == cliente_id or c.documento == documento for c in self._clientes):
                raise OperacionNoPermitidaError(
                    f"Ya existe un cliente registrado con ID '{cliente_id}' o documento '{documento}'."
                )
            nuevo_cliente = Cliente(cliente_id, documento, nombre, correo, telefono)
        except ErrorSistemaFJ as err:
            self._logger.registrar_error("Clientes", err, f"Intento registro ID={cliente_id}")
            print(f"  [X] Error al registrar cliente: {err}")
            return None
        else:
            self._clientes.append(nuevo_cliente)
            self._logger.registrar_evento(
                "INFO", "Clientes", f"Registrado: {nuevo_cliente.obtener_resumen()}"
            )
            print(f"  [OK] {nuevo_cliente.obtener_resumen()}")
            return nuevo_cliente

    def registrar_servicio(self, servicio_builder, *args, **kwargs) -> Optional[Servicio]:
        """Crea y registra un servicio especializado manejando errores de instanciación."""
        try:
            servicio: Servicio = servicio_builder(*args, **kwargs)
            if any(s.id == servicio.id for s in self._servicios):
                raise OperacionNoPermitidaError(
                    f"El ID de servicio '{servicio.id}' ya se encuentra registrado."
                )
        except ErrorSistemaFJ as err:
            self._logger.registrar_error("Servicios", err, f"Clase={servicio_builder.__name__}")
            print(f"  [X] Error al crear servicio: {err}")
            return None
        except Exception as err_inesperado:
            error_encadenado = DatoInvalidoError(
                "Error inesperado en los parámetros del servicio."
            )
            error_encadenado.__cause__ = err_inesperado
            self._logger.registrar_error("Servicios", error_encadenado)
            print(f"  [X] Error crítico controlado: {error_encadenado}")
            return None
        else:
            self._servicios.append(servicio)
            self._logger.registrar_evento(
                "INFO", "Servicios", f"Creado: {servicio.obtener_resumen()}"
            )
            print(f"  [OK] {servicio.obtener_resumen()}")
            return servicio

    def crear_y_confirmar_reserva(
        self,
        reserva_id: str,
        cliente_id: str,
        servicio_id: str,
        duracion_horas: float,
        impuesto: float = 0.19,
        descuento: float = 0.0,
    ) -> Optional[Reserva]:
        """Crea y confirma una reserva usando try / except / finally y encadenamiento."""
        reserva_creada: Optional[Reserva] = None
        exito = False
        try:
            cliente = self._buscar_cliente(cliente_id)
            servicio = self._buscar_servicio(servicio_id)

            try:
                reserva = Reserva(
                    reserva_id, cliente, servicio, duracion_horas, impuesto, descuento
                )
                reserva.confirmar()
            except ErrorSistemaFJ as err_dominio:
                raise ReservaInvalidaError(
                    f"Fallo al procesar la reserva '{reserva_id}'."
                ) from err_dominio

            self._reservas.append(reserva)
            reserva_creada = reserva
            exito = True
            self._logger.registrar_evento(
                "INFO", "Reservas", f"Confirmada: {reserva.obtener_resumen()}"
            )
            print(f"  [OK] {reserva.obtener_resumen()}")
            return reserva_creada

        except ErrorSistemaFJ as err:
            self._logger.registrar_error(
                "Reservas",
                err,
                f"Reserva={reserva_id}, Cliente={cliente_id}, Servicio={servicio_id}",
            )
            print(f"  [X] Reserva rechazada: {err}")
            if err.__cause__:
                print(f"      └─ Motivo técnico: {err.__cause__}")
            return None
        finally:
            estado_auditoria = "EXITOSA" if exito else "FALLIDA"
            self._logger.registrar_evento(
                "AUDIT",
                "Reservas",
                f"Cierre de transacción reserva '{reserva_id}' -> {estado_auditoria}",
            )

    def cancelar_reserva(self, reserva_id: str) -> None:
        try:
            reserva = self._buscar_reserva(reserva_id)
            reserva.cancelar()
        except ErrorSistemaFJ as err:
            self._logger.registrar_error("Reservas", err, f"Cancelación ID={reserva_id}")
            print(f"  [X] Error al cancelar reserva: {err}")
        else:
            self._logger.registrar_evento(
                "INFO", "Reservas", f"Reserva '{reserva_id}' cancelada correctamente."
            )
            print(f"  [OK] Reserva '{reserva_id}' cancelada y servicio liberado.")

    def completar_reserva(self, reserva_id: str) -> None:
        try:
            reserva = self._buscar_reserva(reserva_id)
            reserva.procesar_finalizacion()
        except ErrorSistemaFJ as err:
            self._logger.registrar_error("Reservas", err, f"Finalización ID={reserva_id}")
            print(f"  [X] Error al finalizar reserva: {err}")
        else:
            self._logger.registrar_evento(
                "INFO", "Reservas", f"Reserva '{reserva_id}' finalizada exitosamente."
            )
            print(f"  [OK] Reserva '{reserva_id}' marcada como COMPLETADA.")

    def _buscar_cliente(self, cliente_id: str) -> Cliente:
        for cliente in self._clientes:
            if cliente.id == cliente_id:
                return cliente
        raise ParametroFaltanteError(f"No existe ningún cliente con ID '{cliente_id}'.")

    def _buscar_servicio(self, servicio_id: str) -> Servicio:
        for servicio in self._servicios:
            if servicio.id == servicio_id:
                return servicio
        raise ParametroFaltanteError(f"No existe ningún servicio con ID '{servicio_id}'.")

    def _buscar_reserva(self, reserva_id: str) -> Reserva:
        for reserva in self._reservas:
            if reserva.id == reserva_id:
                return reserva
        raise ParametroFaltanteError(f"No existe ninguna reserva con ID '{reserva_id}'.")

    def generar_reporte_consola(self) -> None:
        print("\n" + "=" * 80)
        print("RESUMEN FINAL DEL ESTADO DEL SISTEMA (MEMORIA)")
        print("=" * 80)
        print(f"Total Clientes registrados : {len(self._clientes)}")
        print(f"Total Servicios activos    : {len(self._servicios)}")
        print(f"Total Reservas procesadas  : {len(self._reservas)}")
        print("-" * 80)
        for r in self._reservas:
            print(f"  • {r.obtener_resumen()}")
        print("=" * 80)


# ==============================================================================
# 8. SIMULACIÓN DE OPERACIONES (12 ESCENARIOS VALIDOS E INVÁLIDOS)
# ==============================================================================


def ejecutar_simulacion() -> None:
    archivo_logs = "software_fj_eventos.log"
    sistema = SistemaGestionSoftwareFJ(archivo_log=archivo_logs)

    print("\n>>> INICIANDO SIMULACIÓN DE OPERACIONES EN SOFTWARE FJ <<<\n")

    # OPERACIÓN 1: Registro válido de cliente 1
    print("Operación 1: Registrar cliente corporativo válido (CLI-01)")
    sistema.registrar_cliente(
        "CLI-01", "1088294510", "Laura Gómez", "laura.gomez@techcorp.co", "+573001234567"
    )

    # OPERACIÓN 2: Registro válido de cliente 2
    print("\nOperación 2: Registrar cliente válido (CLI-02)")
    sistema.registrar_cliente(
        "CLI-02", "900451223", "Carlos Mendoza", "cmendoza@innovasoft.com", "3159876543"
    )

    # OPERACIÓN 3: Registro inválido de cliente (correo mal formado y nombre con números)
    print("\nOperación 3: Intentar registrar cliente con datos inválidos (CLI-03)")
    sistema.registrar_cliente(
        "CLI-03", "10223344", "Pedro123", "correo_sin_arroba.com", "3001112233"
    )

    # OPERACIÓN 4: Registro inválido de cliente duplicado
    print("\nOperación 4: Intentar registrar cliente con documento duplicado (CLI-04)")
    sistema.registrar_cliente(
        "CLI-04", "1088294510", "Laura Duplicada", "otra@empresa.com", "3005556677"
    )

    # OPERACIÓN 5: Creación válida de Sala de Juntas
    print("\nOperación 5: Crear servicio válido -> ReservaSala (SRV-SALA-01)")
    sistema.registrar_servicio(
        ReservaSala, "SRV-SALA-01", "Sala Ejecutiva Orion", 45.0, 12, True
    )

    # OPERACIÓN 6: Creación válida de Alquiler de Equipo
    print("\nOperación 6: Crear servicio válido -> AlquilerEquipo (SRV-EQ-01)")
    sistema.registrar_servicio(
        AlquilerEquipo,
        "SRV-EQ-01",
        "Workstation Dell Precision",
        18.0,
        "Portátil Alto Rendimiento",
        "SN-DELL-9981",
        100.0,
    )

    # OPERACIÓN 7: Creación válida de Asesoría Especializada
    print("\nOperación 7: Crear servicio válido -> AsesoriaEspecializada (SRV-ASE-01)")
    sistema.registrar_servicio(
        AsesoriaEspecializada,
        "SRV-ASE-01",
        "Auditoría Ciberseguridad Perimetral",
        80.0,
        "Seguridad de Redes",
        "ARQUITECTO",
    )

    # OPERACIÓN 8: Creación inválida de servicio (tarifa negativa / parámetros inválidos)
    print("\nOperación 8: Intentar crear servicio con tarifa negativa (SRV-ERR-01)")
    sistema.registrar_servicio(
        ReservaSala, "SRV-ERR-01", "Sala Defectuosa", -25.0, 10, False
    )

    # OPERACIÓN 9: Creación inválida de servicio especializado (nivel de consultor inexistente)
    print("\nOperación 9: Intentar crear asesoría con nivel inválido (SRV-ERR-02)")
    sistema.registrar_servicio(
        AsesoriaEspecializada,
        "SRV-ERR-02",
        "Consultoría Cloud",
        60.0,
        "AWS",
        "GURU_SUPREMO",
    )

    # OPERACIÓN 10: Reserva exitosa de Sala (4 horas con 10% de descuento)
    print("\nOperación 10: Procesar reserva exitosa de Sala (RES-001)")
    sistema.crear_y_confirmar_reserva(
        "RES-001", "CLI-01", "SRV-SALA-01", duracion_horas=4, descuento=0.10
    )

    # OPERACIÓN 11: Intento fallido de reserva sobre un servicio ya ocupado
    print("\nOperación 11: Intentar reservar la misma sala ya ocupada (RES-002)")
    sistema.crear_y_confirmar_reserva(
        "RES-002", "CLI-02", "SRV-SALA-01", duracion_horas=2
    )

    # OPERACIÓN 12: Reserva exitosa de Asesoría, cálculo inconsistente, cancelación y doble cancelación
    print("\nOperación 12: Reserva de Asesoría, fallo por descuento inválido y gestión de estados")
    # 12a. Falla por descuento > 100% (CalculoInconsistenteError encadenado a ReservaInvalidaError)
    sistema.crear_y_confirmar_reserva(
        "RES-003", "CLI-02", "SRV-ASE-01", duracion_horas=3, descuento=1.5
    )
    # 12b. Reserva válida de Asesoría
    sistema.crear_y_confirmar_reserva(
        "RES-004", "CLI-02", "SRV-ASE-01", duracion_horas=3, descuento=0.05
    )
    # 12c. Cancelación válida y posterior intento inválido de volver a cancelar
    sistema.cancelar_reserva("RES-004")
    sistema.cancelar_reserva("RES-004")

    # Demostración adicional directa de sobrecarga con diccionario en servicio de equipo
    print("\nDemostración extra de método sobrecargado (cálculo con diccionario):")
    equipo = sistema._buscar_servicio("SRV-EQ-01")
    costo_paquete = equipo.calcular_costo_final(
        {"duracion": 10, "impuesto": 0.19, "descuento": 0.15, "recargo_fijo": 20.0}
    )
    print(f"  [OK] Cálculo sobrecargado (dict) para 10h de {equipo.nombre}: ${costo_paquete:,.2f}")

    # Reporte final en memoria
    sistema.generar_reporte_consola()
    print(f"\nTodos los eventos y errores fueron registrados en: '{archivo_logs}'")


if __name__ == "__main__":
    ejecutar_simulacion()