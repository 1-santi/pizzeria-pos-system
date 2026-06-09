"""Servicio de pedidos - Orquesta la creación y consulta de pedidos."""
import datetime
from domain.models import Order, OrderItem
from domain.pricing import calculate_order_total
from infra.database import Database
from infra import printer


class OrderService:
    def __init__(self, db: Database):
        self.db = db

    def create_order(self, customer, phone, address, observation,
                     delivery_type, delivery_fee, cadete, payment_method,
                     items: list, zone_id=None, zone_name="") -> Order:
        """Crea un pedido completo, lo persiste e imprime."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        order_items = [OrderItem(name=i['name'], price=i['price']) for i in items]
        total = calculate_order_total(order_items, delivery_fee)

        order = Order(
            customer=customer, phone=phone, address=address,
            observation=observation, delivery_type=delivery_type,
            delivery_fee=delivery_fee, cadete=cadete,
            payment_method=payment_method, items=order_items,
            total=total, date=timestamp,
            zone_id=zone_id, zone_name=zone_name,
        )

        order.id = self.db.add_order(order)
        return order

    def print_order(self, order: Order):
        """Imprime comanda de cocina y ticket de control."""
        printer.print_kitchen_order(order)
        printer.print_control_ticket(order)

    def get_orders(self, **filters):
        return self.db.get_orders(**filters)

    def get_order_by_id(self, order_id: int):
        return self.db.get_order_by_id(order_id)
