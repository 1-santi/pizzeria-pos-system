"""Sistema de impresión y formateo de tickets ESC/POS."""
import os
import datetime
import platform
from collections import Counter

from config import PRINTER_WIDTH, PRINTER_OUTPUT_MODE, TICKETS_DIR

# Configuración importada
OUTPUT_MODE = PRINTER_OUTPUT_MODE
WIDTH = PRINTER_WIDTH

# Comandos ESC/POS genéricos
BIG_FONT_ON = "\x1b\x21\x30"   # Doble altura y ancho
BIG_FONT_OFF = "\x1b\x21\x00"  # Fuente normal
CUT_COMMAND = "\n\n\x1d\x56\x42\x00"  # Corte de guillotina


def center_text(text, width=WIDTH):
    return text.center(width)


def format_line(left, right, width=WIDTH):
    space = width - len(left) - len(right)
    return f"{left}{' ' * space}{right}" if space > 0 else f"{left} {right}"


def normalize_text(text):
    """Quita acentos y caracteres especiales para compatibilidad térmica."""
    import unicodedata
    if not text:
        return ""
    text = text.replace('¡', '').replace('¿', '').replace('ñ', 'n').replace('Ñ', 'N')
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def sanitize_filename(name):
    return "".join([c for c in name if c.isalpha() or c.isdigit() or c == ' ']).strip().replace(' ', '_')


def process_output(filename, text_content, raw_content):
    """Procesa la salida física o digital del ticket."""
    try:
        if OUTPUT_MODE == 'DEBUG':
            print(f"\n--- VISTA PREVIA: {filename} ---")
            preview = text_content.replace(BIG_FONT_ON, "[GRANDE]").replace(BIG_FONT_OFF, "[NORMAL]")
            print(preview)
            print("-" * 30)

        elif OUTPUT_MODE == 'PDF':
            clean_text = text_content.replace(BIG_FONT_ON, "").replace(BIG_FONT_OFF, "")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(clean_text)

            if platform.system() == "Windows":
                # Abre la ventana de impresión nativa de Windows
                cmd = f'powershell -Command "Get-Content -Path \'{filename}\' | Out-Printer"'
                os.system(cmd)
                print(f"Ventana de impresión abierta para: {filename}")

        elif OUTPUT_MODE == 'POS80':
            with open(filename, "w", encoding="utf-8") as f:
                f.write(raw_content)

            if platform.system() == "Windows":
                # Copia el archivo binario directamente al puerto de la ticketera
                cmd = f'copy /b "{filename}" "\\\\127.0.0.1\\POS80"'
                os.system(cmd)
                print(f"Enviado a impresora POS80: {filename}")

    except Exception as e:
        print(f"Error al procesar salida: {e}")


# Helpers de compatibilidad (soportan dict y dataclass)==============================

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
    zone_name = _get_attr(order_data, 'zone_name', '')

    lines.append(center_text("=== COMANDA COCINA ==="))

    # Zona al lado del número de pedido en fuente grande
    BIG_WIDTH = 24  # Ancho efectivo con fuente grande (la mitad del normal)
    if zone_name:
        header_text = f"#{order_id} | {zone_name.upper()}"
    else:
        header_text = f"PEDIDO #{order_id}"
    lines.append(f"{BIG_FONT_ON}{header_text.center(BIG_WIDTH)}{BIG_FONT_OFF}")

    lines.append("=" * WIDTH)

    lines.append(center_text(f"*** {delivery.upper()} ***"))
    lines.append("")

    item_tuples = _get_items(order_data)
    counts = Counter(item_tuples)

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
    filepath = os.path.join(TICKETS_DIR, filename)

    process_output(filepath, text_content, raw_content)
    return filepath


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
    zone_name = _get_attr(order_data, 'zone_name', '')

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
    if zone_name:
        lines.append(f"Zona: {zone_name}")

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
    filepath = os.path.join(TICKETS_DIR, filename)

    process_output(filepath, text_content, raw_content)
    return filepath


def print_menu_ticket(products):
    """Genera e imprime un ticket con el menú completo para referencia (machete)."""
    lines = []
    lines.append(center_text("=== MENU DE PRODUCTOS ==="))
    lines.append(center_text("LPM PIZZAS"))
    lines.append("=" * WIDTH)

    # Agrupar por categoría
    from collections import defaultdict
    categories = defaultdict(list)
    for item in products:
        categories[item.category].append(item)

    for category in sorted(categories.keys()):
        lines.append("")
        lines.append(center_text(f"*** {category.upper()} ***"))
        lines.append(f"{'ID':<4} {'Producto':<33} {'Precio'}")
        lines.append("-" * WIDTH)
        for p in categories[category]:
            display_id = str(p.id) if p.id is not None else ""
            price_str = f"${p.price}"
            # Truncar nombre a 33 caracteres para que entre alineado
            name_display = p.name[:33]
            space = WIDTH - len(f"{display_id:<4}") - len(name_display) - len(price_str)
            if space > 0:
                line = f"{display_id:<4}{name_display}{' ' * space}{price_str}"
            else:
                line = f"{display_id:<4}{name_display} {price_str}"
            lines.append(line)
        lines.append("-" * WIDTH)

    lines.append("")
    lines.append("=" * WIDTH)
    lines.append(center_text("FIN DEL MENU"))

    text_content = normalize_text("\n".join(lines))
    raw_content = text_content + CUT_COMMAND

    filename = "menu_productos_machete.txt"
    filepath = os.path.join(TICKETS_DIR, filename)

    process_output(filepath, text_content, raw_content)
    return filepath
