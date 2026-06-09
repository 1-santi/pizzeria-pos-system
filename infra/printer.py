"""
Sistema de impresión - Formateo y envío de tickets.

IMPORTANTE: Toda la lógica de comandos ESC/POS, tamaños de fuente,
normalización de texto y corte de guillotina se preserva EXACTAMENTE
como en la versión original. Solo se externalizó la configuración
a config.py y se adaptó para aceptar objetos Order (dataclass).

Configuración de salida (desde config.py):
  'POS80' -> Envía directo a la impresora térmica (Usa esto en la PC final)
  'PDF'   -> Abre la ventana de Windows para guardar como PDF (Para probar diseño)
  'DEBUG' -> Solo muestra una vista previa en la consola negra
"""
import os
import datetime
import platform
from collections import Counter

from config import PRINTER_WIDTH, PRINTER_OUTPUT_MODE

# =================================================================
# CONFIGURACION (importada desde config.py)
# =================================================================
OUTPUT_MODE = PRINTER_OUTPUT_MODE
WIDTH = PRINTER_WIDTH

# =================================================================
# Comandos ESC/POS (Solo funcionan en modo 'POS80')
# NO MODIFICAR estos valores - son los comandos exactos que la
# impresora térmica necesita para funcionar correctamente.
# =================================================================
BIG_FONT_ON = "\x1b\x21\x30"   # Doble altura y ancho
BIG_FONT_OFF = "\x1b\x21\x00"  # Fuente normal
CUT_COMMAND = "\n\n\x1d\x56\x42\x00"  # Corte automático por guillotina


def center_text(text, width=WIDTH):
    return text.center(width)


def format_line(left, right, width=WIDTH):
    space = width - len(left) - len(right)
    return f"{left}{' ' * space}{right}" if space > 0 else f"{left} {right}"


def normalize_text(text):
    """Remueve acentos y caracteres especiales para impresoras térmicas.
    Convierte ñ/Ñ a n/N y elimina ¡¿ para evitar caracteres rotos
    en codepages de impresoras genéricas."""
    import unicodedata
    if not text:
        return ""
    text = text.replace('¡', '').replace('¿', '').replace('ñ', 'n').replace('Ñ', 'N')
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def sanitize_filename(name):
    return "".join([c for c in name if c.isalpha() or c.isdigit() or c == ' ']).strip().replace(' ', '_')


def process_output(filename, text_content, raw_content):
    """Maneja la salida según el modo seleccionado."""
    try:
        if OUTPUT_MODE == 'DEBUG':
            print(f"\n--- VISTA PREVIA: {filename} ---")
            # En consola mostramos marcas para lo que sería grande
            preview = text_content.replace(BIG_FONT_ON, "[GRANDE]").replace(BIG_FONT_OFF, "[NORMAL]")
            print(preview)
            print("-" * 30)

        elif OUTPUT_MODE == 'PDF':
            # Escribimos un archivo limpio sin códigos raros para que el PDF no falle
            clean_text = text_content.replace(BIG_FONT_ON, "").replace(BIG_FONT_OFF, "")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(clean_text)

            if platform.system() == "Windows":
                # Este comando abre la ventana de 'Guardar como PDF' de Windows
                cmd = f'powershell -Command "Get-Content -Path \'{filename}\' | Out-Printer"'
                os.system(cmd)
                print(f"Ventana de impresión abierta para: {filename}")

        elif OUTPUT_MODE == 'POS80':
            # Modo Real: Escribimos todo incluyendo comandos de corte y tamaño
            with open(filename, "w", encoding="utf-8") as f:
                f.write(raw_content)

            if platform.system() == "Windows":
                cmd = f'copy /b "{filename}" "\\\\127.0.0.1\\POS80"'
                os.system(cmd)
                print(f"Enviado a impresora POS80: {filename}")

    except Exception as e:
        print(f"Error al procesar salida: {e}")


# =================================================================
# Helpers para acceder a datos del pedido (soporta dict y dataclass)
# =================================================================

def _get_attr(order_data, attr, default=""):
    """Accede a un atributo del pedido, sea dict u objeto."""
    if isinstance(order_data, dict):
        return order_data.get(attr, default)
    return getattr(order_data, attr, default)


def _get_items(order_data):
    """Obtiene los ítems del pedido como lista de tuplas (name, price)."""
    if isinstance(order_data, dict):
        items = order_data.get('items', [])
    else:
        items = getattr(order_data, 'items', [])

    result = []
    for item in items:
        if isinstance(item, dict):
            result.append((item['name'], item['price']))
        else:
            result.append((item.name, item.price))
    return result


# =================================================================
# GENERACIÓN DE TICKETS
# La lógica de formateo, tamaños de fuente y comandos ESC/POS
# se mantiene EXACTAMENTE como en la versión original.
# =================================================================

def print_kitchen_order(order_data):
    """Genera la comanda de cocina con texto GRANDE para los productos."""
    lines = []
    order_id = _get_attr(order_data, 'id')
    delivery = _get_attr(order_data, 'delivery_type', 'N/A')
    customer = _get_attr(order_data, 'customer')
    obs = _get_attr(order_data, 'observation', '')

    lines.append(center_text("=== COMANDA COCINA ==="))
    lines.append(center_text(f"PEDIDO #{order_id}"))
    lines.append("=" * WIDTH)

    lines.append(center_text(f"*** {delivery.upper()} ***"))
    lines.append("")

    item_tuples = _get_items(order_data)
    counts = Counter(item_tuples)

    BIG_WIDTH = 24  # Ancho efectivo con fuente grande (la mitad del normal)

    for (name, price), qty in counts.items():
        name_display = name.upper()
        item_text = f"{qty} x {name_display}"
        lines.append("")
        # Agregamos los códigos de tamaño
        lines.append(f"{BIG_FONT_ON}{item_text.center(BIG_WIDTH)}{BIG_FONT_OFF}")

    lines.append("")

    if obs:
        lines.append("")
        lines.append("*" * WIDTH)
        lines.append(center_text("!!! OBSERVACION !!!"))
        lines.append(f"{BIG_FONT_ON}{obs.upper().center(BIG_WIDTH)}{BIG_FONT_OFF}")
        lines.append("*" * WIDTH)

    lines.append("")
    lines.append("=" * WIDTH)

    text_content = normalize_text("\n".join(lines))
    raw_content = text_content + CUT_COMMAND

    safe_name = sanitize_filename(customer)
    filename = f"comanda_{order_id}_{safe_name}.txt"

    process_output(filename, text_content, raw_content)
    return filename


def print_control_ticket(order_data):
    """Genera el ticket de control para el cliente con detalle completo."""
    lines = []
    order_id = _get_attr(order_data, 'id')
    customer = _get_attr(order_data, 'customer')
    phone = _get_attr(order_data, 'phone', '')
    address = _get_attr(order_data, 'address', '')
    delivery = _get_attr(order_data, 'delivery_type', 'N/A')
    cadete = _get_attr(order_data, 'cadete', '')
    payment_method = _get_attr(order_data, 'payment_method', 'Efectivo')
    obs = _get_attr(order_data, 'observation', '')
    delivery_fee = _get_attr(order_data, 'delivery_fee', 0)
    total = _get_attr(order_data, 'total', 0)

    lines.append(center_text("LPM PIZZAS"))
    lines.append(center_text("M.David 4304"))
    lines.append("-" * WIDTH)

    dt = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    lines.append(f"Fecha: {dt}")
    lines.append(f"Orden #: {order_id}")
    lines.append(f"Cliente: {customer}")
    if phone:
        lines.append(f"Tel: {phone}")
    if address:
        lines.append(f"Dir: {address}")

    if cadete:
        lines.append(f"Tipo: {delivery} ({cadete})")
    else:
        lines.append(f"Tipo: {delivery}")

    lines.append(f"Pago: {payment_method}")
    lines.append("-" * WIDTH)

    lines.append(f"{'Cant':<4} {'Producto':<28} {'Unit':<7} {'Total'}")
    lines.append("-" * WIDTH)

    item_tuples = _get_items(order_data)
    counts = Counter(item_tuples)

    for (name, price), qty in counts.items():
        name_display = name[:28]
        subtotal = price * qty
        line = f"{qty:<4} {name_display:<28} ${price:<6} ${subtotal}"
        lines.append(line)

    lines.append("-" * WIDTH)

    if obs:
        lines.append(f"Obs: {obs}")
        lines.append("-" * WIDTH)

    if delivery_fee > 0:
        subtotal_items = total - delivery_fee
        lines.append(format_line("SUBTOTAL:", f"${subtotal_items}"))
        lines.append(format_line("ENVIO:", f"${delivery_fee}"))
        lines.append("-" * WIDTH)

    lines.append(format_line("TOTAL:", f"${total}"))
    lines.append("-" * WIDTH)
    lines.append("")
    lines.append(center_text("¡GRACIAS POR SU COMPRA!"))

    text_content = normalize_text("\n".join(lines))
    raw_content = text_content + CUT_COMMAND

    safe_name = sanitize_filename(customer)
    filename = f"ticket_{order_id}_{safe_name}.txt"

    process_output(filename, text_content, raw_content)
    return filename
