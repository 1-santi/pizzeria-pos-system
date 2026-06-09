"""Servicio de reportes - Liquidación de cadetes y reportes fiscales."""
import datetime
from typing import List, Dict, Any, Optional

from infra.database import Database
from infra import printer
from config import BASE_PAY_CADETE


class ReportService:
    def __init__(self, db: Database):
        self.db = db

    def get_cadete_liquidation(self, date_str: str = None) -> List[Dict[str, Any]]:
        """Calcula la liquidación diaria de cada cadete."""
        if not date_str:
            date_str = datetime.date.today().strftime("%Y-%m-%d")

        cadetes = self.db.get_cadetes()
        orders = self.db.get_orders(date_filter=date_str)

        # Incluir cadetes que trabajaron hoy aunque hayan sido eliminados
        cadetes_who_worked = set(o.cadete for o in orders if o.cadete)
        all_to_report = sorted(cadetes_who_worked.union(set(cadetes)))

        results = []
        for c_name in all_to_report:
            c_orders = [o for o in orders if o.cadete == c_name]
            if not c_orders:
                continue

            status = "" if c_name in cadetes else " (ELIMINADO)"
            envios_count = len(c_orders)
            comision_total = sum(o.delivery_fee for o in c_orders)
            final_total = BASE_PAY_CADETE + comision_total

            results.append({
                'name': c_name,
                'status': status,
                'envios': envios_count,
                'comision': comision_total,
                'base': BASE_PAY_CADETE,
                'total': final_total,
            })

        return results

    def get_sales_summary(self, date_filter: str = None) -> Dict[str, Any]:
        """Resumen fiscal: totales por medio de pago."""
        if date_filter:
            orders = self.db.get_orders(date_filter=date_filter)
        else:
            orders = self.db.get_orders()

        total_ef = sum(o.total for o in orders if o.payment_method == 'Efectivo')
        total_onl = sum(o.total for o in orders if o.payment_method == 'Online')

        return {
            'total_efectivo': total_ef,
            'total_online': total_onl,
            'total_general': total_ef + total_onl,
            'orders': orders,
            'online_orders': [o for o in orders if o.payment_method == 'Online'],
        }

    def print_fiscal_report(self, period_label: str, summary: Dict[str, Any]):
        """Genera un reporte fiscal formateado para impresión/PDF."""
        report_lines = []
        report_lines.append(printer.center_text("REPORTE FISCAL DE VENTAS"))
        report_lines.append(printer.center_text(f"Periodo: {period_label}"))
        report_lines.append("-" * printer.WIDTH)
        report_lines.append(printer.format_line("EFECTIVO (EF):", f"${summary['total_efectivo']}"))
        report_lines.append(printer.format_line("ONLINE (ONL):", f"${summary['total_online']}"))
        report_lines.append("-" * printer.WIDTH)
        report_lines.append(printer.format_line("TOTAL GENERAL:", f"${summary['total_general']}"))
        report_lines.append("-" * printer.WIDTH)
        report_lines.append("\n" + printer.center_text("Listado de Ventas Online:"))

        if summary['online_orders']:
            report_lines.append(f"{'ID':<5} {'Cliente':<25} {'Monto'}")
            for o in summary['online_orders']:
                report_lines.append(f"{o.id:<5} {o.customer[:25]:<25} ${o.total}")
        else:
            report_lines.append("No hay ventas online.")

        report_text = "\n".join(report_lines)
        filename = f"reporte_fiscal_{period_label.replace(' ', '_').replace('(', '').replace(')', '')}.txt"

        original_mode = printer.OUTPUT_MODE
        if printer.OUTPUT_MODE != 'POS80':
            printer.OUTPUT_MODE = 'PDF'

        printer.process_output(filename, report_text, report_text)
        printer.OUTPUT_MODE = original_mode
