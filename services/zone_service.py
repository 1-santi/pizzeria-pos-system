"""Servicio de zonas de reparto - CRUD de zonas."""
from typing import List
from domain.models import Zone
from infra.database import Database


class ZoneService:
    def __init__(self, db: Database):
        self.db = db

    def get_zones(self) -> List[Zone]:
        return self.db.get_zones()

    def add_zone(self, name: str, description: str = "") -> bool:
        if not name:
            return False
        return self.db.add_zone(name[:30], description[:100])

    def update_zone(self, zone_id: int, name: str, description: str) -> bool:
        if not name:
            return False
        return self.db.update_zone(zone_id, name[:30], description[:100])

    def delete_zone(self, zone_id: int) -> bool:
        return self.db.remove_zone(zone_id)

    def zone_has_orders(self, zone_id: int) -> bool:
        return self.db.zone_has_orders(zone_id)
