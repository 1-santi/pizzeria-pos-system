"""
LPM PIZZAS - Sistema de Gestión
================================
Punto de entrada principal del sistema.
Inicializa la base de datos, crea los servicios e inicia la interfaz.
"""
from infra.database import Database
from services.order_service import OrderService
from services.product_service import ProductService
from services.cadete_service import CadeteService
from services.report_service import ReportService
from services.export_service import ExportService
from services.category_service import CategoryService
from services.zone_service import ZoneService
from ui.menus import main_menu


def main():
    # Inicializar base de datos SQLite (se crea automáticamente si no existe)
    db = Database()

    # Crear servicios con inyección de dependencias
    order_svc = OrderService(db)
    product_svc = ProductService(db)
    cadete_svc = CadeteService(db)
    report_svc = ReportService(db)
    export_svc = ExportService(db)
    category_svc = CategoryService(db)
    zone_svc = ZoneService(db)

    # Iniciar interfaz de consola
    main_menu(order_svc, product_svc, cadete_svc, report_svc, export_svc, category_svc, zone_svc)


if __name__ == "__main__":
    main()

