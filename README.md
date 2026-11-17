# Sistema Integral de Gestión - Software FJ

Aplicación orientada a objetos desarrollada en Python (sin motores de bases de datos) para administrar clientes, servicios especializados y reservas de **Software FJ**, garantizando continuidad operativa mediante manejo avanzado de excepciones y auditoría en archivos de logs.

## Arquitectura y Características

* **Abstracción y Herencia:**
  * `EntidadSistema`: Clase abstracta base con atributos comunes e interfaz de validación y resumen.
  * `Servicio`: Clase abstracta derivada de la cual heredan `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada`.
* **Encapsulación:** La clase `Cliente` protege sus datos personales mediante atributos privados y propiedades con validaciones estrictas.
* **Polimorfismo y Sobrecarga:**
  * Sobrescritura de métodos (`validar_parametros`, `describir_servicio`, `calcular_costo_base`) en cada especialización.
  * Sobrecarga mediante `@singledispatchmethod` en `calcular_costo_final` para soportar duración en enteros (`int`), decimales (`float`) o paquetes (`dict`).
* **Resiliencia y Logs:** Jerarquía de excepciones propias (`ErrorSistemaFJ`), bloques `try/except`, `try/except/else`, `try/except/finally`, encadenamiento de excepciones (`raise ... from ...`) y registro persistente en `software_fj_eventos.log`.

## Requisitos y Ejecución

* **Requisitos:** Python 3.10 o superior (únicamente biblioteca estándar).

```bash
python sistema_software_fj.py
```