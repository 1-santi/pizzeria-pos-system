"""Servicio de cadetes - Alta y baja de repartidores."""
from infra.database import Database


class CadeteService:
    def __init__(self, db: Database):
        self.db = db

    def get_cadetes(self):
        return self.db.get_cadetes()

    def add_cadete(self, name):
        return self.db.add_cadete(name)

    def remove_cadete(self, name):
        return self.db.remove_cadete(name)
