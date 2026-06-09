# REQUISITOS PARA INSTALACIÓN (OTRA PC)

Para que el sistema **LPM PIZZAS** funcione correctamente en otra computadora, asegúrate de cumplir con lo siguiente:

### 1. Sistema Operativo
*   **Windows 10 o 11**

### 2. Python (Lenguaje de Programación)
*   **Versión**: Python 3.7 o superior instalado.
*   **Instalación**: Al instalar Python, asegúrate de marcar la casilla **"Add Python to PATH"**.

### 3. Configuración de Impresora (Crítico)
*   **Impresora Térmica (80mm)**: Debe estar instalada en Windows.
*   **Compartir Impresora**: 
    1. Ve a "Propiedades de la impresora" -> Pestaña **"Compartir"**.
    2. Activa "Compartir esta impresora" y ponle el nombre exacto: **POS80**.
*   **Método de Impresión**: El sistema usa impresión en modo RAW (`copy /b`). Esto garantiza que el texto ocupe todo el ancho, las letras de la comanda salgan grandes y la guillotina corte el papel automáticamente.

### 4. Nuevas Funcionalidades Incluidas
*   **Sistema de Cadetes**: Liquidación diaria automática ($10.000 + envíos).
*   **Control de Pagos**: Registro de Efectivo vs Online (para ARCA).
*   **Historial Interactivo**: Búsqueda por cliente/cadete y reimpresión de tickets.
*   **Exportación**: Generación de archivos Excel (CSV) compatibles con Windows.

---

# CÓMO EJECUTAR EL SISTEMA

1.  Copia la carpeta a la nueva PC.
2.  Abre la carpeta `pizza_system`.
3.  Cambia `OUTPUT_MODE = 'PDF'` a `'POS80'` en el archivo `printer.py` para imprimir real.
4.  Haz doble clic en `run_pizzeria.bat`.

---
*Si el texto sale con márgenes o chico, verifica que la impresora esté compartida correctamente como **POS80**.*
