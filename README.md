<p align="center">
  <img src="logo_pizza.png" alt="LPM Pizzas Logo" width="180"/>
</p>

<h1 align="center">🍕 LPM Pizzas — Sistema de Gestión</h1>

<p align="center">
  <strong>Sistema integral de gestión para pizzerías · Pedidos · Impresión · Reportes fiscales</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.7+"/>
  <img src="https://img.shields.io/badge/SQLite-Base_de_datos-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"/>
  <img src="https://img.shields.io/badge/Licencia-Uso_Privado-red?style=for-the-badge" alt="Licencia"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Impresora-Térmica_80mm-FF6B00?style=flat-square" alt="Impresora"/>
  <img src="https://img.shields.io/badge/Versión-2.0-brightgreen?style=flat-square" alt="Versión"/>
  <img src="https://img.shields.io/badge/Arquitectura-Capas_(Layered)-blueviolet?style=flat-square" alt="Arquitectura"/>
</p>

---

## 📋 Tabla de Contenidos

- [📖 Descripción](#-descripción)
- [✨ Funcionalidades](#-funcionalidades)
- [⚙️ Requisitos del Sistema](#️-requisitos-del-sistema)
- [📥 Instalación en una PC Nueva](#-instalación-en-una-pc-nueva)
- [🚀 Cómo Ejecutar el Sistema](#-cómo-ejecutar-el-sistema)
- [🏗️ Arquitectura del Proyecto](#️-arquitectura-del-proyecto)
- [🗃️ Estructura de la Base de Datos](#️-estructura-de-la-base-de-datos)
- [🖨️ Configuración de la Impresora](#️-configuración-de-la-impresora)
- [⚡ Configuración del Sistema (config.py)](#-configuración-del-sistema-configpy)
- [📖 Guía de Uso Rápido](#-guía-de-uso-rápido)
- [❓ FAQ / Solución de Problemas](#-faq--solución-de-problemas)

---

## 📖 Descripción

**LPM Pizzas** es un sistema de gestión completo diseñado para la operación diaria de una pizzería. Funciona desde la **consola de Windows** (ventana negra) y permite:

- 📝 Tomar pedidos de forma rápida y ágil
- 🖨️ Imprimir comandas de cocina y tickets de control automáticamente
- 🛵 Gestionar cadetes (repartidores) y sus liquidaciones diarias
- 💰 Generar reportes fiscales para **ARCA** (ex AFIP)
- 📊 Exportar datos a Excel (CSV)

> **📍 Dirección del negocio:** M.David 4304

El sistema está pensado para ser **simple de usar** — no necesitás ser programador. Solo hacés doble clic en `run_pizzeria.bat` y listo.

---

## ✨ Funcionalidades

| Módulo | Descripción |
|--------|-------------|
| 🍕 **Menú de Productos** | Gestión de Pizzas, Papas y Empanadas con categorías y precios |
| 📝 **Toma de Pedidos** | Búsqueda inteligente de productos (por nombre o número), soporte para `2 x muzza`, pizzas mitad y mitad |
| 🛵 **Cadetes** | Alta/baja de repartidores, asignación a pedidos con envío |
| 💵 **Medios de Pago** | Registro de Efectivo (EF) y Online (ONL) por separado |
| 🖨️ **Impresión Doble** | **Comanda Cocina** (letras grandes) + **Ticket Control** (detalle completo) con corte automático |
| 📊 **Liquidación Diaria** | Cálculo automático: $10.000 base + comisiones de envío por cadete |
| 📈 **Reporte Fiscal** | Resumen de ventas por medio de pago (Efectivo vs Online) — Listo para ARCA |
| 📂 **Exportar a Excel** | Genera archivos `.csv` compatibles con Excel en español (separador `;`, encoding `utf-8-sig`) |
| 🔁 **Historial** | Búsqueda por cliente, cadete, medio de pago o ID — Reimpresión de tickets |
| 🎯 **Pizza Mitad y Mitad** | Selección de dos sabores, cobra el precio del más caro |

---

## ⚙️ Requisitos del Sistema

| Requisito | Detalle |
|-----------|---------|
| 💻 **Sistema Operativo** | Windows 10 o Windows 11 |
| 🐍 **Python** | Versión 3.7 o superior |
| 🖨️ **Impresora** | Térmica de 80mm (POS80) — *Opcional para desarrollo* |
| 💾 **Espacio en disco** | Menos de 10 MB |
| 🌐 **Internet** | NO necesario (funciona 100% offline) |

> **📌 Nota:** El sistema no requiere instalar ninguna librería adicional de Python. Usa solo módulos incluidos con Python (sqlite3, csv, datetime, etc.).

---

## 📥 Instalación en una PC Nueva

### Paso 1: Descargar Python 🐍

1. Abrí el navegador y entrá a: **[https://www.python.org/downloads/](https://www.python.org/downloads/)**
2. Hacé clic en el botón amarillo grande que dice **"Download Python 3.x.x"**
3. Se va a descargar un archivo como `python-3.x.x-amd64.exe`

### Paso 2: Instalar Python ⚠️ MUY IMPORTANTE

Al abrir el instalador, vas a ver esta pantalla:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│           Install Python 3.x.x (64-bit)            │
│                                                     │
│  ☑  Install launcher for all users (recommended)    │
│  ☑  Add python.exe to PATH   ◄── ¡¡MARCAR ESTO!!   │
│                                                     │
│  ┌─────────────────────┐  ┌──────────────────────┐  │
│  │   Install Now       │  │  Customize install   │  │
│  └─────────────────────┘  └──────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

> ⚠️ **CRÍTICO:** Antes de hacer clic en "Install Now", **marcá la casilla que dice "Add python.exe to PATH"** (está abajo de todo). Si no la marcás, el sistema NO va a funcionar.

4. Hacé clic en **"Install Now"** y esperá a que termine
5. Cuando diga **"Setup was successful"**, cerrá el instalador

### Paso 3: Verificar que Python se instaló bien ✅

1. Abrí el menú de inicio de Windows
2. Escribí `cmd` y abrí **"Símbolo del sistema"**
3. Escribí el siguiente comando y presioná Enter:

```
python --version
```

```
┌──────────────────────────────────────────┐
│ C:\Users\TuNombre> python --version      │
│ Python 3.12.4                            │  ◄── Si ves esto, ¡funciona!
│                                          │
│ C:\Users\TuNombre>                       │
└──────────────────────────────────────────┘
```

> Si dice `"python" no se reconoce como un comando...` significa que no marcaste la casilla de PATH. Desinstalá Python y volvé a instalarlo marcando la casilla.

### Paso 4: Copiar los archivos del sistema 📂

1. Copiá **toda la carpeta** del proyecto a la nueva PC (por ejemplo al Escritorio)
2. La carpeta se llama `proyecto de la pizzeria` y contiene todos los archivos necesarios
3. **No muevas ni renombres** los archivos de adentro

### Paso 5: Configurar la impresora 🖨️

Seguí las instrucciones de la sección [Configuración de la Impresora](#️-configuración-de-la-impresora) más abajo.

---

## 🚀 Cómo Ejecutar el Sistema

### Forma rápida (recomendada):
Hacé **doble clic** en el archivo:

```
📁 proyecto de la pizzeria/
  └── 🟢 run_pizzeria.bat   ◄── Doble clic acá
```

### Forma manual (desde terminal):
```bash
cd "C:\Users\TuNombre\Desktop\proyecto de la pizzeria"
python main.py
```

Al iniciar vas a ver:

```
     __                      ____  _
    / /   ____  ____ ___    / __ \(_)____________________
   / /   / __ \/ __ `__ \  / /_/ / /_  /_  / / __ `/ ___/
  / /___/ /_/ / / / / / / / ____/ / / /_/ /_/ /_/ (__  )
 /_____/ .___/_/ /_/ /_/ /_/   /_/ /___/___/\__,_/____/
      /_/

--------------------------------------------------
         SISTEMA DE GESTION LPM PIZZAS
--------------------------------------------------
1. Ver Menu
2. Tomar Pedido
3. Administrar
4. Salir

Seleccione una opcion ([2]):
```

> 💡 **Tip:** El sistema arranca por defecto en "Tomar Pedido" (opción 2). Si presionás Enter directo, va a la toma de pedidos.

---

## 🏗️ Arquitectura del Proyecto

El proyecto utiliza una **Arquitectura por Capas** (Layered Architecture) que separa las responsabilidades en módulos independientes:

```mermaid
graph TB
    subgraph "🖥️ Capa de Presentación (UI)"
        A[menus.py<br/>Navegación] --> B[input_helpers.py<br/>Parseo y Búsqueda]
        A --> C[display.py<br/>Header y Tablas]
    end

    subgraph "⚙️ Capa de Servicios (Lógica de Negocio)"
        D[order_service.py<br/>Pedidos]
        E[product_service.py<br/>CRUD Productos]
        F[cadete_service.py<br/>CRUD Cadetes]
        G[report_service.py<br/>Liquidación y Fiscal]
        H[export_service.py<br/>CSV / Excel]
    end

    subgraph "🏛️ Capa de Dominio"
        I[models.py<br/>Product, OrderItem, Order]
        J[pricing.py<br/>Reglas de Precios]
    end

    subgraph "🔧 Capa de Infraestructura"
        K[database.py<br/>SQLite]
        L[printer.py<br/>ESC/POS]
    end

    A --> D
    A --> E
    A --> F
    A --> G
    A --> H
    D --> I
    D --> J
    D --> K
    D --> L
    E --> K
    F --> K
    G --> K
    H --> K

    M[main.py<br/>Punto de entrada] --> A
    N[config.py<br/>Configuración] -.-> D
    N -.-> K
    N -.-> L

    style M fill:#4CAF50,color:white
    style N fill:#FF9800,color:white
```

### 📁 Estructura de Archivos

```
proyecto de la pizzeria/
│
├── 🟢 main.py                    # Punto de entrada del sistema (~30 líneas)
├── ⚙️ config.py                   # Configuración centralizada (impresora, constantes)
│
├── 📦 domain/                     # Capa de Dominio (modelos de datos)
│   ├── __init__.py
│   ├── models.py                  # Dataclasses: Product, OrderItem, Order
│   └── pricing.py                 # Reglas de precios (mitad y mitad, etc.)
│
├── 🔧 services/                   # Capa de Servicios (lógica de negocio)
│   ├── __init__.py
│   ├── order_service.py           # Crear pedidos, buscar, filtrar
│   ├── product_service.py         # Alta, baja y modificación de productos
│   ├── cadete_service.py          # Alta, baja de cadetes (repartidores)
│   ├── report_service.py          # Liquidación diaria y reportes fiscales
│   └── export_service.py          # Exportación a CSV (Excel)
│
├── 🖥️ ui/                         # Capa de Presentación (interfaz de consola)
│   ├── __init__.py
│   ├── menus.py                   # Navegación del menú principal y submenús
│   ├── input_helpers.py           # Parseo de entrada (ej: "2 x muzza")
│   └── display.py                 # Header ASCII, formateo de tablas
│
├── 🗄️ infra/                      # Capa de Infraestructura
│   ├── __init__.py
│   ├── database.py                # Conexión y queries a SQLite
│   └── printer.py                 # Impresión ESC/POS (térmica 80mm) y PDF
│
├── 🗃️ pizzeria.db                 # Base de datos SQLite (se crea automáticamente)
├── 🖼️ logo_pizza.png              # Logo del negocio
├── 🟢 run_pizzeria.bat            # Script para iniciar con doble clic
└── 📄 README.md                   # Esta documentación
```

### 🔄 Flujo de un Pedido

```mermaid
sequenceDiagram
    actor Usuario as 👤 Operador
    participant UI as 🖥️ UI (menus.py)
    participant OS as ⚙️ OrderService
    participant DB as 🗄️ SQLite
    participant PR as 🖨️ Printer

    Usuario->>UI: Selecciona "Tomar Pedido"
    UI->>Usuario: Pide nombre, teléfono, dirección
    UI->>Usuario: Pide productos (búsqueda inteligente)
    UI->>Usuario: Selección de cadete y medio de pago
    UI->>OS: Crea el pedido con todos los datos
    OS->>DB: INSERT en orders + order_items
    DB-->>OS: Retorna ID del pedido
    OS->>PR: Envía datos para impresión
    PR->>PR: Genera Comanda Cocina (letras grandes)
    PR->>PR: Genera Ticket Control (detalle)
    PR-->>Usuario: 🖨️ Se imprimen ambos tickets
    OS-->>UI: Confirma pedido creado
    UI-->>Usuario: Muestra resumen en pantalla
```

---

## 🗃️ Estructura de la Base de Datos

El sistema utiliza **SQLite** como base de datos. El archivo `pizzeria.db` se crea automáticamente al iniciar por primera vez.

### Tabla `products` — Productos del menú

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | INTEGER (PK) | Identificador único, autoincremental |
| `name` | TEXT NOT NULL | Nombre del producto (máx. 30 caracteres) |
| `price` | INTEGER NOT NULL | Precio en pesos (sin decimales) |
| `category` | TEXT DEFAULT 'Pizza' | Categoría: `Pizza`, `Papas` o `Empanadas` |

### Tabla `orders` — Pedidos

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | INTEGER (PK) | Número de pedido, autoincremental |
| `date` | TEXT NOT NULL | Fecha y hora (`YYYY-MM-DD HH:MM:SS`) |
| `customer` | TEXT NOT NULL | Nombre del cliente |
| `phone` | TEXT | Teléfono del cliente |
| `address` | TEXT | Dirección de entrega |
| `observation` | TEXT | Observaciones (ej: "sin cebolla") |
| `delivery_type` | TEXT NOT NULL | `Envío` o `Take Away` |
| `delivery_fee` | INTEGER DEFAULT 0 | Costo del envío en pesos |
| `cadete` | TEXT | Nombre del cadete asignado |
| `payment_method` | TEXT DEFAULT 'Efectivo' | `Efectivo` o `Online` |
| `total` | INTEGER NOT NULL | Total cobrado (productos + envío) |

### Tabla `order_items` — Detalle de cada pedido

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | INTEGER (PK) | Identificador único |
| `order_id` | INTEGER (FK) | Referencia a `orders.id` |
| `product_name` | TEXT NOT NULL | Nombre del producto al momento de la venta |
| `price` | INTEGER NOT NULL | Precio unitario al momento de la venta |
| `quantity` | INTEGER DEFAULT 1 | Cantidad de unidades |

### Tabla `cadetes` — Repartidores

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | INTEGER (PK) | Identificador único |
| `name` | TEXT NOT NULL UNIQUE | Nombre del cadete |

### Diagrama de relaciones

```mermaid
erDiagram
    PRODUCTS {
        int id PK
        text name
        int price
        text category
    }

    ORDERS {
        int id PK
        text date
        text customer
        text phone
        text address
        text observation
        text delivery_type
        int delivery_fee
        text cadete
        text payment_method
        int total
    }

    ORDER_ITEMS {
        int id PK
        int order_id FK
        text product_name
        int price
        int quantity
    }

    CADETES {
        int id PK
        text name
    }

    ORDERS ||--o{ ORDER_ITEMS : "contiene"
    CADETES ||--o{ ORDERS : "reparte"
```

---

## 🖨️ Configuración de la Impresora

### ¿Qué impresora necesito?

El sistema está diseñado para impresoras térmicas de **80mm** (como las de un comercio o restaurante). El modelo recomendado es cualquiera compatible con comandos **ESC/POS**.

### Paso a paso para configurar la impresora ⚠️ CRÍTICO

#### 1. Instalar la impresora en Windows

Conectá la impresora por USB e instalá los drivers que vienen con ella. Windows debería reconocerla automáticamente.

#### 2. Compartir la impresora como "POS80"

Este paso es **obligatorio** para que el sistema pueda imprimir:

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  1. Abrí  Configuración → Dispositivos → Impresoras    │
│                                                         │
│  2. Buscá tu impresora térmica en la lista              │
│                                                         │
│  3. Clic derecho → "Propiedades de la impresora"        │
│                                                         │
│  4. Pestaña "Compartir"                                 │
│     ☑ Compartir esta impresora                          │
│     Nombre del recurso: [ POS80 ]  ◄── EXACTO así      │
│                                                         │
│  5. Clic en "Aceptar"                                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

> ⚠️ **El nombre DEBE ser exactamente `POS80`** (en mayúsculas, sin espacios). El sistema envía la impresión al recurso compartido `\\127.0.0.1\POS80`.

#### 3. Verificar que funciona

Abrí una ventana de **cmd** (Símbolo del sistema) y escribí:

```
echo Prueba de impresion > test.txt
copy /b test.txt "\\127.0.0.1\POS80"
```

Si la impresora imprime "Prueba de impresion", ¡está todo listo! 🎉

---

## ⚡ Configuración del Sistema (`config.py`)

El archivo `config.py` contiene todas las configuraciones centralizadas del sistema. Los ajustes más importantes son:

### 🖨️ Modo de Impresión (`OUTPUT_MODE`)

Este es el ajuste **más importante** que vas a tener que cambiar:

```python
# =====================================================
# CONFIGURACION DE SALIDA DE IMPRESIÓN
# =====================================================
# Opciones:
#   'POS80'  → Impresora térmica real (para el local)
#   'PDF'    → Abre ventana de Windows para guardar PDF
#   'DEBUG'  → Solo muestra en la pantalla negra (para probar)
# =====================================================
OUTPUT_MODE = 'PDF'     # ◄── Cambiá esto según tu necesidad
```

| Modo | ¿Cuándo usarlo? | ¿Qué hace? |
|------|-----------------|------------|
| `'POS80'` | **En el local** con la impresora conectada | Envía directo a la impresora térmica, con corte automático de papel |
| `'PDF'` | Para **probar** sin impresora | Abre la ventana de Windows para guardar como PDF |
| `'DEBUG'` | Para **desarrollo** | Solo muestra una vista previa en la consola (no genera archivos) |

#### ¿Cómo cambiar el modo?

1. Abrí el archivo `config.py` con el **Bloc de notas** (clic derecho → Abrir con → Bloc de notas)
2. Buscá la línea que dice `OUTPUT_MODE = 'PDF'`
3. Cambiá `'PDF'` por `'POS80'` (con comillas simples)
4. Guardá el archivo (Ctrl + S)
5. Reiniciá el sistema (cerrá y volvé a abrir `run_pizzeria.bat`)

```python
# ANTES (modo prueba):
OUTPUT_MODE = 'PDF'

# DESPUÉS (modo producción con impresora):
OUTPUT_MODE = 'POS80'
```

### 💰 Configuración de Cadetes

```python
# Pago base diario por cadete (en pesos)
CADETE_BASE_PAY = 10000
```

### 🖨️ Ancho de Impresión

```python
# Ancho de ticket en caracteres (80mm = 48 chars)
PRINTER_WIDTH = 48
```

### 📍 Datos del Negocio

```python
BUSINESS_NAME = "LPM PIZZAS"
BUSINESS_ADDRESS = "M.David 4304"
```

---

## 📖 Guía de Uso Rápido

### 🍕 Tomar un Pedido (el flujo más importante)

```
1. Abrí el sistema (doble clic en run_pizzeria.bat)
2. Presioná Enter (va directo a "Tomar Pedido")
3. Escribí el nombre del cliente
4. Escribí teléfono y dirección (opcionales)
5. Elegí tipo de entrega: 1=Envío, 2=Take Away
6. Si es envío, ingresá el costo del envío
```

**Agregar productos al pedido:**
```
Producto: muzza          → Busca y agrega 1 muzzarella
Producto: 2 x napo       → Agrega 2 napolitanas
Producto: 3x fugazzeta   → Agrega 3 fugazzetas
Producto: 5              → Agrega el producto #5 del menú
Producto: mitad           → Activa el modo "mitad y mitad"
Producto: menu            → Muestra el menú completo
Producto: fin             → Termina de agregar productos
```

```
7. Escribí observaciones si las hay (ej: "sin cebolla")
8. Si es envío, seleccioná el cadete
9. Elegí medio de pago: 1=Efectivo, 2=Online
10. ¡Listo! Se imprimen la comanda y el ticket automáticamente
```

### 📊 Ver la Liquidación de Cadetes

```
Menú principal → 3 (Administrar) → 2 (Reportes) → 2 (Liquidación)
```

Muestra una tabla con:
```
Cadete              Envios   Comision   Base       Total
─────────────────────────────────────────────────────────
Juan                5        $7500      $10000     $17500
María               3        $4500      $10000     $14500
```

### 📈 Generar Reporte Fiscal (ARCA)

```
Menú principal → 3 (Administrar) → 2 (Reportes) → 3 (Resumen de Ventas)
```

Permite ver:
- Ventas de **hoy**
- Ventas de un **día específico**
- Ventas de un **mes completo**
- **Todo el historial**

Separa automáticamente **Efectivo** vs **Online** para declarar en ARCA.

### 📂 Exportar a Excel

```
Menú principal → 3 (Administrar) → 3 (Exportar a Excel)
```

Genera un archivo `.csv` que se abre perfectamente en Excel con:
- Separador `;` (punto y coma) — Compatible con Excel en español
- Encoding `utf-8-sig` — Para que los acentos y la ñ se vean bien
- Columnas: ID, Fecha, Cliente, Teléfono, Dirección, Tipo Entrega, Envío, Cadete, Método Pago, Total, Items

---

## ❓ FAQ / Solución de Problemas

### 🔴 "python no se reconoce como un comando"

**Causa:** Python no se agregó al PATH durante la instalación.

**Solución:**
1. Desinstalá Python desde **Configuración → Aplicaciones**
2. Volvé a instalar Python marcando **"Add python.exe to PATH"**
3. Reiniciá la computadora

---

### 🔴 La impresora no imprime / "No se pudo copiar el archivo"

**Causa:** La impresora no está compartida correctamente.

**Solución:**
1. Verificá que la impresora esté compartida con el nombre exacto **`POS80`**
2. Abrí `cmd` y probá: `copy /b test.txt "\\127.0.0.1\POS80"`
3. Verificá que `OUTPUT_MODE` esté en `'POS80'` en `config.py`

---

### 🔴 El ticket sale con el texto chico o con márgenes

**Causa:** La impresora está usando el driver de Windows en vez del modo RAW.

**Solución:** El sistema usa `copy /b` (modo RAW binario) para enviar los datos directamente. Asegurate de que la impresora esté compartida como **POS80** y no estés usando "Imprimir" de Windows.

---

### 🔴 Al abrir el CSV en Excel, los acentos se ven raro (Ã¡ en vez de á)

**Causa:** Excel no reconoció la codificación del archivo.

**Solución:** El sistema ya genera los CSV con encoding `utf-8-sig` (BOM), lo que debería funcionar automáticamente. Si aún así se ven mal:
1. Abrí Excel
2. Pestaña **Datos → Obtener datos → Desde archivo de texto**
3. Seleccioná el archivo `.csv`
4. En la ventana de importación, elegí codificación **UTF-8**
5. Separador: **Punto y coma**

---

### 🔴 Se me cerró el sistema y perdí datos

**No te preocupes.** Los datos se guardan automáticamente en `pizzeria.db` después de cada operación. Al volver a abrir el sistema, todo tu historial va a seguir ahí.

---

### 🟡 ¿Cómo cambio los precios de los productos?

```
Menú principal → 3 (Administrar) → 1 (Gestión) → 1 (Productos) → 2 (Editar)
```

---

### 🟡 ¿Puedo agregar un nuevo tipo de producto (no solo pizza)?

Sí. El sistema soporta 3 categorías:
- 🍕 **Pizza**
- 🍟 **Papas**
- 🥟 **Empanadas**

Al agregar un producto, el sistema te pregunta en qué categoría ponerlo.

---

### 🟡 ¿Qué pasa si borro un cadete que ya tiene pedidos?

Los pedidos anteriores conservan el nombre del cadete en su registro. La liquidación del día mostrará a cadetes eliminados con la etiqueta **(ELIMINADO)** si tienen entregas ese día.

---

### 🟡 ¿Puedo usar el sistema sin impresora?

¡Sí! Cambiá `OUTPUT_MODE` a `'PDF'` o `'DEBUG'` en `config.py`:
- **PDF**: Abre la ventana de Windows para "imprimir" (podés guardar como PDF)
- **DEBUG**: Solo muestra el ticket en la pantalla negra

---

### 🟡 ¿Dónde se guardan los datos?

En el archivo `pizzeria.db` que está en la misma carpeta del sistema. Es un archivo de base de datos SQLite. **No lo borres** — ahí está todo el historial de pedidos, productos y cadetes.

---

<p align="center">
  <strong>🍕 Hecho con 🧡 para LPM Pizzas — M.David 4304 🍕</strong>
</p>

<p align="center">
  <sub>Sistema de Gestión v2.0 · Arquitectura por Capas · Python 3 + SQLite</sub>
</p>
