"""
Helpers de input - Parseo de cantidades, búsqueda de productos,
y flujo interactivo de mitad y mitad.
"""
import re
from typing import Optional, Tuple, List

from domain.models import Product
from domain.pricing import calculate_half_and_half_price


def parse_quantity_query(query_input: str) -> Tuple[float, str]:
    """Parsea inputs como '2xmuzza', '0.5 x docena saladas', o 'fugazzeta'.
    Retorna (cantidad, texto_de_búsqueda)."""
    query_input = query_input.strip()
    # Permitir números enteros o decimales (ej: 0.5, 1.5, 2)
    match = re.match(r'^(\d+(?:\.\d+)?)\s*[xX]\s*(.*)$', query_input)
    if match:
        try:
            quantity = float(match.group(1))
            if quantity.is_integer():
                quantity = int(quantity)
        except ValueError:
            quantity = 1
        query = match.group(2).strip()
        return quantity, query
    return 1, query_input


def search_product(query: str, products: List[Product]) -> List[Product]:
    """Busca productos por ID de base de datos o texto parcial en el nombre."""
    if query.isdigit():
        target_id = int(query)
        for p in products:
            if p.id == target_id:
                return [p]
        return []
    return [p for p in products if query.lower() in p.name.lower()]


def select_product(products: List[Product], prompt: str) -> Optional[Product]:
    """Busca y selecciona un producto interactivamente."""
    query = input(prompt).strip()
    if not query:
        return None

    matches = search_product(query, products)

    if not matches:
        print("No se encontró el producto.")
        return None
    if len(matches) == 1:
        return matches[0]

    print("\nSeleccione una opción:")
    for i, p in enumerate(matches):
        print(f"{i+1}. {p.name} (${p.price})")
    sel = input("Seleccione # (0 cancelar): ")
    if sel.isdigit():
        idx = int(sel) - 1
        if 0 <= idx < len(matches):
            return matches[idx]
    return None


def handle_half_and_half(products: List[Product]) -> Optional[dict]:
    """Flujo interactivo para armar una pizza mitad y mitad (solo pizzas grandes)."""
    # Filtrar solo productos que sean de la categoría Pizza y tengan "grande" en el nombre
    pizzas_grandes = [p for p in products if p.category.lower() == "pizza" and "grande" in p.name.lower()]

    if not pizzas_grandes:
        print("No hay pizzas grandes cargadas en el menú para armar mitades.")
        return None

    print("\n--- SELECCION DE MITADES (SOLO PIZZAS GRANDES) ---")
    print("Sabor 1:")
    sabor1 = select_product(pizzas_grandes, "Buscar primer sabor grande: ")
    if not sabor1:
        return None
    print(f"Sabor 1: {sabor1.name} (${sabor1.price})")

    print("\nSabor 2:")
    sabor2 = select_product(pizzas_grandes, "Buscar segundo sabor grande: ")
    if not sabor2:
        return None
    print(f"Sabor 2: {sabor2.name} (${sabor2.price})")

    final_price = calculate_half_and_half_price(sabor1.price, sabor2.price)
    final_name = f"1/2 {sabor1.name} / 1/2 {sabor2.name}"

    print("-" * 40)
    print(f"Resumen:")
    print(f"Items: {final_name}")
    print(f"Precio: ${final_price}")

    confirm = input("¿Confirmar esta mitad y mitad? ([s]/n): ").lower().strip()
    if confirm == 's' or confirm == '':
        return {"name": final_name, "price": final_price}
    return None
