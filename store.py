import json
import os
import shutil
import datetime

DATA_FILE = 'data.json'
BACKUP_DIR = 'backups'

class Store:
    def __init__(self):
        self.data_file = DATA_FILE
        self.backup_dir = BACKUP_DIR
        self.ensure_backup_dir()
        self.backup_data()
        self.data = self.load_data()

    def ensure_backup_dir(self):
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def backup_data(self):
        if not os.path.exists(self.data_file):
            return
        
        today = datetime.date.today()
        backup_filename = f"data_{today}.json"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        # Only backup if not already exists for today to save minimal IO/space
        # although overwriting is safer if app crashed? Let's keep it simple: overwrite or skip.
        # Let's simple copy.
        try:
            shutil.copy2(self.data_file, backup_path)
        except Exception as e:
            print(f"Advertencia: No se pudo crear respaldo: {e}")

    def load_data(self):
        if not os.path.exists(self.data_file):
            return {"menu": [], "orders": [], "cadetes": []}
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "cadetes" not in data:
                    data["cadetes"] = []
                return data
        except json.JSONDecodeError:
             return {"menu": [], "orders": [], "cadetes": []}

    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def get_menu(self):
        return self.data.get("menu", [])

    def add_order(self, customer_name, order_details, total_price, phone="", address="", observation="", delivery_type="", delivery_fee=0, cadete_name="", payment_method="Efectivo"):
        # order_details is list of item names or dicts.
        
        # We need a timestamp? Let's add it for history view
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        order = {
            "id": len(self.data.get("orders", [])) + 1,
            "date": timestamp,
            "customer": customer_name,
            "phone": phone,
            "address": address,
            "observation": observation,
            "delivery_type": delivery_type,
            "delivery_fee": delivery_fee,
            "cadete": cadete_name,
            "payment_method": payment_method,
            "items": order_details,
            "total": total_price
        }
        self.data["orders"].append(order)
        self.save_data()
        return order["id"]
        
    def get_orders(self):
        return self.data.get("orders", [])

    def add_product(self, name, price, category="Pizza"):
        # Check if exists to avoid duplicates? For now just append as requested allow simple add
        new_pizza = {"name": name, "price": price, "category": category}
        self.data["menu"].append(new_pizza)
        self.save_data()

    def update_product(self, old_name, new_name, new_price, new_category=None):
        for pizza in self.data["menu"]:
            if pizza["name"] == old_name:
                pizza["name"] = new_name
                pizza["price"] = new_price
                if new_category is not None:
                    pizza["category"] = new_category
                self.save_data()
                return True
        return False

    def remove_product(self, name):
         self.data["menu"] = [p for p in self.data["menu"] if p["name"] != name]
         self.save_data()

    def get_cadetes(self):
        return self.data.get("cadetes", [])

    def add_cadete(self, name):
        if name not in self.data["cadetes"]:
            self.data["cadetes"].append(name)
            self.save_data()
            return True
        return False

    def remove_cadete(self, name):
        if name in self.data["cadetes"]:
            self.data["cadetes"].remove(name)
            self.save_data()
            return True
        return False
