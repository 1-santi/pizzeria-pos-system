# 📋 INSTRUCCIONES DE INSTALACIÓN — LPM PIZZAS v2.0

> Guía rápida para instalar el sistema en una computadora nueva.
> Para la documentación completa, ver el archivo [README.md](README.md).

---

## 1. 💻 Sistema Operativo

- **Windows 10 o 11** (obligatorio)

## 2. 🐍 Python (Lenguaje de Programación)

- **Versión**: Python 3.7 o superior
- **Descarga**: [https://python.org/downloads](https://python.org/downloads)
- ⚠️ **MUY IMPORTANTE**: Al instalar, **marcá la casilla "Add python.exe to PATH"** (está abajo de todo en el instalador)

## 3. 🖨️ Configuración de Impresora (Crítico para impresión real)

La impresora térmica de 80mm debe estar **compartida en Windows** con el nombre exacto:

```
Nombre del recurso compartido: POS80
```

### Pasos:
1. Abrí **Configuración → Dispositivos → Impresoras**
2. Clic derecho en tu impresora térmica → **Propiedades de la impresora**
3. Pestaña **"Compartir"** → Marcar **"Compartir esta impresora"**
4. Escribir en "Nombre del recurso": **`POS80`** (exacto, en mayúsculas)
5. Aceptar

> El sistema envía la impresión a `\\127.0.0.1\POS80` usando modo RAW (`copy /b`). Esto garantiza que los tickets usen todo el ancho del papel, las letras de la comanda salgan en tamaño grande y la guillotina corte automáticamente.

## 4. ⚙️ Configuración del Modo de Impresión

Abrí el archivo **`config.py`** con el Bloc de notas y cambiá la línea:

```python
# En el local con impresora conectada:
OUTPUT_MODE = 'POS80'

# Para probar sin impresora (genera PDF):
OUTPUT_MODE = 'PDF'

# Para desarrollo (solo muestra en pantalla):
OUTPUT_MODE = 'DEBUG'
```

---

## 5. 🚀 CÓMO EJECUTAR EL SISTEMA

1. Copiá la carpeta completa `proyecto de la pizzeria` a la nueva PC
2. Configurá el modo de impresión en `config.py` (ver punto 4)
3. Hacé **doble clic en `run_pizzeria.bat`**

---

## 📁 Estructura del Proyecto (v2.0 — Arquitectura por Capas)

```
proyecto de la pizzeria/
├── main.py                    # Punto de entrada
├── config.py                  # Configuración (¡EDITAR OUTPUT_MODE ACÁ!)
├── domain/                    # Modelos de datos
│   ├── models.py              # Product, OrderItem, Order
│   └── pricing.py             # Reglas de precios
├── services/                  # Lógica de negocio
│   ├── order_service.py       # Gestión de pedidos
│   ├── product_service.py     # CRUD de productos
│   ├── cadete_service.py      # CRUD de cadetes
│   ├── report_service.py      # Liquidación y reportes
│   └── export_service.py      # Exportación a CSV
├── ui/                        # Interfaz de consola
│   ├── menus.py               # Menús y navegación
│   ├── input_helpers.py       # Parseo de entrada
│   └── display.py             # Formateo visual
├── infra/                     # Infraestructura
│   ├── database.py            # SQLite (pizzeria.db)
│   └── printer.py             # Impresión ESC/POS
├── pizzeria.db                # Base de datos (se crea sola)
├── run_pizzeria.bat           # Iniciar el sistema
└── README.md                  # Documentación completa
```

---

## ✨ Funcionalidades Principales

| Función | Descripción |
|---------|-------------|
| 📝 Tomar Pedido | Búsqueda inteligente, soporte "2 x muzza", mitad y mitad |
| 🖨️ Impresión Doble | Comanda Cocina (grande) + Ticket Control (detalle) |
| 🛵 Cadetes | Liquidación diaria: $10.000 base + comisiones de envío |
| 💰 Medios de Pago | Efectivo vs Online — Separado para ARCA |
| 📈 Reporte Fiscal | Por día, mes o total — Listo para facturar |
| 📂 Exportar Excel | CSV con separador `;` compatible con Excel en español |
| 🗃️ Base de Datos | SQLite (`pizzeria.db`) — No se pierde nada |

---

*Si el texto del ticket sale chico o con márgenes, verificá que la impresora esté compartida exactamente como **POS80**.*

*Para más detalles, consultá el [README.md](README.md) completo.*
