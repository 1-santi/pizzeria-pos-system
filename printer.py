import os
import datetime
import platform

# =================================================================
# CONFIGURACION DE SALIDA
# 'POS80' -> Envía directo a la impresora térmica (Usa esto en la PC final)
# 'PDF'   -> Abre la ventana de Windows para guardar como PDF (Para probar diseño)
# 'DEBUG' -> Solo muestra una vista previa en la consola negra
# =================================================================
OUTPUT_MODE = 'PDF' 

WIDTH = 48

# Comandos ESC/POS (Solo funcionan en modo 'POS80')
BIG_FONT_ON = "\x1b\x21\x30"  
BIG_FONT_OFF = "\x1b\x21\x00" 
CUT_COMMAND = "\n\n\x1d\x56\x42\x00"

def center_text(text, width=WIDTH):
    return text.center(width)

def format_line(left, right, width=WIDTH):
    space = width - len(left) - len(right)
    return f"{left}{' ' * space}{right}" if space > 0 else f"{left} {right}"

def normalize_text(text):
    import unicodedata
    if not text: return ""
    text = text.replace('¡', '').replace('¿', '').replace('ñ', 'n').replace('Ñ', 'N')
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def sanitize_filename(name):
    return "".join([c for c in name if c.isalpha() or c.isdigit() or c==' ']).strip().replace(' ', '_')

def process_output(filename, text_content, raw_content):
    """Maneja la salida según el modo seleccionado"""
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

def print_kitchen_order(order_data):
    lines = []
    lines.append(center_text("=== COMANDA COCINA ==="))
    lines.append(center_text(f"PEDIDO #{order_data['id']}"))
    lines.append("=" * WIDTH)
    
    delivery = order_data.get('delivery_type', 'N/A')
    lines.append(center_text(f"*** {delivery.upper()} ***"))
    lines.append("")
    
    from collections import Counter
    item_tuples = [(i['name'], i['price']) for i in order_data['items']]
    counts = Counter(item_tuples)
    
    BIG_WIDTH = 24 
    
    for (name, price), qty in counts.items():
        name_display = name.upper()
        item_text = f"{qty} x {name_display}"
        lines.append("")
        # Agregamos los códigos de tamaño
        lines.append(f"{BIG_FONT_ON}{item_text.center(BIG_WIDTH)}{BIG_FONT_OFF}")
        
    lines.append("")
    
    obs = order_data.get('observation', "")
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
    
    safe_name = sanitize_filename(order_data['customer'])
    filename = f"comanda_{order_data['id']}_{safe_name}.txt"
    
    process_output(filename, text_content, raw_content)
    return filename

def print_control_ticket(order_data):
    lines = []
    lines.append(center_text("LPM PIZZAS"))
    lines.append(center_text("M.David 4304"))
    lines.append("-" * WIDTH)
    
    dt = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    lines.append(f"Fecha: {dt}")
    lines.append(f"Orden #: {order_data['id']}")
    lines.append(f"Cliente: {order_data['customer']}")
    if order_data.get('phone'):
        lines.append(f"Tel: {order_data['phone']}")
    if order_data.get('address'):
        lines.append(f"Dir: {order_data['address']}")
    
    delivery = order_data.get('delivery_type', 'N/A')
    cadete = order_data.get('cadete', "")
    payment_method = order_data.get('payment_method', 'Efectivo')
    
    if cadete:
        lines.append(f"Tipo: {delivery} ({cadete})")
    else:
        lines.append(f"Tipo: {delivery}")
        
    lines.append(f"Pago: {payment_method}")
    lines.append("-" * WIDTH)
    
    lines.append(f"{'Cant':<4} {'Producto':<28} {'Unit':<7} {'Total'}") 
    lines.append("-" * WIDTH)
    
    from collections import Counter
    item_tuples = [(i['name'], i['price']) for i in order_data['items']]
    counts = Counter(item_tuples)
    
    for (name, price), qty in counts.items():
        name_display = name[:28]
        subtotal = price * qty
        line = f"{qty:<4} {name_display:<28} ${price:<6} ${subtotal}"
        lines.append(line)
        
    lines.append("-" * WIDTH)
    
    obs = order_data.get('observation', "")
    if obs:
        lines.append(f"Obs: {obs}")
        lines.append("-" * WIDTH)
        
    delivery_fee = order_data.get('delivery_fee', 0)
    if delivery_fee > 0:
        subtotal_items = order_data['total'] - delivery_fee
        lines.append(format_line("SUBTOTAL:", f"${subtotal_items}"))
        lines.append(format_line("ENVIO:", f"${delivery_fee}"))
        lines.append("-" * WIDTH)

    lines.append(format_line("TOTAL:", f"${order_data['total']}"))
    lines.append("-" * WIDTH)
    lines.append("")
    lines.append(center_text("¡GRACIAS POR SU COMPRA!"))
   
    text_content = normalize_text("\n".join(lines))
    raw_content = text_content + CUT_COMMAND
    
    safe_name = sanitize_filename(order_data['customer'])
    filename = f"ticket_{order_data['id']}_{safe_name}.txt"
    
    process_output(filename, text_content, raw_content)
    return filename
