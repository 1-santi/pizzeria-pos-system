"""Configuración centralizada del sistema LPM Pizzas."""
import os
import sys

# Ruta base del proyecto (soporta ejecutable compilado y script normal)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuración del Negocio
BASE_PAY_CADETE = 10000
PRODUCT_CATEGORIES = ["Pizza", "Papas", "Empanadas"]
DELIVERY_TYPES = ["Envío", "Take Away"]
PAYMENT_METHODS = ["Efectivo", "Online"]

# Base de Datos (data/pizzeria.db)
DATABASE_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_FILE = os.path.join(DATABASE_DIR, "pizzeria.db")

# Carpeta de tickets y comandas (tickets/)
TICKETS_DIR = os.path.join(BASE_DIR, "tickets")
os.makedirs(TICKETS_DIR, exist_ok=True)

# Configuración de Impresión (modos: 'POS80', 'PDF', 'DEBUG')
PRINTER_WIDTH = 48
PRINTER_OUTPUT_MODE = "POS80"
