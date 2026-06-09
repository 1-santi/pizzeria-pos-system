import os
import time
import re
import datetime
import csv
from store import Store
import printer

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def parse_quantity_query(query_input):
    """
    Parses a query string like '2xmuzza', '2 x 1', or 'muzza'.
    Returns (quantity, query_text).
    """
    query_input = query_input.strip()
    # Pattern: Digit(s) + optional spaces + 'x' + optional spaces + rest
    match = re.match(r'^(\d+)\s*[xX]\s*(.*)$', query_input)
    if match:
        quantity = int(match.group(1))
        # Ensure quantity is at least 1
        if quantity < 1: quantity = 1
        query = match.group(2).strip()
        return quantity, query
    return 1, query_input

def select_product_simple(display_menu, prompt):
    """Auxiliary for searching and selecting a product from menu"""
    query = input(prompt).strip()
    if not query: return None
    
    # Search logic
    matches = []
    if query.isdigit():
        idx = int(query) - 1
        if 0 <= idx < len(display_menu):
            matches = [display_menu[idx]]
    else:
        matches = [p for p in display_menu if query.lower() in p['name'].lower()]
        
    if not matches:
        print("No se encontró el producto.")
        return None
    if len(matches) == 1:
        return matches[0]
    
    print("\nSeleccione una opción:")
    for i, p in enumerate(matches):
        print(f"{i+1}. {p['name']} (${p['price']})")
    sel = input("Seleccione # (0 cancelar): ")
    if sel.isdigit():
        idx = int(sel) - 1
        if 0 <= idx < len(matches):
            return matches[idx]
    return None

def handle_half_and_half(display_menu):
    """Special flow for Half and Half pizzas"""
    print("\n--- SELECCION DE MITADES ---")
    print("Sabor 1:")
    sabor1 = select_product_simple(display_menu, "Buscar primer sabor: ")
    if not sabor1: return None
    print(f"Sabor 1: {sabor1['name']} (${sabor1['price']})")
    
    print("\nSabor 2:")
    sabor2 = select_product_simple(display_menu, "Buscar segundo sabor: ")
    if not sabor2: return None
    print(f"Sabor 2: {sabor2['name']} (${sabor2['price']})")
    
    # Price logic: the more expensive one
    final_price = max(sabor1['price'], sabor2['price'])
    final_name = f"1/2 {sabor1['name']} / 1/2 {sabor2['name']}"
    
    print("-" * 40)
    print(f"Resumen Mitad y Mitad:")
    print(f"Items: {final_name}")
    print(f"Precio (el más caro): ${final_price}")
    
    confirm = input("¿Confirmar esta mitad y mitad? ([s]/n): ").lower().strip()
    if confirm == 's' or confirm == '':
        return {"name": final_name, "price": final_price}
    return None

def print_header():
    print(r"""
    __                      ____  _                       
   / /   ____  ____ ___    / __ \(_)____________________
  / /   / __ \/ __ `__ \  / /_/ / /_  /_  / / __ `/ ___/
 / /___/ /_/ / / / / / / / ____/ / / /_/ /_/ /_/ (__  ) 
/_____/ .___/_/ /_/ /_/ /_/   /_/ /___/___/\__,_/____/  
     /_/                                                 
    """)
    print("--------------------------------------------------")
    print("         SISTEMA DE GESTION LPM PIZZAS            ")
    print("--------------------------------------------------")

def get_display_menu(store):
    menu = store.get_menu()
    from collections import defaultdict
    categories = defaultdict(list)
    for item in menu:
        cat = item.get('category', 'Pizza')
        categories[cat].append(item)
    
    display_ordered_menu = []
    for category in sorted(categories.keys()):
        for product in categories[category]:
            display_ordered_menu.append(product)
    return display_ordered_menu

def show_menu(store):
    print("\n--- MENU ---")
    display_menu = get_display_menu(store)
    if not display_menu:
        print("No hay productos en el sistema.")
        return

    # Group by category for display
    from collections import defaultdict
    categories = defaultdict(list)
    for item in display_menu:
        cat = item.get('category', 'Pizza')
        categories[cat].append(item)
    
    item_id = 1
    for category in sorted(categories.keys()):
        print(f"\n=== {category.upper()} ===")
        print(f"{'ID':<4} {'Nombre':<25} {'Precio':<10}")
        print("-" * 45)
        for product in categories[category]:
            print(f"{item_id:<4} {product['name']:<25} ${product['price']:<9}")
            item_id += 1
        print("-" * 45)

def take_order(store):
    print("\n--- TOMAR PEDIDO ---")
    display_menu = get_display_menu(store)
    if not display_menu:
        print("No hay productos para vender.")
        time.sleep(1)
        return

    while True:
        customer_name = input("Nombre del cliente (Obligatorio): ").strip()
        if customer_name:
            break
        print("El nombre es obligatorio.")
    
    phone = input("Teléfono (Opcional): ").strip()
    address = input("Dirección (Opcional): ").strip()
    
    # Delivery type
    print("\nTipo de entrega:")
    print("1. Envío")
    print("2. Take Away")
    delivery_choice = input("Seleccione (1/2) [1]: ").strip()
    delivery_type = "Envío" if (delivery_choice == "1" or delivery_choice == "") else "Take Away"
    
    delivery_fee = 0
    if delivery_type == "Envío":
        fee_input = input("Precio del envío [0]: ").strip()
        if fee_input:
            try:
                delivery_fee = int(fee_input)
            except ValueError:
                delivery_fee = 0

    order_items_objs = [] # Stores dicts {'name': ..., 'price': ...}
    total_items_price = 0

    while True:
        print(f"\nPedido de: {customer_name}")
        print(f"Items: {len(order_items_objs)} | Subtotal: ${total_items_price}")
        print("Opciones: 'menu', 'fin', o producto (ej: 'muzza', '2 x napo')")
        
        query_input = input("Producto: ").strip()
        
        if query_input.lower() == 'fin':
            break
        elif query_input.lower() == 'menu':
            show_menu(store)
            continue
        elif query_input.lower() in ['mitad', '1/2']:
            half_item = handle_half_and_half(display_menu)
            if half_item:
                order_items_objs.append(half_item)
                total_items_price += half_item['price']
                print("Mitad y mitad agregada con éxito.")
            continue
        elif not query_input:
            continue
            
        # Parse logic
        quantity, query = parse_quantity_query(query_input)
        
        # Search logic
        matches = []
        if query.isdigit():
            idx = int(query) - 1
            if 0 <= idx < len(display_menu):
                matches = [display_menu[idx]]
        else:
            matches = [p for p in display_menu if query.lower() in p['name'].lower()]
        
        selected_pizza = None
        
        if not matches:
            print("No se encontraron coincidencias.")
        elif len(matches) == 1:
            selected_pizza = matches[0]
            print(f"Agregar {quantity} x {selected_pizza['name']} (${selected_pizza['price']})?")
            # Default to 's' if Enter is pressed
            confirm = input("Confirmar ([s]/n): ").lower().strip()
            if confirm == 's' or confirm == '':
                pass # Confirmed
            else:
                selected_pizza = None
        else:
            print("\nCoincidencias encontradas:")
            for i, p in enumerate(matches):
                print(f"{i+1}. {p['name']} (${p['price']})")
            
            sel = input("Seleccione # (0 cancelar): ")
            if sel.isdigit():
                sel_idx = int(sel) - 1
                if 0 <= sel_idx < len(matches):
                    selected_pizza = matches[sel_idx]
        
        # Add to cart
        if selected_pizza:
            for _ in range(quantity):
                order_items_objs.append({"name": selected_pizza['name'], "price": selected_pizza['price']})
                total_items_price += selected_pizza['price']
            print(f"Agregado {quantity} items.")

    if order_items_objs:
        observation = input("\nObservaciones (Enter si no hay): ").strip()

        # store expects just names in list for historical reasons (unless we refactor store schema significantly)
        # But wait, store.py 'items' is just a list. We can store objects if we want, but old orders are strings.
        # To avoid breaking schema if mixed, let's keep storing strings in DB, but pass full objects to printer?
        # Ideally we store full objects, but let's stick to strings for DB to be safe with prev version, 
        # or maybe we can store dicts. JSON supports mixed types.
        # Let's store just names in DB to save space/compat, BUT we have a problem:
        # If price changes later, history is wrong.
        # Correct way: Store snapshot of item at moment of sale.
        # Let's migrate to storing [{"name": "X", "price": 100}] in "items".
        # Store.py add_order puts whatever we pass into "items".
        
        # Let's pass the list of dicts to store.
        order_items_names_only = [i['name'] for i in order_items_objs] # Fallback if we want simple
        # But requirements say we want detailed receipt.
        # Let's pass the full objects to store.
        
        # Refactor: I'll pass the list of dicts to add_order.
        # Note: printer expects list of dicts now.
        
        # Prepare order data for printer
        # Cadete selection
        cadete_name = ""
        if delivery_type == "Envío":
            cadetes = store.get_cadetes()
            if cadetes:
                while not cadete_name:
                    print("\nSeleccione Cadete (Obligatorio para envíos):")
                    for i, c in enumerate(cadetes, 1):
                        print(f"{i}. {c}")
                    c_choice = input("Seleccione #: ").strip()
                    if c_choice.isdigit() and 1 <= int(c_choice) <= len(cadetes):
                        cadete_name = cadetes[int(c_choice)-1]
                    else:
                        print("[!] Opción inválida. Por favor, elija un cadete de la lista.")
            else:
                print("\n[!] No hay cadetes registrados en el sistema.")
                input("Presione Enter para continuar sin asignar cadete...")

        # Payment Method selection
        print("\nMedio de Pago:")
        print("1. Efectivo (EF)")
        print("2. Online (ONL)")
        p_choice = input("Seleccione (1/2) [1]: ").strip()
        payment_method = "Online" if p_choice == "2" else "Efectivo"

        print("\nGenerando documentos...")
        
        # Final Total calculation
        final_total = total_items_price + delivery_fee
        
        order_id = store.add_order(customer_name, order_items_objs, final_total, phone, address, observation, delivery_type, delivery_fee, cadete_name, payment_method)
        print(f"\nPEDIDO #{order_id} CREADO CON EXITO!")
        print(f"Cliente: {customer_name}")
        if delivery_fee > 0:
            print(f"Subtotal: ${total_items_price}")
            print(f"Envío: ${delivery_fee}")
        if cadete_name:
            print(f"Cadete: {cadete_name}")
        print(f"Pago: {payment_method}")
        print(f"Total a cobrar: ${final_total}")
        
        # Prepare order data for printer
        order_data = {
            "id": order_id,
            "customer": customer_name,
            "phone": phone,
            "address": address,
            "observation": observation,
            "delivery_type": delivery_type,
            "delivery_fee": delivery_fee,
            "cadete": cadete_name,
            "payment_method": payment_method,
            "items": order_items_objs, # Passing dicts!
            "total": final_total
        }
        
        printer.print_kitchen_order(order_data)
        printer.print_control_ticket(order_data)
        
        input("Presione Enter para continuar...")
    else:
        print("Pedido cancelado.")
        time.sleep(1)

def products_menu(store):
    CATEGORIES = ["Pizza", "Papas", "Empanadas"]
    
    while True:
        clear_screen()
        print("\n--- GESTION DE PRODUCTOS ---")
        print("1. Agregar Producto")
        print("2. Editar Producto")
        print("3. Eliminar Producto")
        print("4. Volver")
        
        op = input("Seleccione opcion ([1]): ").strip()
        
        if op == '1' or op == '':
            name = input("Nombre: ").strip()
            if not name:
                print("El nombre no puede estar vacío.")
                time.sleep(1)
                continue
            
            # Limit name length for printer safety
            name = name[:30]
            
            try:
                price_input = input("Precio: ")
                price = int(price_input)
                if price <= 0:
                    print("El precio debe ser mayor a 0.")
                    time.sleep(1)
                    continue
            except ValueError:
                print("Precio inválido. Debe ser un número.")
                time.sleep(1)
                continue
            
            print("\nCategoría:")
            for i, cat in enumerate(CATEGORIES, 1):
                print(f"{i}. {cat}")
            cat_choice = input("Seleccione (1-3): ").strip()
            
            if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(CATEGORIES):
                category = CATEGORIES[int(cat_choice) - 1]
            else:
                category = "Pizza"  # Default
            
            store.add_product(name, price, category)
            print(f"Producto agregado en categoría {category}.")
            time.sleep(1)
            
        elif op == '2':
            show_menu(store)
            query = input("Nombre/ID a editar: ")
            menu = store.get_menu()
            target = None
            if query.isdigit():
                idx = int(query) - 1
                if 0 <= idx < len(menu):
                    target = menu[idx]
            else:
                 for p in menu:
                     if p['name'].lower() == query.lower():
                         target = p
                         break
            
            if target:
                current_cat = target.get('category', 'Pizza')
                print(f"Editando {target['name']} (${target['price']}) - {current_cat}")
                new_name = input(f"Nuevo nombre (enter mantener): ").strip()
                new_name = (new_name[:30]) if new_name else target['name']
                
                new_price_input = input(f"Nuevo precio (enter mantener): ")
                try:
                    if new_price_input:
                        new_price = int(new_price_input)
                        if new_price <= 0:
                            print("Precio debe ser > 0. Se mantiene anterior.")
                            new_price = target['price']
                    else:
                        new_price = target['price']
                except ValueError:
                    print("Valor inválido. Se mantiene anterior.")
                    new_price = target['price']
                
                print("\nNueva categoría:")
                for i, cat in enumerate(CATEGORIES, 1):
                    print(f"{i}. {cat}")
                print("Enter para mantener")
                cat_choice = input("Seleccione: ").strip()
                
                if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(CATEGORIES):
                    new_category = CATEGORIES[int(cat_choice) - 1]
                else:
                    new_category = None  # Keep current
                
                store.update_product(target['name'], new_name, new_price, new_category)
                print("Actualizado.")
            else:
                print("No encontrado.")
            time.sleep(1)

        elif op == '3':
            show_menu(store)
            name = input("Nombre exacto a eliminar: ")
            store.remove_product(name)
            print("Eliminado.")
            time.sleep(1)
        elif op == '4':
            break

def show_order_detail(store, order):
    while True:
        clear_screen()
        print("\n--- DETALLE DE PEDIDO #" + str(order['id']) + " ---")
        print(f"Fecha:     {order.get('date', 'N/A')}")
        print(f"Cliente:   {order['customer']}")
        if order.get('phone'): print(f"Telefono:  {order['phone']}")
        if order.get('address'): print(f"Direccion: {order['address']}")
        print(f"Entrega:   {order['delivery_type']}")
        if order.get('cadete'): print(f"Cadete:    {order['cadete']}")
        print(f"Pago:      {order.get('payment_method', 'Efectivo')}")
        print("-" * 40)
        print(f"{'Cant':<5} {'Producto':<25} {'Precio':<10}")
        
        from collections import Counter
        # The items can be names (old) or dicts (new)
        item_list = order['items']
        if item_list and isinstance(item_list[0], dict):
            item_tuples = [(i['name'], i['price']) for i in item_list]
        else:
            item_tuples = [(name, 0) for name in item_list]
            
        counts = Counter(item_tuples)
        for (name, price), qty in counts.items():
            print(f"{qty:<5} {name[:25]:<25} ${price*qty}")
            
        print("-" * 40)
        if order.get('delivery_fee', 0) > 0:
            subtotal = order['total'] - order['delivery_fee']
            print(f"Subtotal:  ${subtotal}")
            print(f"Envio:     ${order['delivery_fee']}")
        print(f"TOTAL:     ${order['total']}")
        if order.get('observation'):
            print(f"Obs:       {order['observation']}")
        print("-" * 40)
        
        print("\nOpciones:")
        print("1. Reimprimir Comanda (Cocina)")
        print("2. Reimprimir Ticket (Control)")
        print("3. Volver")
        
        op = input("Seleccione: ").strip()
        if op == '1':
            printer.print_kitchen_order(order)
            input("Reimpresión enviada. Enter para continuar...")
        elif op == '2':
            printer.print_control_ticket(order)
            input("Reimpresión enviada. Enter para continuar...")
        elif op == '3':
            break

def history_menu(store):
    while True:
        clear_screen()
        print("\n--- HISTORIAL DE PEDIDOS ---")
        orders = store.get_orders()
        
        if not orders:
            print("Sin pedidos.")
            input("\nPresione Enter para volver...")
            break
            
        print("1. Ver todos (últimos 10)")
        print("2. Buscar por nombre de cliente")
        print("3. Filtrar por cadete")
        print("4. Filtrar por medio de pago")
        print("5. Ver por ID de pedido")
        print("6. Volver")
        
        choice = input("\nSeleccione opcion: ").strip()
        
        filtered_orders = []
        if choice == '1':
            filtered_orders = orders[-10:]
        elif choice == '2':
            query = input("Nombre a buscar: ").lower()
            filtered_orders = [o for o in orders if query in o['customer'].lower()]
        elif choice == '3':
            cadetes = store.get_cadetes()
            if not cadetes:
                print("No hay cadetes registrados.")
                time.sleep(1)
                continue
            for i, c in enumerate(cadetes, 1):
                print(f"{i}. {c}")
            c_sel = input("Seleccione cadete #: ").strip()
            if c_sel.isdigit() and 1 <= int(c_sel) <= len(cadetes):
                c_name = cadetes[int(c_sel)-1]
                filtered_orders = [o for o in orders if o.get('cadete') == c_name]
        elif choice == '4':
            print("1. Efectivo")
            print("2. Online")
            p_sel = input("Seleccione pago (1/2): ").strip()
            p_method = "Online" if p_sel == "2" else "Efectivo"
            filtered_orders = [o for o in orders if o.get('payment_method', 'Efectivo') == p_method]
        elif choice == '5':
            oid = input("Ingrese ID del pedido: ").strip()
            if oid.isdigit():
                target = next((o for o in orders if o['id'] == int(oid)), None)
                if target:
                    show_order_detail(store, target)
                    continue
                else:
                    print("Pedido no encontrado.")
                    time.sleep(1)
            continue
        elif choice == '6':
            break
        else:
            continue

        if not filtered_orders:
            print("\nNo se encontraron pedidos.")
            input("Enter para continuar...")
            continue

        print(f"\n{'ID':<4} {'Fecha':<20} {'Cliente':<20} {'Total':<10}")
        print("-" * 60)
        for o in filtered_orders:
            date_str = o.get('date', 'N/A')
            print(f"{o['id']:<4} {date_str:<20} {o['customer']:<20} ${o['total']:<10}")
        
        sel = input("\nIngrese ID para ver detalle (Enter para volver): ").strip()
        if sel.isdigit():
            target = next((o for o in filtered_orders if o['id'] == int(sel)), None)
            if target:
                show_order_detail(store, target)

def cadetes_menu(store):
    while True:
        clear_screen()
        print("\n--- GESTION DE CADETES ---")
        cadetes = store.get_cadetes()
        if not cadetes:
            print("No hay cadetes registrados.")
        else:
            for i, c in enumerate(cadetes, 1):
                print(f"{i}. {c}")
        
        print("\n1. Agregar Cadete")
        print("2. Eliminar Cadete")
        print("3. Volver")
        
        op = input("Seleccione opcion: ").strip()
        if op == '1':
            name = input("Nombre del nuevo cadete: ").strip()
            if name:
                store.add_cadete(name)
                print("Cadete agregado.")
            time.sleep(1)
        elif op == '2':
            if not cadetes:
                print("Nada que eliminar.")
            else:
                sel = input("Seleccione # a eliminar: ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(cadetes):
                    name = cadetes[int(sel)-1]
                    store.remove_cadete(name)
                    print(f"Cadete {name} eliminado.")
            time.sleep(1)
        elif op == '3':
            break

def liquidation_menu(store):
    clear_screen()
    print("\n--- LIQUIDACION DE CADETES ---")
    print("Calculando para el día de hoy...")
    
    orders = store.get_orders()
    cadetes = store.get_cadetes()
    
    if not cadetes:
        print("No hay cadetes registrados.")
        input("\nPresione Enter para volver...")
        return

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    print(f"\nFecha: {today_str}")
    print(f"{'Cadete':<20} {'Envios':<8} {'Comision':<10} {'Base':<10} {'Total':<10}")
    print("-" * 65)
    
    BASE_PAY = 10000
    
    # Identify all unique cadetes who worked today, even if deleted from the fixed list
    cadetes_who_worked = set([o.get('cadete') for o in orders if o.get('date', '').startswith(today_str) and o.get('cadete')])
    
    # Combine with current fixed list to ensure everyone is covered
    all_to_report = sorted(list(cadetes_who_worked.union(set(cadetes))))
    
    for c_name in all_to_report:
        # Filter orders for today and this cadete
        c_orders = [o for o in orders if o.get('date', '').startswith(today_str) and o.get('cadete') == c_name]
        
        if not c_orders:
            continue # If no orders and not in record for today, skip
            
        status = ""
        if c_name not in cadetes:
            status = " (ELIMINADO)"
            
        envios_count = len(c_orders)
        comision_total = sum(o.get('delivery_fee', 0) for o in c_orders)
        final_total = BASE_PAY + comision_total
        
        name_display = (c_name + status)[:20]
        print(f"{name_display:<20} {envios_count:<8} ${comision_total:<9} ${BASE_PAY:<9} ${final_total:<9}")
    
    print("-" * 65)
    input("\nPresione Enter para volver...")

def sales_report_menu(store):
    while True:
        clear_screen()
        print("\n--- REPORTE FISCAL (VENTAS POR MEDIO DE PAGO) ---")
        print("1. Hoy")
        print("2. Día específico (AAAA-MM-DD)")
        print("3. Mes específico (AAAA-MM)")
        print("4. Todo el historial")
        print("5. Volver")
        
        op = input("\nSeleccione periodo: ").strip()
        if op == '5': break

        orders = store.get_orders()
        if not orders:
            print("No hay pedidos registrados.")
            input("Enter para volver...")
            break

        filtered = []
        period_label = ""

        if op == '1':
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            filtered = [o for o in orders if o.get('date', '').startswith(today_str)]
            period_label = f"HOY ({today_str})"
        elif op == '2':
            target = input("Ingrese fecha (EJ: 2026-01-20): ").strip()
            filtered = [o for o in orders if o.get('date', '').startswith(target)]
            period_label = f"DIA ({target})"
        elif op == '3':
            target = input("Ingrese mes (EJ: 2026-01): ").strip()
            filtered = [o for o in orders if o.get('date', '').startswith(target)]
            period_label = f"MES ({target})"
        elif op == '4':
            filtered = orders
            period_label = "TOTAL HISTORICO"
        else:
            continue

        if not filtered:
            print(f"\nNo se encontraron ventas para: {period_label}")
            input("Enter para continuar...")
            continue

        # Totals calculation
        total_ef = sum(o['total'] for o in filtered if o.get('payment_method', 'Efectivo') == 'Efectivo')
        total_onl = sum(o['total'] for o in filtered if o.get('payment_method') == 'Online')
        total_gen = total_ef + total_onl

        print(f"\n=== RESUMEN {period_label} ===")
        print("-" * 40)
        print(f"EFECTIVO (EF):    ${total_ef:>10}")
        print(f"ONLINE (ONL):      ${total_onl:>10}")
        print("-" * 40)
        print(f"TOTAL GENERAL:     ${total_gen:>10}")
        print("-" * 40)
        
        print("\n¿Desea ver el listado detallado?")
        print("1. Ver solo ventas ONLINE (para ARCA)")
        print("2. Ver todas las ventas del periodo")
        print("3. Exportar este resumen a PDF")
        print("4. No, volver")
        
        list_op = input("Seleccione: ").strip()
        
        if list_op == '3':
            # Preparamos un reporte formateado para la impresora/PDF
            report_lines = []
            report_lines.append(printer.center_text("REPORTE FISCAL DE VENTAS"))
            report_lines.append(printer.center_text(f"Periodo: {period_label}"))
            report_lines.append("-" * printer.WIDTH)
            report_lines.append(printer.format_line("EFECTIVO (EF):", f"${total_ef}"))
            report_lines.append(printer.format_line("ONLINE (ONL):", f"${total_onl}"))
            report_lines.append("-" * printer.WIDTH)
            report_lines.append(printer.format_line("TOTAL GENERAL:", f"${total_gen}"))
            report_lines.append("-" * printer.WIDTH)
            report_lines.append("\n" + printer.center_text("Listado de Ventas Online:"))
            
            online_list = [o for o in filtered if o.get('payment_method') == 'Online']
            if online_list:
                report_lines.append(f"{'ID':<5} {'Cliente':<25} {'Monto'}")
                for o in online_list:
                    report_lines.append(f"{o['id']:<5} {o['customer'][:25]:<25} ${o['total']}")
            else:
                report_lines.append("No hay ventas online.")
            
            report_text = "\n".join(report_lines)
            filename = f"reporte_fiscal_{period_label.replace(' ', '_').replace('(', '').replace(')', '')}.txt"
            
            # Usamos el sistema de printer para generar el PDF (usando el modo actual seleccionado)
            # Para asegurar que salga como PDF para el usuario, forzamos temporalmente el modo PDF si no está en POS80
            original_mode = printer.OUTPUT_MODE
            if printer.OUTPUT_MODE != 'POS80':
                printer.OUTPUT_MODE = 'PDF'
            
            printer.process_output(filename, report_text, report_text)
            printer.OUTPUT_MODE = original_mode
            input("\nProceso de exportación finalizado. Presione Enter para continuar...")
            continue

        detail_list = []
        if list_op == '1':
            detail_list = [o for o in filtered if o.get('payment_method') == 'Online']
            print("\n--- LISTADO ONLINE PARA FACTURAR ---")
        elif list_op == '2':
            detail_list = filtered
            print("\n--- LISTADO COMPLETO DEL PERIODO ---")
        else:
            continue

        if not detail_list:
            print("No hay ventas para mostrar en esta lista.")
        else:
            print(f"{'ID':<5} {'Cliente':<25} {'Monto':<10}")
            print("-" * 45)
            for o in detail_list:
                print(f"{o['id']:<5} {o['customer'][:25]:<25} ${o['total']:<10}")

        input("\nPresione Enter para volver al reporte...")

def export_to_csv(filename, data):
    if not data:
        return False
    
    # Headers adaptados para Excel
    headers = ["ID", "Fecha", "Cliente", "Telefono", "Direccion", "Tipo Entrega", "Envio($)", "Cadete", "Metodo Pago", "Total($)", "Items"]
    
    try:
        # Usamos utf-8-sig para que Excel reconozca los caracteres especiales (tildes, ñ) en Windows
        with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';') # Semicolon es mejor para Excel en español
            writer.writerow(headers)
            
            for o in data:
                # Formatear items como texto simple
                item_list = o['items']
                if item_list and isinstance(item_list[0], dict):
                    items_str = ", ".join([f"{i['name']}" for i in item_list])
                else:
                    items_str = ", ".join(item_list)
                
                writer.writerow([
                    o['id'],
                    o.get('date', ''),
                    o['customer'],
                    o.get('phone', ''),
                    o.get('address', ''),
                    o['delivery_type'],
                    o.get('delivery_fee', 0),
                    o.get('cadete', ''),
                    o.get('payment_method', 'Efectivo'),
                    o['total'],
                    items_str
                ])
        return True
    except Exception as e:
        print(f"Error al escribir CSV: {e}")
        return False

def export_menu(store):
    while True:
        clear_screen()
        print("\n--- EXPORTAR DATOS (EXCEL) ---")
        print("1. Exportar TODO el historial")
        print("2. Exportar solo ventas ONLINE (Mes actual)")
        print("3. Volver")
        
        op = input("\nSeleccione opcion: ").strip()
        
        orders = store.get_orders()
        if not orders and op in ['1', '2']:
            print("No hay datos para exportar.")
            time.sleep(1)
            continue
            
        if op == '1':
            filename = f"historial_completo_{datetime.date.today()}.csv"
            if export_to_csv(filename, orders):
                print(f"\n[EXITO] Archivo creado: {os.path.abspath(filename)}")
            else:
                print("\n[ERROR] No se pudo crear el archivo.")
            input("\nPresione Enter para continuar...")
        elif op == '2':
            this_month = datetime.date.today().strftime("%Y-%m")
            online_orders = [o for o in orders if o.get('payment_method') == 'Online' and o.get('date', '').startswith(this_month)]
            
            if not online_orders:
                print(f"No hay ventas ONLINE en el mes {this_month}.")
                time.sleep(1)
                continue
                
            filename = f"ventas_online_{this_month}.csv"
            if export_to_csv(filename, online_orders):
                print(f"\n[EXITO] Archivo creado: {os.path.abspath(filename)}")
            else:
                print("\n[ERROR] No se pudo crear el archivo.")
            input("\nPresione Enter para continuar...")
        elif op == '3':
            break

def management_menu(store):
    while True:
        clear_screen()
        print("\n--- GESTION DE NEGOCIO ---")
        print("1. Productos (Menú y Precios)")
        print("2. Cadetes (Repartidores)")
        print("3. Volver")
        
        op = input("\nSeleccione opcion: ").strip()
        if op == '1':
            products_menu(store)
        elif op == '2':
            cadetes_menu(store)
        elif op == '3':
            break

def reports_menu(store):
    while True:
        clear_screen()
        print("\n--- REPORTES Y FINANZAS ---")
        print("1. Historial de Pedidos (Detalles y Reimpresión)")
        print("2. Liquidación de Cadetes (Pago diario)")
        print("3. Resumen de Ventas (Fiscal / ARCA)")
        print("4. Volver")
        
        op = input("\nSeleccione opcion: ").strip()
        if op == '1':
            history_menu(store)
        elif op == '2':
            liquidation_menu(store)
        elif op == '3':
            sales_report_menu(store)
        elif op == '4':
            break

def admin_menu(store):
    while True:
        clear_screen()
        print("\n--- ADMINISTRACION ---")
        print("1. GESTION (Productos y Cadetes)")
        print("2. REPORTES (Historial, Liquidación y Fiscal)")
        print("3. EXPORTAR A EXCEL (CSV)")
        print("4. Volver")
        
        op = input("\nSeleccione opcion: ").strip()
        
        if op == '1':
            management_menu(store)
        elif op == '2':
            reports_menu(store)
        elif op == '3':
            export_menu(store)
        elif op == '4':
            break

def main():
    store = Store()
    
    while True:
        clear_screen()
        print_header()
        print("1. Ver Menu")
        print("2. Tomar Pedido")
        print("3. Administrar")
        print("4. Salir")
        
        option = input("\nSeleccione una opcion ([2]): ").strip()
        
        if option == '1':
            clear_screen()
            print_header()
            show_menu(store)
            input("\nPresione Enter para volver...")
        elif option == '2' or option == '':
            clear_screen()
            take_order(store)
        elif option == '3':
            admin_menu(store)
        elif option == '4':
            print("Saliendo del sistema...")
            break
        else:
            print("Opcion invalida.")
            time.sleep(1)

if __name__ == "__main__":
    main()
