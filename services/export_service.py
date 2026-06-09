"""Servicio de exportación - Genera archivos CSV compatibles con Excel."""
import csv
import os
import datetime
from typing import List

from domain.models import Order
from infra.database import Database


class ExportService:
    def __init__(self, db: Database):
        self.db = db

    def export_to_csv(self, filename: str, orders: List[Order]) -> bool:
        """Exporta una lista de pedidos a CSV (separador ; para Excel en español)."""
        if not orders:
            return False

        headers = [
            "ID", "Fecha", "Cliente", "Telefono", "Direccion",
            "Zona", "Tipo Entrega", "Envio($)", "Cadete", "Metodo Pago",
            "Total($)", "Items",
        ]

        try:
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(headers)

                for o in orders:
                    items_str = ", ".join(item.name for item in o.items)
                    writer.writerow([
                        o.id, o.date, o.customer, o.phone, o.address,
                        o.zone_name or "", o.delivery_type, o.delivery_fee, o.cadete,
                        o.payment_method, o.total, items_str,
                    ])
            return True
        except Exception as e:
            print(f"Error al escribir CSV: {e}")
            return False

    def export_all(self) -> str:
        """Exporta todo el historial. Retorna la ruta del archivo o '' si falla."""
        orders = self.db.get_orders()
        filename = f"historial_completo_{datetime.date.today()}.csv"
        if self.export_to_csv(filename, orders):
            return os.path.abspath(filename)
        return ""

    def export_online_month(self) -> str:
        """Exporta ventas online del mes actual."""
        this_month = datetime.date.today().strftime("%Y-%m")
        orders = self.db.get_orders(payment_filter="Online", date_filter=this_month)
        if not orders:
            return ""
        filename = f"ventas_online_{this_month}.csv"
        if self.export_to_csv(filename, orders):
            return os.path.abspath(filename)
        return ""
