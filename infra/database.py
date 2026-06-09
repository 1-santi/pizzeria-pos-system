"""
Capa de acceso a datos - SQLite.
Reemplaza el antiguo store.py + data.json con una base de datos relacional.
Soporta transacciones ACID y acceso concurrente.
"""
import sqlite3
import datetime
from typing import List, Optional

from config import DATABASE_FILE
from domain.models import Product, Order, OrderItem, Category, Zone


class Database:
    """Gestiona toda la persistencia del sistema usando SQLite."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_FILE
        self._create_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Crea las tablas si no existen. Se ejecuta al iniciar el sistema."""
        conn = self._get_connection()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS zones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    category TEXT NOT NULL DEFAULT 'Pizza',
                    FOREIGN KEY (category) REFERENCES categories(name) ON UPDATE CASCADE
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    customer TEXT NOT NULL,
                    phone TEXT DEFAULT '',
                    address TEXT DEFAULT '',
                    observation TEXT DEFAULT '',
                    delivery_type TEXT NOT NULL,
                    delivery_fee INTEGER DEFAULT 0,
                    cadete TEXT DEFAULT '',
                    payment_method TEXT DEFAULT 'Efectivo',
                    total INTEGER NOT NULL,
                    zone_id INTEGER,
                    zone_name TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id)
                );

                CREATE TABLE IF NOT EXISTS cadetes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                );

                CREATE INDEX IF NOT EXISTS idx_orders_zone ON orders(zone_id);
            """)

            # Migración segura: agregar columnas zone_id y zone_name a orders si no existen
            # (para bases de datos creadas antes de esta versión)
            try:
                conn.execute("ALTER TABLE orders ADD COLUMN zone_id INTEGER")
            except sqlite3.OperationalError:
                pass  # columna ya existe
            try:
                conn.execute("ALTER TABLE orders ADD COLUMN zone_name TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass  # columna ya existe
            
            # Seed default categories if empty
            cursor = conn.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] == 0:
                defaults = {"Pizza", "Empanadas", "Papas"}
                
                # Also collect any existing categories from products table to avoid foreign key issues
                try:
                    cursor = conn.execute("SELECT DISTINCT category FROM products")
                    for row in cursor.fetchall():
                        if row["category"]:
                            defaults.add(row["category"])
                except sqlite3.OperationalError:
                    pass
                
                conn.executemany(
                    "INSERT INTO categories (name) VALUES (?)",
                    [(c,) for c in sorted(defaults)]
                )

            # Seed default zones if empty
            cursor = conn.execute("SELECT COUNT(*) FROM zones")
            if cursor.fetchone()[0] == 0:
                default_zones = [
                    ("Zona 1", ""),
                    ("Zona 2", ""),
                    ("Zona 3", ""),
                ]
                conn.executemany(
                    "INSERT INTO zones (name, description) VALUES (?, ?)",
                    default_zones
                )
            
            conn.commit()
        finally:
            conn.close()

    # =========================================================
    # PRODUCTOS
    # =========================================================

    def get_menu(self) -> List[Product]:
        """Retorna todos los productos ordenados por categoría y nombre."""
        conn = self._get_connection()
        try:
            rows = conn.execute(
                "SELECT id, name, price, category FROM products ORDER BY category, name"
            ).fetchall()
            return [
                Product(id=r["id"], name=r["name"], price=r["price"], category=r["category"])
                for r in rows
            ]
        finally:
            conn.close()

    def add_product(self, product: Product) -> int:
        """Agrega un producto al menú. Retorna el ID generado."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
                (product.name, product.price, product.category),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def update_product(self, product_id: int, name: str, price: int, category: str = None) -> bool:
        """Actualiza nombre, precio y opcionalmente categoría de un producto."""
        conn = self._get_connection()
        try:
            if category:
                conn.execute(
                    "UPDATE products SET name=?, price=?, category=? WHERE id=?",
                    (name, price, category, product_id),
                )
            else:
                conn.execute(
                    "UPDATE products SET name=?, price=? WHERE id=?",
                    (name, price, product_id),
                )
            conn.commit()
            return True
        finally:
            conn.close()

    def remove_product(self, product_id: int) -> bool:
        """Elimina un producto por ID."""
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM products WHERE id=?", (product_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    # =========================================================
    # PEDIDOS
    # =========================================================

    def add_order(self, order: Order) -> int:
        """Inserta un pedido con sus ítems de forma atómica (transacción)."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """INSERT INTO orders 
                   (date, customer, phone, address, observation,
                    delivery_type, delivery_fee, cadete, payment_method, total,
                    zone_id, zone_name)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    order.date, order.customer, order.phone, order.address,
                    order.observation, order.delivery_type, order.delivery_fee,
                    order.cadete, order.payment_method, order.total,
                    order.zone_id, order.zone_name,
                ),
            )
            order_id = cursor.lastrowid

            for item in order.items:
                conn.execute(
                    "INSERT INTO order_items (order_id, name, price) VALUES (?, ?, ?)",
                    (order_id, item.name, item.price),
                )

            conn.commit()
            return order_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_orders(
        self,
        date_filter: str = None,
        cadete_filter: str = None,
        payment_filter: str = None,
        zone_filter: int = None,
    ) -> List[Order]:
        """Retorna pedidos con filtros opcionales."""
        conn = self._get_connection()
        try:
            query = "SELECT * FROM orders WHERE 1=1"
            params = []

            if date_filter:
                query += " AND date LIKE ?"
                params.append(f"{date_filter}%")
            if cadete_filter:
                query += " AND cadete = ?"
                params.append(cadete_filter)
            if payment_filter:
                query += " AND payment_method = ?"
                params.append(payment_filter)
            if zone_filter is not None:
                query += " AND zone_id = ?"
                params.append(zone_filter)

            query += " ORDER BY id"
            rows = conn.execute(query, params).fetchall()

            orders = []
            for r in rows:
                items_rows = conn.execute(
                    "SELECT name, price FROM order_items WHERE order_id=?",
                    (r["id"],),
                ).fetchall()
                items = [OrderItem(name=ir["name"], price=ir["price"]) for ir in items_rows]

                orders.append(
                    Order(
                        id=r["id"], date=r["date"], customer=r["customer"],
                        phone=r["phone"], address=r["address"],
                        observation=r["observation"], delivery_type=r["delivery_type"],
                        delivery_fee=r["delivery_fee"], cadete=r["cadete"],
                        payment_method=r["payment_method"], items=items,
                        total=r["total"],
                        zone_id=r["zone_id"], zone_name=r["zone_name"] or "",
                    )
                )

            return orders
        finally:
            conn.close()

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Retorna un pedido específico por ID, o None si no existe."""
        conn = self._get_connection()
        try:
            r = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
            if not r:
                return None

            items_rows = conn.execute(
                "SELECT name, price FROM order_items WHERE order_id=?",
                (r["id"],),
            ).fetchall()
            items = [OrderItem(name=ir["name"], price=ir["price"]) for ir in items_rows]

            return Order(
                id=r["id"], date=r["date"], customer=r["customer"],
                phone=r["phone"], address=r["address"],
                observation=r["observation"], delivery_type=r["delivery_type"],
                delivery_fee=r["delivery_fee"], cadete=r["cadete"],
                payment_method=r["payment_method"], items=items,
                total=r["total"],
                zone_id=r["zone_id"], zone_name=r["zone_name"] or "",
            )
        finally:
            conn.close()

    # =========================================================
    # CADETES
    # =========================================================

    def get_cadetes(self) -> List[str]:
        """Retorna la lista de nombres de cadetes activos."""
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT name FROM cadetes ORDER BY name").fetchall()
            return [r["name"] for r in rows]
        finally:
            conn.close()

    def add_cadete(self, name: str) -> bool:
        """Agrega un cadete. Retorna False si ya existe."""
        conn = self._get_connection()
        try:
            conn.execute("INSERT INTO cadetes (name) VALUES (?)", (name,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def remove_cadete(self, name: str) -> bool:
        """Elimina un cadete por nombre."""
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM cadetes WHERE name=?", (name,))
            conn.commit()
            return True
        finally:
            conn.close()

    # =========================================================
    # CATEGORIAS
    # =========================================================

    def get_categories(self) -> List[Category]:
        """Retorna la lista de categorías registradas en el sistema."""
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
            return [Category(id=r["id"], name=r["name"]) for r in rows]
        finally:
            conn.close()

    def add_category(self, name: str) -> bool:
        """Agrega una categoría. Retorna False si ya existe."""
        conn = self._get_connection()
        try:
            conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()


    def update_category(self, category_id: int, new_name: str) -> bool:
        """Actualiza el nombre de una categoría y todos los productos asociados."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            # Primero, obtener el nombre anterior de la categoría
            row = conn.execute("SELECT name FROM categories WHERE id = ?", (category_id,)).fetchone()
            if not row:
                return False
            old_name = row["name"]

            # Actualizar en base de datos. Usamos una transacción explícita sin foreign_keys para
            # evitar conflictos durante el cambio manual cruzado.
            conn.execute("BEGIN TRANSACTION")
            conn.execute("UPDATE products SET category = ? WHERE category = ?", (new_name, old_name))
            conn.execute("UPDATE categories SET name = ? WHERE id = ?", (new_name, category_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            conn.rollback()
            return False
        finally:
            conn.close()

    def remove_category(self, category_id: int) -> bool:
        """Elimina una categoría por su ID."""
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def category_has_products(self, category_name: str) -> bool:
        """Verifica si una categoría tiene productos asociados."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM products WHERE category = ?", (category_name,))
            return cursor.fetchone()[0] > 0
        finally:
            conn.close()

    # =========================================================
    # ZONAS DE REPARTO
    # =========================================================

    def get_zones(self) -> List[Zone]:
        """Retorna la lista de zonas de reparto."""
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT id, name, description FROM zones ORDER BY name").fetchall()
            return [Zone(id=r["id"], name=r["name"], description=r["description"] or "") for r in rows]
        finally:
            conn.close()

    def add_zone(self, name: str, description: str = "") -> bool:
        """Agrega una zona. Retorna False si ya existe."""
        conn = self._get_connection()
        try:
            conn.execute("INSERT INTO zones (name, description) VALUES (?, ?)", (name, description))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def update_zone(self, zone_id: int, name: str, description: str) -> bool:
        """Actualiza nombre y descripción de una zona."""
        conn = self._get_connection()
        try:
            conn.execute(
                "UPDATE zones SET name = ?, description = ? WHERE id = ?",
                (name, description, zone_id),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def remove_zone(self, zone_id: int) -> bool:
        """Elimina una zona por su ID."""
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM zones WHERE id = ?", (zone_id,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def zone_has_orders(self, zone_id: int) -> bool:
        """Verifica si una zona tiene pedidos asociados."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM orders WHERE zone_id = ?", (zone_id,))
            return cursor.fetchone()[0] > 0
        finally:
            conn.close()

