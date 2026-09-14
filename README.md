# 3T Carrier - Sistema de Gestión Logística

Sistema web desarrollado con Python, Flask, HTML y CSS para la administración
de operaciones de 3T Carrier.

El frontend principal ya se encuentra desarrollado. El siguiente paso es
conectar los módulos con la base de datos y reemplazar los datos temporales
por información real.

---

## Tecnologías

- Python
- Flask
- HTML
- CSS
- SQLAlchemy
- Flask-Migrate
- MySQL (base de datos planeada)

---

## Estructura principal

### app.py
Contiene las rutas de Flask y conecta las páginas HTML con el backend.

Actualmente varias rutas utilizan listas vacías o valores en 0 para permitir
visualizar el frontend sin tener conectada la base de datos.

### models.py
Contiene los modelos que representan las entidades de la base de datos.

### config.py
Configuración de Flask y conexión con la base de datos.

### templates/
Contiene las interfaces HTML del sistema.

Principales módulos:

- Login
- Dashboard
- Clientes
- Pedidos
- Operadores
- Unidades
- Asignaciones
- Seguimiento
- Incidencias

También existen formularios para registrar nuevos datos.

### static/css/
Contiene los estilos generales de la aplicación y las imágenes utilizadas.

---

# Estado actual

## Frontend

El diseño principal ya está desarrollado.

Se cuenta con:

- Login
- Dashboard
- Gestión de clientes
- Gestión de pedidos
- Gestión de operadores
- Gestión de unidades
- Asignación de operador y unidad a pedidos
- Seguimiento de flota
- Gestión de incidencias

El módulo de seguimiento está pensado para evolucionar hacia un sistema de
rastreo de flotas con mapa, ubicación GPS, velocidad, ETA y estado de ruta.

---

# Trabajo pendiente - Backend y Base de Datos

## 1. Conectar MySQL

Configurar la conexión real utilizando las variables de entorno.

NO subir el archivo `.env` al repositorio.

Cada desarrollador debe crear su propio `.env` tomando como referencia
`.env.example`.

---

## 2. Conectar modelos

Revisar `models.py` y comprobar que los modelos coincidan con las tablas
definitivas de la base de datos.

Relaciones principales:

Cliente -> Pedido

Pedido -> Asignación

Operador -> Asignación

Unidad -> Asignación

Pedido -> Seguimiento

Pedido -> Incidencia

---

## 3. Reemplazar datos temporales

Actualmente existen secciones como:

```python
lista_clientes = []
lista_pedidos = []
lista_operadores = []
lista_unidades = []
