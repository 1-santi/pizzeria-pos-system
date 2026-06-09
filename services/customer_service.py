"""Servicio de clientes - Búsqueda híbrida, CRUD y gestión de direcciones."""
from typing import List, Optional
from domain.models import Customer, CustomerAddress
from infra.database import Database


class CustomerService:
    def __init__(self, db: Database):
        self.db = db

    # ----- CLIENTES -----

    def search(self, query: str) -> List[Customer]:
        """Búsqueda híbrida: número → teléfono, texto → nombre."""
        if not query:
            return []
        return self.db.search_customers(query)

    def find_one(self, query: str) -> Optional[Customer]:
        """Busca y retorna el primer resultado, o None."""
        results = self.search(query)
        return results[0] if len(results) == 1 else None

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        return self.db.get_customer_by_id(customer_id)

    def get_all(self) -> List[Customer]:
        return self.db.get_all_customers()

    def create(self, name: str, phone: str = "", notes: str = "") -> Customer:
        """Crea un cliente y retorna el objeto completo."""
        cid = self.db.add_customer(name, phone, notes)
        return Customer(id=cid, name=name, phone=phone, notes=notes)

    def update(self, customer_id: int, name: str, phone: str, notes: str) -> bool:
        return self.db.update_customer(customer_id, name, phone, notes)

    def delete(self, customer_id: int) -> bool:
        return self.db.remove_customer(customer_id)

    def get_order_count(self, customer_id: int) -> int:
        return self.db.get_customer_order_count(customer_id)

    # ----- DIRECCIONES -----

    def add_address(self, customer_id: int, address: str, label: str = "Casa",
                    zone_id: int = None, is_default: bool = False) -> int:
        return self.db.add_customer_address(customer_id, address, label, zone_id, is_default)

    def update_address(self, address_id: int, address: str, label: str,
                       zone_id: int = None, is_default: bool = False) -> bool:
        return self.db.update_customer_address(address_id, address, label, zone_id, is_default)

    def delete_address(self, address_id: int) -> bool:
        return self.db.remove_customer_address(address_id)
