"""Servicio de categorías - CRUD de categorías de productos."""
from typing import List
from domain.models import Category
from infra.database import Database


class CategoryService:
    def __init__(self, db: Database):
        self.db = db

    def get_categories(self) -> List[Category]:
        return self.db.get_categories()

    def add_category(self, name: str) -> bool:
        if not name:
            return False
        return self.db.add_category(name[:30])

    def rename_category(self, category_id: int, new_name: str) -> bool:
        if not new_name:
            return False
        return self.db.update_category(category_id, new_name[:30])

    def delete_category(self, category_id: int) -> bool:
        return self.db.remove_category(category_id)

    def category_has_products(self, category_name: str) -> bool:
        return self.db.category_has_products(category_name)
