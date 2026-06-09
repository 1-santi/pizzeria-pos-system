"""
Menús de navegación - Toda la interacción con el usuario.
Cada función de menú recibe los servicios que necesita como parámetros
(inyección de dependencias simple).
"""
import time
import datetime

from ui.display import clear_screen, print_header, show_menu, show_order_detail
from ui.input_helpers import parse_quantity_query, search_product, handle_half_and_half
from infra import printer


# =================================================================
# MENÚ PRINCIPAL
# =================================================================

def main_menu(order_svc, product_svc, cadete_svc, report_svc, export_svc, category_svc, zone_svc, customer_svc):
    """Punto de entrada del sistema. Menú principal."""
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
            show_menu(product_svc.get_menu())
            input("\nEnter para volver...")
        elif option == '2' or option == '':
            clear_screen()
            take_order(order_svc, product_svc, cadete_svc, zone_svc, customer_svc)
        elif option == '3':
            admin_menu(order_svc, product_svc, cadete_svc, report_svc, export_svc, category_svc, zone_svc, customer_svc)
        elif option == '4':
            print("Saliendo del sistema...")
            break
        else:
            print("Opcion invalida.")
            time.sleep(1)


# =================================================================
# TOMA DE PEDIDOS
# =================================================================

def take_order(order_svc, product_svc, cadete_svc, zone_svc, customer_svc):
    """Flujo completo de toma de pedidos con búsqueda rápida de clientes."""
    print("\n--- TOMAR PEDIDO ---")
    products = product_svc.get_menu()
    if not products:
        print("No hay productos para vender.")
        time.sleep(1)
        return

    # =====================================================
    # IDENTIFICACIÓN DEL CLIENTE (búsqueda híbrida)
    # =====================================================
    customer = None       # Objeto Customer si se encontró
    customer_id = None    # ID para vincular al pedido
    customer_name = ""
    phone = ""
    address = ""
    zone_id = None
    zone_name = ""

    query = input("Cliente (nombre/teléfono, Enter = nuevo): ").strip()

    if query:
        matches = customer_svc.search(query)

        if len(matches) == 1:
            customer = matches[0]
            print(f"\n[✓] {customer.name}", end="")
            if customer.phone:
                print(f" | Tel: {customer.phone}", end="")
            print()
        elif len(matches) > 1:
            print(f"\n{len(matches)} clientes encontrados:")
            for i, c in enumerate(matches, 1):
                tel = f" | {c.phone}" if c.phone else ""
                print(f"  {i}. {c.name}{tel}")
            print(f"  0. Ninguno (cliente nuevo)")
            sel = input("Seleccione #: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(matches):
                customer = matches[int(sel) - 1]
            # Si elige 0 o inválido, queda customer = None
        else:
            print("[i] No se encontraron clientes.")

    if customer:
        customer_id = customer.id
        customer_name = customer.name
        phone = customer.phone

        # Selección de dirección guardada
        if customer.addresses:
            print(f"\nDirecciones de {customer.name}:")
            for i, addr in enumerate(customer.addresses, 1):
                default_mark = " *" if addr.is_default else ""
                zone_mark = f" ({addr.zone_name})" if addr.zone_name else ""
                print(f"  [{i}] {addr.label:<10} — {addr.address}{zone_mark}{default_mark}")
            print(f"  [{len(customer.addresses)+1}] Otra dirección")

            default_idx = "1"
            a_choice = input(f"Seleccione [{default_idx}]: ").strip() or default_idx
            if a_choice.isdigit() and 1 <= int(a_choice) <= len(customer.addresses):
                chosen = customer.addresses[int(a_choice) - 1]
                address = chosen.address
                zone_id = chosen.zone_id
                zone_name = chosen.zone_name
            else:
                address = input("Dirección: ").strip()
        else:
            address = input("Dirección (Opcional): ").strip()

        if customer.notes:
            print(f"[Nota] {customer.notes}")
    else:
        # Cliente nuevo o sin buscar
        if query and not query[0].isdigit():
            customer_name = query  # Usar lo que ya escribió como nombre
        else:
            customer_name = ""

        while not customer_name:
            customer_name = input("Nombre del cliente: ").strip()
            if not customer_name:
                print("El nombre es obligatorio.")

        phone = input("Teléfono (Opcional): ").strip()
        address = input("Dirección (Opcional): ").strip()

    # Tipo de entrega
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

        # Selección de zona — solo si no se autocompletó de la dirección
        if not zone_id:
            zones = zone_svc.get_zones()
            if zones:
                print("\nZona de reparto:")
                for i, z in enumerate(zones, 1):
                    desc = f" ({z.description})" if z.description else ""
                    print(f"  {i}. {z.name}{desc}")
                z_choice = input(f"Seleccione zona (1-{len(zones)}) [Enter = sin zona]: ").strip()
                if z_choice.isdigit() and 1 <= int(z_choice) <= len(zones):
                    selected_zone = zones[int(z_choice) - 1]
                    zone_id = selected_zone.id
                    zone_name = selected_zone.name
        else:
            print(f"Zona: {zone_name} (de dirección guardada)")

    # =====================================================
    # OFRECER GUARDAR CLIENTE NUEVO
    # =====================================================
    if not customer and customer_name and (phone or address):
        save = input("\n¿Guardar cliente para próximos pedidos? ([s]/n): ").strip().lower()
        if save != 'n':
            customer = customer_svc.create(customer_name, phone)
            customer_id = customer.id
            print(f"[✓] Cliente #{customer.id} guardado.")
            # Guardar dirección si tiene
            if address:
                addr_zone = zone_id if delivery_type == "Envío" else None
                customer_svc.add_address(customer.id, address, "Casa", addr_zone, True)
                print(f"[✓] Dirección guardada.")

    # =====================================================
    # SELECCIÓN DE PRODUCTOS
    # =====================================================
    order_items = []
    total_items_price = 0

    while True:
        print(f"\nPedido de: {customer_name}")
        zone_label = f" | {zone_name}" if zone_name else ""
        print(f"Items: {len(order_items)} | Subtotal: ${total_items_price}{zone_label}")
        print("Opciones: 'menu', 'fin', o producto (ej: 'muzza', '2 x napo')")

        query_input = input("Producto: ").strip()

        if query_input.lower() == 'fin':
            break
        elif query_input.lower() == 'menu':
            show_menu(products)
            continue
        elif query_input.lower() in ['mitad', '1/2']:
            half_item = handle_half_and_half(products)
            if half_item:
                order_items.append(half_item)
                total_items_price += half_item['price']
                print("Mitad y mitad agregada con éxito.")
            continue
        elif not query_input:
            continue

        # Parsear cantidad y buscar
        quantity, query = parse_quantity_query(query_input)
        matches = search_product(query, products)

        selected_pizza = None

        if not matches:
            print("No se encontraron coincidencias.")
        elif len(matches) == 1:
            selected_pizza = matches[0]
            print(f"Agregar {quantity} x {selected_pizza.name} (${selected_pizza.price})?")
            confirm = input("Confirmar ([s]/n): ").lower().strip()
            if confirm != 's' and confirm != '':
                selected_pizza = None
        else:
            print("\nCoincidencias encontradas:")
            for i, p in enumerate(matches):
                print(f"{i+1}. {p.name} (${p.price})")

            sel = input("Seleccione # (0 cancelar): ")
            if sel.isdigit():
                sel_idx = int(sel) - 1
                if 0 <= sel_idx < len(matches):
                    selected_pizza = matches[sel_idx]

        # Agregar al carrito
        if selected_pizza:
            if isinstance(quantity, float):
                # Es una cantidad fraccionaria (ej: 0.5 x Docena)
                item_price = int(selected_pizza.price * quantity)
                item_name = f"{quantity} x {selected_pizza.name}"
                order_items.append({"name": item_name, "price": item_price})
                total_items_price += item_price
                print(f"Agregado {quantity} x {selected_pizza.name} (${item_price}).")
            else:
                for _ in range(quantity):
                    order_items.append({"name": selected_pizza.name, "price": selected_pizza.price})
                    total_items_price += selected_pizza.price
                print(f"Agregado {quantity} items.")

    # Finalizar pedido
    if order_items:
        observation = input("\nObservaciones: ").strip()

        # Selección de cadete
        cadete_name = ""
        if delivery_type == "Envío":
            cadetes = cadete_svc.get_cadetes()
            if cadetes:
                while not cadete_name:
                    print("\nSeleccione Cadete:")
                    for i, c in enumerate(cadetes, 1):
                        print(f"{i}. {c}")
                    c_choice = input("Seleccione #: ").strip()
                    if c_choice.isdigit() and 1 <= int(c_choice) <= len(cadetes):
                        cadete_name = cadetes[int(c_choice) - 1]
                    else:
                        print("[!] Opción inválida. Por favor, elija un cadete de la lista.")
            else:
                print("\n[!] No hay cadetes registrados en el sistema.")
                input("Presione Enter para continuar sin asignar cadete...")

        # Medio de pago
        print("\nMedio de Pago:")
        print("1. Efectivo")
        print("2. Online")
        p_choice = input("Seleccione (1/2) [1]: ").strip()
        payment_method = "Online" if p_choice == "2" else "Efectivo"

        print("\nGenerando documentos...")

        # Crear y persistir el pedido
        order = order_svc.create_order(
            customer=customer_name, phone=phone, address=address,
            observation=observation, delivery_type=delivery_type,
            delivery_fee=delivery_fee, cadete=cadete_name,
            payment_method=payment_method, items=order_items,
            zone_id=zone_id, zone_name=zone_name,
            customer_id=customer_id,
        )

        print(f"\nPEDIDO #{order.id} CREADO CON EXITO!")
        print(f"Cliente: {customer_name}")
        if zone_name:
            print(f"Zona: {zone_name}")
        if delivery_fee > 0:
            print(f"Subtotal: ${total_items_price}")
            print(f"Envío: ${delivery_fee}")
        if cadete_name:
            print(f"Cadete: {cadete_name}")
        print(f"Pago: {payment_method}")
        print(f"Total a cobrar: ${order.total}")

        # Imprimir tickets
        order_svc.print_order(order)

        input("Presione Enter para continuar...")
    else:
        print("Pedido cancelado.")
        time.sleep(1)



# =================================================================
# ADMINISTRACIÓN
# =================================================================

def admin_menu(order_svc, product_svc, cadete_svc, report_svc, export_svc, category_svc, zone_svc, customer_svc):
    while True:
        clear_screen()
        print("\n--- ADMINISTRACION ---")
        print("1. GESTION (Productos, Cadetes, Categorías, Zonas y Clientes)")
        print("2. REPORTES (Historial, Liquidación y Fiscal)")
        print("3. EXPORTAR A EXCEL (CSV)")
        print("4. Volver")

        op = input("\nSeleccione opcion: ").strip()

        if op == '1':
            management_menu(product_svc, cadete_svc, category_svc, zone_svc, customer_svc)
        elif op == '2':
            reports_menu(order_svc, cadete_svc, report_svc, zone_svc)
        elif op == '3':
            export_menu(export_svc)
        elif op == '4':
            break


def management_menu(product_svc, cadete_svc, category_svc, zone_svc, customer_svc):
    while True:
        clear_screen()
        print("\n--- GESTION DE NEGOCIO ---")
        print("1. Productos")
        print("2. Cadetes")
        print("3. Categorías")
        print("4. Zonas de Reparto")
        print("5. Clientes")
        print("6. Volver")

        op = input("\nSeleccione opcion: ").strip()
        if op == '1':
            products_menu(product_svc)
        elif op == '2':
            cadetes_menu(cadete_svc)
        elif op == '3':
            categories_menu(category_svc)
        elif op == '4':
            zones_menu(zone_svc)
        elif op == '5':
            customers_menu(customer_svc, zone_svc)
        elif op == '6':
            break


# =================================================================
# GESTIÓN DE PRODUCTOS
# =================================================================

def products_menu(product_svc):
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

            categories = product_svc.get_categories()
            print("\nCategoría:")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")
            cat_choice = input(f"Seleccione (1-{len(categories)}): ").strip()

            if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                category = categories[int(cat_choice) - 1]
            else:
                category = "Pizza"

            product_svc.add_product(name, price, category)
            print(f"Producto agregado en categoría {category}.")
            time.sleep(1)

        elif op == '2':
            products = product_svc.get_menu()
            show_menu(products)
            query = input("Nombre/ID a editar: ")

            target = None
            if query.isdigit():
                target_id = int(query)
                for p in products:
                    if p.id == target_id:
                        target = p
                        break
            else:
                for p in products:
                    if p.name.lower() == query.lower():
                        target = p
                        break

            if target:
                print(f"Editando {target.name} (${target.price}) - {target.category}")
                new_name = input(f"Nuevo nombre (enter mantener): ").strip()
                new_name = (new_name[:30]) if new_name else target.name

                new_price_input = input(f"Nuevo precio (enter mantener): ")
                try:
                    if new_price_input:
                        new_price = int(new_price_input)
                        if new_price <= 0:
                            print("Precio debe ser > 0. Se mantiene anterior.")
                            new_price = target.price
                    else:
                        new_price = target.price
                except ValueError:
                    print("Valor inválido. Se mantiene anterior.")
                    new_price = target.price

                categories = product_svc.get_categories()
                print("\nNueva categoría:")
                for i, cat in enumerate(categories, 1):
                    print(f"{i}. {cat}")
                print("Enter para mantener")
                cat_choice = input("Seleccione: ").strip()

                if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                    new_category = categories[int(cat_choice) - 1]
                else:
                    new_category = None

                product_svc.update_product(target.id, new_name, new_price, new_category)
                print("Actualizado.")
            else:
                print("No encontrado.")
            time.sleep(1)

        elif op == '3':
            products = product_svc.get_menu()
            show_menu(products)
            query = input("Nombre/ID a eliminar: ")

            target = None
            if query.isdigit():
                target_id = int(query)
                for p in products:
                    if p.id == target_id:
                        target = p
                        break
            else:
                for p in products:
                    if p.name.lower() == query.lower():
                        target = p
                        break

            if target:
                product_svc.remove_product(target.id)
                print(f"Eliminado: {target.name}")
            else:
                print("No encontrado.")
            time.sleep(1)

        elif op == '4':
            break


# =================================================================
# GESTIÓN DE CATEGORÍAS
# =================================================================

def categories_menu(category_svc):
    while True:
        clear_screen()
        print("\n--- GESTION DE CATEGORIAS ---")
        categories = category_svc.get_categories()
        if not categories:
            print("No hay categorías registradas.")
        else:
            print(f"{'ID':<5} {'Nombre':<20}")
            print("-" * 25)
            for cat in categories:
                print(f"{cat.id:<5} {cat.name:<20}")
            print("-" * 25)

        print("\n1. Agregar Categoría")
        print("2. Renombrar Categoría")
        print("3. Eliminar Categoría")
        print("4. Volver")

        op = input("Seleccione opcion: ").strip()
        if op == '1':
            name = input("Nombre de la nueva categoría: ").strip()
            if name:
                if category_svc.add_category(name):
                    print("Categoría agregada.")
                else:
                    print("Error: La categoría ya existe o es inválida.")
            time.sleep(1)
        elif op == '2':
            if not categories:
                print("No hay categorías para renombrar.")
                time.sleep(1)
                continue
            sel = input("Ingrese ID de la categoría a renombrar: ").strip()
            if sel.isdigit():
                cat_id = int(sel)
                target = None
                for cat in categories:
                    if cat.id == cat_id:
                        target = cat
                        break
                if target:
                    new_name = input(f"Nuevo nombre para '{target.name}': ").strip()
                    if new_name:
                        if category_svc.rename_category(cat_id, new_name):
                            print("Categoría renombrada con éxito.")
                        else:
                            print("Error al renombrar. Tal vez el nombre ya existe.")
                    else:
                        print("Nombre inválido.")
                else:
                    print("Categoría no encontrada.")
            time.sleep(1)
        elif op == '3':
            if not categories:
                print("No hay categorías para eliminar.")
                time.sleep(1)
                continue
            sel = input("Ingrese ID de la categoría a eliminar: ").strip()
            if sel.isdigit():
                cat_id = int(sel)
                target = None
                for cat in categories:
                    if cat.id == cat_id:
                        target = cat
                        break
                if target:
                    if category_svc.category_has_products(target.name):
                        print(f"No se puede eliminar la categoría '{target.name}' porque tiene productos asociados.")
                        print("Por favor, edite o elimine esos productos primero.")
                    else:
                        confirm = input(f"¿Está seguro de que desea eliminar la categoría '{target.name}'? (s/N): ").strip().lower()
                        if confirm == 's':
                            category_svc.delete_category(cat_id)
                            print("Categoría eliminada.")
                else:
                    print("Categoría no encontrada.")
            time.sleep(1)
        elif op == '4':
            break


# =================================================================
# GESTIÓN DE ZONAS DE REPARTO
# =================================================================

def zones_menu(zone_svc):
    while True:
        clear_screen()
        print("\n--- GESTION DE ZONAS DE REPARTO ---")
        zones = zone_svc.get_zones()
        if not zones:
            print("No hay zonas registradas.")
        else:
            print(f"{'ID':<5} {'Nombre':<20} {'Descripción'}")
            print("-" * 50)
            for z in zones:
                print(f"{z.id:<5} {z.name:<20} {z.description}")
            print("-" * 50)

        print("\n1. Agregar Zona")
        print("2. Editar Zona")
        print("3. Eliminar Zona")
        print("4. Volver")

        op = input("Seleccione opcion: ").strip()
        if op == '1':
            name = input("Nombre de la zona (ej: Zona 4): ").strip()
            if name:
                desc = input("Descripción (ej: San Benito hasta Colonia): ").strip()
                if zone_svc.add_zone(name, desc):
                    print("Zona agregada.")
                else:
                    print("Error: La zona ya existe o el nombre es inválido.")
            time.sleep(1)
        elif op == '2':
            if not zones:
                print("No hay zonas para editar.")
                time.sleep(1)
                continue
            sel = input("Ingrese ID de la zona a editar: ").strip()
            if sel.isdigit():
                zone_id = int(sel)
                target = None
                for z in zones:
                    if z.id == zone_id:
                        target = z
                        break
                if target:
                    new_name = input(f"Nuevo nombre [{target.name}]: ").strip() or target.name
                    new_desc = input(f"Nueva descripción [{target.description}]: ").strip()
                    if new_desc == "":
                        new_desc = target.description
                    if zone_svc.update_zone(zone_id, new_name, new_desc):
                        print("Zona actualizada.")
                    else:
                        print("Error al actualizar. Tal vez el nombre ya existe.")
                else:
                    print("Zona no encontrada.")
            time.sleep(1)
        elif op == '3':
            if not zones:
                print("No hay zonas para eliminar.")
                time.sleep(1)
                continue
            sel = input("Ingrese ID de la zona a eliminar: ").strip()
            if sel.isdigit():
                zone_id = int(sel)
                target = None
                for z in zones:
                    if z.id == zone_id:
                        target = z
                        break
                if target:
                    if zone_svc.zone_has_orders(zone_id):
                        print(f"[!] La zona '{target.name}' tiene pedidos asociados.")
                        confirm = input("¿Eliminar de todos modos? Los pedidos conservarán el nombre (s/N): ").strip().lower()
                        if confirm != 's':
                            time.sleep(1)
                            continue
                    else:
                        confirm = input(f"¿Eliminar la zona '{target.name}'? (s/N): ").strip().lower()
                        if confirm != 's':
                            time.sleep(1)
                            continue
                    zone_svc.delete_zone(zone_id)
                    print("Zona eliminada.")
                else:
                    print("Zona no encontrada.")
            time.sleep(1)
        elif op == '4':
            break


# =================================================================
# GESTIÓN DE CADETES
# =================================================================

def cadetes_menu(cadete_svc):
    while True:
        clear_screen()
        print("\n--- GESTION DE CADETES ---")
        cadetes = cadete_svc.get_cadetes()
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
                cadete_svc.add_cadete(name)
                print("Cadete agregado.")
            time.sleep(1)
        elif op == '2':
            if not cadetes:
                print("Nada que eliminar.")
            else:
                sel = input("Seleccione # a eliminar: ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(cadetes):
                    name = cadetes[int(sel) - 1]
                    cadete_svc.remove_cadete(name)
                    print(f"Cadete {name} eliminado.")
            time.sleep(1)
        elif op == '3':
            break


# =================================================================
# REPORTES Y FINANZAS
# =================================================================

def reports_menu(order_svc, cadete_svc, report_svc, zone_svc):
    while True:
        clear_screen()
        print("\n--- REPORTES Y FINANZAS ---")
        print("1. Historial de Pedidos (Detalles y Reimpresión)")
        print("2. Liquidación de Cadetes (Pago diario)")
        print("3. Resumen de Ventas (Fiscal / ARCA)")
        print("4. Volver")

        op = input("\nSeleccione opcion: ").strip()
        if op == '1':
            history_menu(order_svc, cadete_svc, zone_svc)
        elif op == '2':
            liquidation_menu(report_svc)
        elif op == '3':
            sales_report_menu(report_svc)
        elif op == '4':
            break


def history_menu(order_svc, cadete_svc, zone_svc):
    while True:
        clear_screen()
        print("\n--- HISTORIAL DE PEDIDOS ---")

        print("1. Ver todos (últimos 10)")
        print("2. Buscar por nombre de cliente")
        print("3. Filtrar por cadete")
        print("4. Filtrar por medio de pago")
        print("5. Filtrar por zona de reparto")
        print("6. Ver por ID de pedido")
        print("7. Volver")

        choice = input("\nSeleccione opcion: ").strip()

        filtered_orders = []
        if choice == '1':
            all_orders = order_svc.get_orders()
            filtered_orders = all_orders[-10:] if all_orders else []
        elif choice == '2':
            query = input("Nombre a buscar: ").lower()
            all_orders = order_svc.get_orders()
            filtered_orders = [o for o in all_orders if query in o.customer.lower()]
        elif choice == '3':
            cadetes = cadete_svc.get_cadetes()
            if not cadetes:
                print("No hay cadetes registrados.")
                time.sleep(1)
                continue
            for i, c in enumerate(cadetes, 1):
                print(f"{i}. {c}")
            c_sel = input("Seleccione cadete #: ").strip()
            if c_sel.isdigit() and 1 <= int(c_sel) <= len(cadetes):
                c_name = cadetes[int(c_sel) - 1]
                filtered_orders = order_svc.get_orders(cadete_filter=c_name)
        elif choice == '4':
            print("1. Efectivo")
            print("2. Online")
            p_sel = input("Seleccione pago (1/2): ").strip()
            p_method = "Online" if p_sel == "2" else "Efectivo"
            filtered_orders = order_svc.get_orders(payment_filter=p_method)
        elif choice == '5':
            zones = zone_svc.get_zones()
            if not zones:
                print("No hay zonas registradas.")
                time.sleep(1)
                continue
            for i, z in enumerate(zones, 1):
                print(f"{i}. {z.name}")
            z_sel = input("Seleccione zona #: ").strip()
            if z_sel.isdigit() and 1 <= int(z_sel) <= len(zones):
                z_id = zones[int(z_sel) - 1].id
                filtered_orders = order_svc.get_orders(zone_filter=z_id)
            else:
                print("Opción inválida.")
                time.sleep(1)
                continue
        elif choice == '6':
            oid = input("Ingrese ID del pedido: ").strip()
            if oid.isdigit():
                target = order_svc.get_order_by_id(int(oid))
                if target:
                    order_detail_menu(order_svc, target)
                    continue
                else:
                    print("Pedido no encontrado.")
                    time.sleep(1)
            continue
        elif choice == '7':
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
            print(f"{o.id:<4} {o.date:<20} {o.customer:<20} ${o.total:<10}")

        sel = input("\nIngrese ID para ver detalle (Enter para volver): ").strip()
        if sel.isdigit():
            target = order_svc.get_order_by_id(int(sel))
            if target:
                order_detail_menu(order_svc, target)


def order_detail_menu(order_svc, order):
    """Detalle de un pedido con opciones de reimpresión."""
    while True:
        clear_screen()
        show_order_detail(order)

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


def liquidation_menu(report_svc):
    """Liquidación diaria de cadetes."""
    clear_screen()
    print("\n--- LIQUIDACION DE CADETES ---")
    print("Calculando para el día de hoy...")

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    results = report_svc.get_cadete_liquidation(today_str)

    if not results:
        print("No hay datos de cadetes para hoy.")
        input("\nPresione Enter para volver...")
        return

    from config import BASE_PAY_CADETE

    print(f"\nFecha: {today_str}")
    print(f"{'Cadete':<20} {'Envios':<8} {'Comision':<10} {'Base':<10} {'Total':<10}")
    print("-" * 65)

    for r in results:
        name_display = (r['name'] + r['status'])[:20]
        print(f"{name_display:<20} {r['envios']:<8} ${r['comision']:<9} ${r['base']:<9} ${r['total']:<9}")

    print("-" * 65)
    input("\nPresione Enter para volver...")


def sales_report_menu(report_svc):
    """Reporte fiscal con resumen de ventas por medio de pago."""
    while True:
        clear_screen()
        print("\n--- REPORTE FISCAL (VENTAS POR MEDIO DE PAGO) ---")
        print("1. Hoy")
        print("2. Día específico (AAAA-MM-DD)")
        print("3. Mes específico (AAAA-MM)")
        print("4. Todo el historial")
        print("5. Volver")

        op = input("\nSeleccione periodo: ").strip()
        if op == '5':
            break

        date_filter = None
        period_label = ""

        if op == '1':
            date_filter = datetime.date.today().strftime("%Y-%m-%d")
            period_label = f"HOY ({date_filter})"
        elif op == '2':
            date_filter = input("Ingrese fecha (EJ: 2026-01-20): ").strip()
            period_label = f"DIA ({date_filter})"
        elif op == '3':
            date_filter = input("Ingrese mes (EJ: 2026-01): ").strip()
            period_label = f"MES ({date_filter})"
        elif op == '4':
            period_label = "TOTAL HISTORICO"
        else:
            continue

        summary = report_svc.get_sales_summary(date_filter)

        if summary['total_general'] == 0 and not summary['orders']:
            print(f"\nNo se encontraron ventas para: {period_label}")
            input("Enter para continuar...")
            continue
        print(f"\n=== RESUMEN {period_label} ===")
        print("-" * 40)
        print(f"EFECTIVO (EF):    ${summary['total_efectivo']:>10}")
        print(f"ONLINE (ONL):      ${summary['total_online']:>10}")
        print("-" * 40)
        print(f"TOTAL GENERAL:     ${summary['total_general']:>10}")
        print("-" * 40)

        # Mostrar resumen por zonas
        if 'sales_by_zone' in summary and summary['sales_by_zone']:
            print("\nVentas por Zona de Reparto:")
            print("-" * 40)
            for z_name, z_total in sorted(summary['sales_by_zone'].items()):
                print(f"  {z_name:<25} ${z_total:>10}")
            print("-" * 40)

        print("\n¿Desea ver el listado detallado?")
        print("1. Ver solo ventas ONLINE (para ARCA)")
        print("2. Ver todas las ventas del periodo")
        print("3. Exportar este resumen a PDF")
        print("4. No, volver")

        list_op = input("Seleccione: ").strip()

        if list_op == '3':
            report_svc.print_fiscal_report(period_label, summary)
            input("\nProceso de exportación finalizado. Presione Enter para continuar...")
            continue

        detail_list = []
        if list_op == '1':
            detail_list = summary['online_orders']
            print("\n--- LISTADO ONLINE PARA FACTURAR ---")
        elif list_op == '2':
            detail_list = summary['orders']
            print("\n--- LISTADO COMPLETO DEL PERIODO ---")
        else:
            continue

        if not detail_list:
            print("No hay ventas para mostrar en esta lista.")
        else:
            print(f"{'ID':<5} {'Cliente':<25} {'Monto':<10}")
            print("-" * 45)
            for o in detail_list:
                print(f"{o.id:<5} {o.customer[:25]:<25} ${o.total:<10}")

        input("\nPresione Enter para volver al reporte...")


# =================================================================
# EXPORTACIÓN
# =================================================================

def export_menu(export_svc):
    while True:
        clear_screen()
        print("\n--- EXPORTAR DATOS (EXCEL) ---")
        print("1. Exportar TODO el historial")
        print("2. Exportar solo ventas ONLINE (Mes actual)")
        print("3. Volver")

        op = input("\nSeleccione opcion: ").strip()

        if op == '1':
            result = export_svc.export_all()
            if result:
                print(f"\n[EXITO] Archivo creado: {result}")
            else:
                print("\n[ERROR] No se pudo crear el archivo o no hay datos.")
            input("\nPresione Enter para continuar...")
        elif op == '2':
            result = export_svc.export_online_month()
            if result:
                print(f"\n[EXITO] Archivo creado: {result}")
            else:
                print("\nNo hay ventas ONLINE en el mes actual o hubo un error.")
            input("\nPresione Enter para continuar...")
        elif op == '3':
            break


# =================================================================
# GESTIÓN DE CLIENTES
# =================================================================

def customers_menu(customer_svc, zone_svc):
    while True:
        clear_screen()
        print("\n--- GESTION DE CLIENTES ---")
        customers = customer_svc.get_all()
        if not customers:
            print("No hay clientes registrados.")
        else:
            print(f"{'ID':<5} {'Nombre':<25} {'Teléfono':<15} {'Notas'}")
            print("-" * 70)
            for c in customers:
                notes_trunc = (c.notes[:25] + "...") if c.notes and len(c.notes) > 25 else (c.notes or "")
                print(f"{c.id:<5} {c.name:<25} {c.phone:<15} {notes_trunc}")
            print("-" * 70)

        print("\n1. Agregar Cliente")
        print("2. Editar Cliente (Datos Básicos / Direcciones)")
        print("3. Eliminar Cliente")
        print("4. Volver")

        op = input("Seleccione opcion: ").strip()
        if op == '1':
            name = input("Nombre del cliente: ").strip()
            if not name:
                print("El nombre es obligatorio.")
                time.sleep(1)
                continue
            phone = input("Teléfono: ").strip()
            notes = input("Notas/Observaciones: ").strip()
            customer_svc.create(name, phone, notes)
            print("Cliente creado.")
            time.sleep(1)
        elif op == '2':
            if not customers:
                print("No hay clientes para editar.")
                time.sleep(1)
                continue
            sel = input("Ingrese ID del cliente a editar: ").strip()
            if sel.isdigit():
                customer_id = int(sel)
                target = customer_svc.get_by_id(customer_id)
                if target:
                    edit_customer_submenu(customer_svc, zone_svc, target)
                else:
                    print("Cliente no encontrado.")
                    time.sleep(1)
        elif op == '3':
            if not customers:
                print("No hay clientes para eliminar.")
                time.sleep(1)
                continue
            sel = input("Ingrese ID del cliente a eliminar: ").strip()
            if sel.isdigit():
                customer_id = int(sel)
                target = customer_svc.get_by_id(customer_id)
                if target:
                    order_count = customer_svc.get_order_count(customer_id)
                    if order_count > 0:
                        print(f"[!] El cliente '{target.name}' tiene {order_count} pedidos asociados.")
                        confirm = input("¿Eliminar de todos modos? Sus datos en los pedidos históricos se mantendrán (s/N): ").strip().lower()
                        if confirm != 's':
                            continue
                    else:
                        confirm = input(f"¿Eliminar al cliente '{target.name}'? (s/N): ").strip().lower()
                        if confirm != 's':
                            continue
                    customer_svc.delete(customer_id)
                    print("Cliente eliminado.")
                else:
                    print("Cliente no encontrado.")
            time.sleep(1)
        elif op == '4':
            break


def edit_customer_submenu(customer_svc, zone_svc, customer):
    while True:
        clear_screen()
        customer = customer_svc.get_by_id(customer.id)
        if not customer:
            print("Error: El cliente ya no existe.")
            time.sleep(1)
            break

        print(f"\n--- EDITAR CLIENTE: {customer.name} (ID: {customer.id}) ---")
        print(f"Nombre:   {customer.name}")
        print(f"Teléfono: {customer.phone}")
        print(f"Notas:    {customer.notes}")
        print("\nDirecciones:")
        if not customer.addresses:
            print("  Sin direcciones registradas.")
        else:
            for i, addr in enumerate(customer.addresses, 1):
                def_mark = " * [PRINCIPAL]" if addr.is_default else ""
                zone_mark = f" (Zona: {addr.zone_name})" if addr.zone_name else " (Sin Zona)"
                print(f"  {i}. [{addr.label}] {addr.address}{zone_mark}{def_mark}")

        print("\nOpciones:")
        print("1. Editar datos básicos (Nombre, Teléfono, Notas)")
        print("2. Agregar nueva dirección")
        print("3. Editar dirección existente")
        print("4. Eliminar dirección")
        print("5. Ver historial de pedidos")
        print("6. Volver")

        op = input("Seleccione opcion: ").strip()
        if op == '1':
            new_name = input(f"Nuevo nombre [{customer.name}]: ").strip() or customer.name
            new_phone = input(f"Nuevo teléfono [{customer.phone}]: ").strip() or customer.phone
            new_notes = input(f"Nuevas notas [{customer.notes}]: ").strip() or customer.notes
            customer_svc.update(customer.id, new_name, new_phone, new_notes)
            print("Datos actualizados.")
            time.sleep(1)
        elif op == '2':
            addr_str = input("Dirección (calle, número, etc.): ").strip()
            if not addr_str:
                print("La dirección no puede estar vacía.")
                time.sleep(1)
                continue
            label = input("Etiqueta (ej: Casa, Trabajo, Oficina) [Casa]: ").strip() or "Casa"

            zones = zone_svc.get_zones()
            zone_id = None
            if zones:
                print("\nSeleccione Zona:")
                for i, z in enumerate(zones, 1):
                    desc = f" ({z.description})" if z.description else ""
                    print(f"  {i}. {z.name}{desc}")
                z_choice = input("Seleccione zona #: ").strip()
                if z_choice.isdigit() and 1 <= int(z_choice) <= len(zones):
                    zone_id = zones[int(z_choice) - 1].id

            is_default_input = input("¿Establecer como dirección principal? (s/N): ").strip().lower()
            is_default = (is_default_input == 's')

            customer_svc.add_address(customer.id, addr_str, label, zone_id, is_default)
            print("Dirección agregada.")
            time.sleep(1)
        elif op == '3':
            if not customer.addresses:
                print("No hay direcciones para editar.")
                time.sleep(1)
                continue
            sel = input("Ingrese número de dirección a editar: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(customer.addresses):
                addr = customer.addresses[int(sel) - 1]
                new_addr_str = input(f"Nueva dirección [{addr.address}]: ").strip() or addr.address
                new_label = input(f"Nueva etiqueta [{addr.label}]: ").strip() or addr.label

                zones = zone_svc.get_zones()
                zone_id = addr.zone_id
                if zones:
                    curr_zone_label = f" (Actual: {addr.zone_name})" if addr.zone_name else " (Actual: Ninguna)"
                    print(f"\nSeleccione Zona{curr_zone_label}:")
                    for i, z in enumerate(zones, 1):
                        desc = f" ({z.description})" if z.description else ""
                        print(f"  {i}. {z.name}{desc}")
                    print("  0. Quitar zona")
                    z_choice = input("Seleccione zona # (Enter para mantener): ").strip()
                    if z_choice == '0':
                        zone_id = None
                    elif z_choice.isdigit() and 1 <= int(z_choice) <= len(zones):
                        zone_id = zones[int(z_choice) - 1].id

                is_default_input = input(f"¿Establecer como dirección principal? (Actual: {addr.is_default}) (s/N): ").strip().lower()
                is_default = (is_default_input == 's') if is_default_input else addr.is_default

                customer_svc.update_address(addr.id, new_addr_str, new_label, zone_id, is_default)
                print("Dirección actualizada.")
            else:
                print("Opción inválida.")
            time.sleep(1)
        elif op == '4':
            if not customer.addresses:
                print("No hay direcciones para eliminar.")
                time.sleep(1)
                continue
            sel = input("Ingrese número de dirección a eliminar: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(customer.addresses):
                addr = customer.addresses[int(sel) - 1]
                confirm = input(f"¿Eliminar la dirección '{addr.label}: {addr.address}'? (s/N): ").strip().lower()
                if confirm == 's':
                    customer_svc.delete_address(addr.id)
                    print("Dirección eliminada.")
            else:
                print("Opción inválida.")
            time.sleep(1)
        elif op == '5':
            orders = customer_svc.get_orders(customer.id)
            if not orders:
                print("El cliente no tiene pedidos registrados.")
            else:
                clear_screen()
                print(f"\n--- HISTORIAL DE PEDIDOS: {customer.name} ---")
                print(f"{'ID':<5} {'Fecha':<20} {'Total':<10}")
                print("-" * 40)
                for o in orders:
                    print(f"{o.id:<5} {o.date:<20} ${o.total:<10}")
                print("-" * 40)

                sel = input("\nIngrese ID de pedido para ver detalle (Enter para volver): ").strip()
                if sel.isdigit():
                    target = None
                    for o in orders:
                        if o.id == int(sel):
                            target = o
                            break
                    if target:
                        clear_screen()
                        show_order_detail(target)
                        input("\nPresione Enter para continuar...")
            time.sleep(1)
        elif op == '6':
            break

