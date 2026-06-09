"""Servicio de productos - CRUD del menú."""
from domain.models import Product
from infra.database import Database


class ProductService:
    def __init__(self, db: Database):
        self.db = db

    def get_menu(self):
        return self.db.get_menu()

    def get_categories(self):
        return [c.name for c in self.db.get_categories()]

    def add_product(self, name, price, category="Pizza"):
        product = Product(name=name[:30], price=price, category=category)
        return self.db.add_product(product)

    def update_product(self, product_id, name, price, category=None):
        return self.db.update_product(product_id, name[:30], price, category)

    def remove_product(self, product_id):
        return self.db.remove_product(product_id)
