"""
Modelos del dominio - Entidades del negocio.
Dataclasses tipadas que representan los objetos centrales del sistema.
Sin dependencias de infraestructura (DB, impresora, etc.).
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Category:
    """Representa una categoría de productos (Pizza, Empanadas, Papas, etc.)."""
    name: str
    id: Optional[int] = None


@dataclass
class Zone:
    """Representa una zona de reparto (ej: Zona 1 — San Benito y Colonia)."""
    name: str
    description: str = ""
    id: Optional[int] = None


@dataclass
class Product:
    """Representa un producto del menú (pizza, papas, empanada)."""
    name: str
    price: int
    category: str = "Pizza"
    id: Optional[int] = None


@dataclass
class OrderItem:
    """Snapshot de un producto en el momento de la venta.
    Se almacena con el pedido para preservar el precio histórico."""
    name: str
    price: int


@dataclass
class Order:
    """Representa un pedido completo del sistema."""
    customer: str
    delivery_type: str
    items: List[OrderItem] = field(default_factory=list)
    total: int = 0
    id: Optional[int] = None
    date: str = ""
    phone: str = ""
    address: str = ""
    observation: str = ""
    delivery_fee: int = 0
    cadete: str = ""
    payment_method: str = "Efectivo"
    zone_id: Optional[int] = None
    zone_name: str = ""

