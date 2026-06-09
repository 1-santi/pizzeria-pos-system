"""
Funciones de visualización y formateo de pantalla.
Maneja todo lo que se muestra al usuario en la consola.
"""
import os
from collections import defaultdict, Counter


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


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


def show_menu(products):
    """Muestra el menú completo agrupado por categoría."""
    if not products:
        print("No hay productos en el sistema.")
        return

    categories = defaultdict(list)
    for item in products:
        categories[item.category].append(item)

    item_id = 1
    for category in sorted(categories.keys()):
        print(f"\n=== {category.upper()} ===")
        print(f"{'ID':<4} {'Nombre':<25} {'Precio':<10}")
        print("-" * 45)
        for product in categories[category]:
            print(f"{item_id:<4} {product.name:<25} ${product.price:<9}")
            item_id += 1
        print("-" * 45)


def show_order_detail(order):
    """Muestra el detalle completo de un pedido."""
    print("\n--- DETALLE DE PEDIDO #" + str(order.id) + " ---")
    print(f"Fecha:     {order.date}")
    print(f"Cliente:   {order.customer}")
    if order.phone:
        print(f"Telefono:  {order.phone}")
    if order.address:
        print(f"Direccion: {order.address}")
    print(f"Entrega:   {order.delivery_type}")
    if order.cadete:
        print(f"Cadete:    {order.cadete}")
    print(f"Pago:      {order.payment_method}")
    print("-" * 40)
    print(f"{'Cant':<5} {'Producto':<25} {'Precio':<10}")

    item_tuples = [(i.name, i.price) for i in order.items]
    counts = Counter(item_tuples)
    for (name, price), qty in counts.items():
        print(f"{qty:<5} {name[:25]:<25} ${price * qty}")

    print("-" * 40)
    if order.delivery_fee > 0:
        subtotal = order.total - order.delivery_fee
        print(f"Subtotal:  ${subtotal}")
        print(f"Envio:     ${order.delivery_fee}")
    print(f"TOTAL:     ${order.total}")
    if order.observation:
        print(f"Obs:       {order.observation}")
    print("-" * 40)
