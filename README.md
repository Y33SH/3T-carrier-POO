# 3T Carrier - Sistema de Gestión Logística

Sistema web para administrar las operaciones de **3T Carrier**.

## Tecnologías

- Python
- Flask
- HTML
- CSS
- SQLAlchemy
- MySQL
- PyMySQL
- Flask-Login
- python-dotenv

## Estructura

```text
3T-carrier-POO/
│
├── app.py
├── config.py
├── models.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── static/
│   └── css/
│       ├── estilos.css
│       └── IMG/
│
└── templates/
    ├── login.html
    ├── dashboard.html
    ├── clientes.html
    ├── nuevo_cliente.html
    ├── pedidos.html
    ├── nuevo_pedido.html
    ├── operadores.html
    ├── unidades.html
    ├── asignaciones.html
    ├── seguimiento.html
    └── incidencias.html
```

## Archivos principales

### `app.py`
Aplicación principal de Flask. Contiene las rutas y será el intermediario entre las páginas HTML y la base de datos.

### `config.py`
Configuración de Flask y conexión con MySQL. Las credenciales deben obtenerse desde `.env`.

### `models.py`
Modelos SQLAlchemy que representan las tablas y relaciones de la base de datos.

### `templates/`
Interfaces HTML del sistema.

### `static/`
CSS, imágenes y demás archivos estáticos.

## Módulos

El sistema contempla:

- Login y usuarios
- Dashboard
- Clientes
- Pedidos
- Operadores
- Unidades
- Asignaciones
- Seguimiento
- Incidencias

## Base de datos

Base propuesta:

```text
BD_GestionLogistica3T
```

Tablas principales:

```text
Usuarios
Clientes
TiposServicio
Pedidos
Operadores
Unidades
Asignaciones
Seguimientos
Incidencias
```

Relación general:

```text
Cliente
   ↓
Pedido ← TipoServicio
   ↓
Asignación
 ├── Operador
 └── Unidad

Pedido
 ├── Seguimientos
 └── Incidencias
```

## Arquitectura

```text
HTML/CSS
   ↓
Flask (app.py)
   ↓
SQLAlchemy (models.py)
   ↓
MySQL
```

## Objetivo de la integración

Actualmente existe la interfaz y estructura inicial del sistema.

La siguiente etapa es conectar todas las páginas con la base de datos para que los datos sean reales y dinámicos.

Se necesita implementar:

1. Conexión Flask → MySQL.
2. Modelos y relaciones SQLAlchemy.
3. Creación de tablas.
4. CRUD de clientes.
5. CRUD de pedidos.
6. CRUD de operadores.
7. CRUD de unidades.
8. Asignaciones de pedido + operador + unidad.
9. Seguimiento de pedidos.
10. Registro de incidencias.
11. Login real con usuarios.
12. Dashboard calculado con información de la BD.

El sistema debe evitar datos escritos manualmente en HTML.

Ejemplo:

```python
pedidos = Pedido.query.all()
return render_template("pedidos.html", pedidos=pedidos)
```

Y en HTML:

```html
{% for pedido in pedidos %}
    {{ pedido.id }}
{% endfor %}
```

## Seguridad

NO subir a GitHub:

```text
.env
contraseñas
tokens
secret keys
credenciales de MySQL
```

`.env.example` solamente debe mostrar las variables necesarias:

```env
SECRET_KEY=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=
```

Las contraseñas de usuarios tampoco deben almacenarse en texto plano.

## Estado actual

- Frontend: desarrollado
- Flask: estructura inicial
- Login visual: desarrollado
- Dashboard visual: desarrollado
- Base de datos: pendiente de integración
- CRUD: pendiente
- Autenticación real: pendiente

## Instrucción para continuar el proyecto

Antes de modificar código:

1. Analizar todos los archivos existentes.
2. No reemplazar innecesariamente el frontend actual.
3. Mantener las rutas y nombres de templates cuando sea posible.
4. Revisar `app.py`, `config.py` y `models.py`.
5. Implementar la base de datos por etapas.
6. Explicar cada modificación antes de realizarla.
7. Trabajar un módulo a la vez y comprobar que funciona antes de continuar.
8. Mantener las credenciales fuera del repositorio.
