"""
Reglas de precios del dominio.
Lógica de negocio pura, sin dependencias externas.
"""
from typing import List
from domain.models import OrderItem


def calculate_half_and_half_price(price1: int, price2: int) -> int:
    """Mitad y mitad: se cobra el precio del sabor más caro."""
    return max(price1, price2)


def calculate_order_total(items: List[OrderItem], delivery_fee: int = 0) -> int:
    """Calcula el total del pedido: suma de ítems + envío."""
    return sum(item.price for item in items) + delivery_fee
