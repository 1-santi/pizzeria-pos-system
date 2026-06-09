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

def main_menu(order_svc, product_svc, cadete_svc, report_svc, export_svc, category_svc):
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
            take_order(order_svc, product_svc, cadete_svc)
        elif option == '3':
            admin_menu(order_svc, product_svc, cadete_svc, report_svc, export_svc, category_svc)
        elif option == '4':
            print("Saliendo del sistema...")
            break
        else:
            print("Opcion invalida.")
            time.sleep(1)


# =================================================================
# TOMA DE PEDIDOS
# =================================================================

def take_order(order_svc, product_svc, cadete_svc):
    """Flujo completo de toma de pedidos."""
    print("\n--- TOMAR PEDIDO ---")
    products = product_svc.get_menu()
    if not products:
        print("No hay productos para vender.")
        time.sleep(1)
        return

    # Datos del cliente
    while True:
        customer_name = input("Nombre del cliente: ").strip()
        if customer_name:
            break
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

    # Selección de productos
    order_items = []
    total_items_price = 0

    while True:
        print(f"\nPedido de: {customer_name}")
        print(f"Items: {len(order_items)} | Subtotal: ${total_items_price}")
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
        )

        print(f"\nPEDIDO #{order.id} CREADO CON EXITO!")
        print(f"Cliente: {customer_name}")
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

def admin_menu(order_svc, product_svc, cadete_svc, report_svc, export_svc, category_svc):
    while True:
        clear_screen()
        print("\n--- ADMINISTRACION ---")
        print("1. GESTION (Productos, Cadetes y Categorías)")
        print("2. REPORTES (Historial, Liquidación y Fiscal)")
        print("3. EXPORTAR A EXCEL (CSV)")
        print("4. Volver")

        op = input("\nSeleccione opcion: ").strip()

        if op == '1':
            management_menu(product_svc, cadete_svc, category_svc)
        elif op == '2':
            reports_menu(order_svc, cadete_svc, report_svc)
        elif op == '3':
            export_menu(export_svc)
        elif op == '4':
            break


def management_menu(product_svc, cadete_svc, category_svc):
    while True:
        clear_screen()
        print("\n--- GESTION DE NEGOCIO ---")
        print("1. Productos")
        print("2. Cadetes")
        print("3. Categorías")
        print("4. Volver")

        op = input("\nSeleccione opcion: ").strip()
        if op == '1':
            products_menu(product_svc)
        elif op == '2':
            cadetes_menu(cadete_svc)
        elif op == '3':
            categories_menu(category_svc)
        elif op == '4':
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

def reports_menu(order_svc, cadete_svc, report_svc):
    while True:
        clear_screen()
        print("\n--- REPORTES Y FINANZAS ---")
        print("1. Historial de Pedidos (Detalles y Reimpresión)")
        print("2. Liquidación de Cadetes (Pago diario)")
        print("3. Resumen de Ventas (Fiscal / ARCA)")
        print("4. Volver")

        op = input("\nSeleccione opcion: ").strip()
        if op == '1':
            history_menu(order_svc, cadete_svc)
        elif op == '2':
            liquidation_menu(report_svc)
        elif op == '3':
            sales_report_menu(report_svc)
        elif op == '4':
            break


def history_menu(order_svc, cadete_svc):
    while True:
        clear_screen()
        print("\n--- HISTORIAL DE PEDIDOS ---")

        print("1. Ver todos (últimos 10)")
        print("2. Buscar por nombre de cliente")
        print("3. Filtrar por cadete")
        print("4. Filtrar por medio de pago")
        print("5. Ver por ID de pedido")
        print("6. Volver")

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
