"""
Configuración centralizada del sistema LPM Pizzas.
Todos los valores que antes estaban hardcodeados en main.py, store.py y printer.py
ahora se administran desde este único archivo.
"""
import os

# === Ruta base del proyecto ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === Configuración del Negocio ===
BASE_PAY_CADETE = 10000
PRODUCT_CATEGORIES = ["Pizza", "Papas", "Empanadas"]
DELIVERY_TYPES = ["Envío", "Take Away"]
PAYMENT_METHODS = ["Efectivo", "Online"]

# === Configuración de Base de Datos ===
DATABASE_FILE = os.path.join(BASE_DIR, "pizzeria.db")

# === Configuración de Impresión ===
# 'POS80' -> Envía directo a la impresora térmica (Usa esto en la PC final)
# 'PDF'   -> Abre la ventana de Windows para guardar como PDF (Para probar diseño)
# 'DEBUG' -> Solo muestra una vista previa en la consola negra
PRINTER_WIDTH = 48
PRINTER_OUTPUT_MODE = "PDF"
