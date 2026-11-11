# Contexto técnico del sistema 3T Carrier

Este documento resume la arquitectura y las funciones incorporadas al sistema para servir como contexto de trabajo para un asistente de IA y como base para el manual técnico. Se redactó a partir del estado actual del código; antes de documentar una instalación o despliegue, confirmar la configuración concreta del entorno y de la base de datos.

## 1. Descripción general

3T Carrier es una aplicación web para gestión logística desarrollada con Flask, SQLAlchemy y plantillas Jinja2. La aplicación principal concentra rutas, validaciones de flujo y permisos en `app.py`; los modelos ORM se definen en `models.py`; la interfaz está en `templates/`; los estilos y scripts se encuentran en `static/`. La base de datos se configura mediante `config.py` y las migraciones de esquema están en `migrations/`.

El sistema contempla cuatro roles:

- **Administrador:** gestión completa del sistema y configuración de cuentas.
- **Editor:** operación diaria de pedidos, asignaciones, seguimiento e incidencias.
- **Consultor:** autoservicio limitado a los pedidos de su cliente vinculado y solicitudes de cotización.
- **Usuario:** cuenta creada que aún no está habilitada como Consultor; al iniciar sesión recibe un aviso para contactar al administrador.

## 2. Arquitectura y conceptos de POO

- Los modelos `Usuario`, `Cliente`, `TipoServicio`, `Operador`, `Unidad`, `Pedido`, `Asignacion`, `Seguimiento` e `Incidencia` son clases que heredan de `db.Model`.
- SQLAlchemy mapea sus atributos a columnas y relaciones de la base de datos.
- `Usuario` implementa métodos de instancia para establecer y comprobar contraseñas (`set_password` y `verificar_password`).
- `app.py` contiene las rutas Flask, los decoradores de autenticación/autorización y funciones auxiliares para lógica compartida.
- Las plantillas Jinja2 presentan los datos y controlan la visibilidad de enlaces con condiciones de rol. La autorización real también se verifica en las rutas del servidor.

## 3. Modelo de datos y relaciones relevantes

- `Usuario.id_cliente` es una clave foránea opcional hacia `Cliente.id_cliente`; permite asociar una cuenta de Consultor a un cliente.
- `Pedido.id_cliente` relaciona el pedido con su cliente.
- `Pedido.id_tipo_servicio` relaciona el pedido con `TipoServicio`.
- `Asignacion.id_pedido`, `Seguimiento.id_pedido` e `Incidencia.id_pedido` relacionan la operación con un pedido.
- Los modelos `Asignacion` también enlazan un operador y una unidad.
- El folio de pedido es único en la base de datos.

La migración `migrations/versions/f7c20d5b9e31_vincular_usuarios_con_clientes.py` agrega `usuarios.id_cliente` y su clave foránea. Debe aplicarse con el flujo de Flask-Migrate/Alembic del proyecto antes de utilizar la vinculación de Consultores en una base existente.

## 4. Autenticación, sesión y autorización

- El inicio de sesión está disponible en `/` y `/login`.
- La contraseña se compara con `check_password_hash`; las cuentas creadas desde administración guardan la contraseña mediante `generate_password_hash`.
- Después de autenticar, se guardan en la sesión el identificador, nombre y rol del usuario, además de datos de control de actividad y fecha.
- Administrador y Editor llegan al Dashboard; Consultor llega a “Mis pedidos”; Usuario sin habilitar recibe un aviso y se limpia su sesión.
- `login_requerido` exige una sesión y `roles_requeridos(...)` exige sesión y uno de los roles indicados.
- `validar_expiracion_sesion` revisa actividad y fecha; una sesión vencida se limpia y redirige al login.
- `/logout` limpia la sesión.

La visibilidad del menú no sustituye los decoradores de autorización: las rutas deben conservar sus controles de rol aunque un enlace esté oculto en la interfaz.

## 5. Matriz de módulos por rol

| Módulo / función | Administrador | Editor | Consultor | Usuario |
|---|---:|---:|---:|---:|
| Dashboard | Sí | Sí | Sí | No se habilita el acceso normal |
| Seguimiento | Sí | Sí | Sí, filtrado por cliente | No |
| Pedidos operativos | Sí | Sí | No | No |
| Asignaciones e incidencias | Sí | Sí | No | No |
| Clientes, operadores y unidades | Sí | No | No | No |
| Reportes administrativos | Sí | No | No | No |
| Vincular cuentas y crear usuarios | Sí | No | No | No |
| Mis pedidos y solicitar cotización | No | No | Sí | No |

Las plantillas de navegación relevantes incluyen `base.html`, `dashboard.html`, `seguimiento.html`, `mis_pedidos.html`, `cotizacion.html`, `usuarios_consultor.html` y las páginas de módulos operativos.

## 6. Administración de cuentas y vinculación de clientes

- `GET/POST /admin/crear-usuario` crea cuentas solo con rol `Usuario` o `Consultor`. Rechaza roles distintos, nombres vacíos o demasiado largos y nombres de usuario existentes.
- `GET/POST /admin/consultores` lista cuentas con rol `Usuario` o `Consultor`; permite elegir un cliente y guardar la cuenta como Consultor vinculada.
- La eliminación desde el módulo de vinculación usa `POST /admin/usuarios/<id_usuario>/eliminar`. Solo permite eliminar cuentas Usuario o Consultor, y no permite eliminar la cuenta administradora con la que se inició sesión. Las restricciones de claves foráneas pueden impedir eliminar una cuenta todavía referenciada.
- En los selectores de clientes se agrupa la razón social ignorando espacios externos y diferencias entre mayúsculas/minúsculas. Cuando una cuenta ya está vinculada a uno de varios registros con la misma razón social, se conserva ese registro como opción seleccionada.
- No se fusionan ni borran automáticamente los registros de clientes duplicados existentes.

## 7. Autoservicio del Consultor

- `GET /mis-pedidos` muestra pedidos cuyo `id_cliente` corresponde al usuario autenticado. También excluye cotizaciones marcadas `CANCELADO POR CLIENTE`.
- `GET/POST /solicitar-cotizacion` presenta y procesa el formulario de cotización con tipo de servicio, origen y destino.
- El pedido nuevo usa el cliente del Consultor autenticado, tarifa `0.00`, estado `Pendiente de Aprobar` y folio con prefijo `COT-`.
- El formulario incluye un token UUID como clave de idempotencia. Reenviar el mismo formulario no crea una segunda solicitud; el botón también se desactiva al enviar.
- `POST /mis-pedidos/<id_pedido>/cancelar` solo permite cancelar una cotización `COT-` pendiente que pertenezca al cliente de la sesión.
- La cancelación cambia el estado a `CANCELADO POR CLIENTE`, conserva el registro como historial y lo oculta de “Mis pedidos”, del listado operativo de pedidos y de los selectores para nuevas asignaciones e incidencias.
- No se permite cancelar pedidos que ya tengan asignación, seguimiento o incidencia relacionada.
- La página del Consultor no expone botones de cancelación para pedidos aprobados u otros pedidos que no cumplan las condiciones anteriores.

## 8. Catálogos, pedidos y reglas de negocio

- La creación de clientes rechaza una razón social vacía o ya registrada después de normalizar espacios externos y mayúsculas/minúsculas.
- La edición de clientes aplica la misma regla excluyendo el registro que se está editando.
- La comprobación de razón social duplicada está en la lógica de aplicación; no hay una restricción única de base de datos que garantice unicidad ante escrituras concurrentes.
- `clientes_sin_duplicados(...)` reduce repetición visual en formularios de pedidos y vinculación sin borrar filas históricas.
- `tipos_servicio_sin_duplicados(...)` evita repetir tipos de servicio con nombres equivalentes y conserva el servicio asociado al editar.
- Los pedidos de Consultor no se consultan por un identificador enviado desde el navegador: se filtran usando el `id_cliente` de la cuenta autenticada.
- Las cotizaciones canceladas se excluyen de la lista operativa de pedidos y no se ofrecen para crear asignaciones ni incidencias.

## 9. Seguimiento

- La ruta `/seguimiento` comparte la vista de seguimiento con permisos según rol.
- Para un Consultor, la consulta se limita a pedidos del cliente vinculado y sus asignaciones/seguimientos asociados.
- Administrador y Editor ven el seguimiento operativo general.
- La barra lateral de seguimiento incluye los enlaces de autoservicio para Consultores, además de los enlaces administrativos u operativos permitidos al rol actual.

## 10. Reportes y documentos PDF

- `/reportes` y `/reportes/<tipo>` están disponibles para Administrador.
- Los reportes se generan como PDF usando ReportLab.
- `GET /descargar-carta-porte/<id_asignacion>` está protegido para Administrador y Editor; incluye datos del pedido, cliente, servicio, operador, unidad, tarifa, estados y fechas.
- `GET /descargar-reporte-incidencia/<id_incidencia>` está protegido para Administrador y Editor; incluye pedido, cliente, tipo de falla, descripción, fecha, estado y solución.
- Las tablas de asignaciones e incidencias enlazan con las descargas correspondientes.

## 11. Organización de archivos clave

- `app.py`: rutas Flask, roles, sesión, reglas de negocio, generación de PDF.
- `models.py`: entidades SQLAlchemy y relaciones.
- `config.py`: configuración de la aplicación y base de datos.
- `migrations/versions/`: cambios versionados del esquema.
- `templates/`: interfaz HTML/Jinja2 por módulo.
- `templates/base.html`: layout y menú común usado por algunas páginas.
- `static/css/estilos.css`: estilos y clases visuales de botones/tablas.
- `static/js/session-timeout.js`: lógica de expiración/notificación de sesión en el navegador.
- `requirements.txt`: dependencias Python del proyecto.

## 12. Validaciones realizadas durante los cambios

Las funciones añadidas o corregidas se probaron con una aplicación Flask temporal y una base SQLite temporal, sin modificar la base configurada para el proyecto. Se verificaron, entre otros:

- creación, rechazo de duplicados y permisos de cuentas;
- vinculación y filtrado de pedidos por cliente;
- generación y acceso a rutas de PDF;
- deduplicación de clientes/servicios en selectores;
- protección contra envíos repetidos de cotización;
- cancelación solo por el cliente propietario, retención del estado cancelado y exclusión de vistas/selector operativos;
- renderizado de menús según rol;
- sintaxis Python con `python -m py_compile app.py` y formato con `git diff --check`.

Estas pruebas aisladas no reemplazan una prueba de integración contra la base de datos real ni una revisión del despliegue.

## 13. Consideraciones para futuras modificaciones

1. Al añadir una función nueva, actualizar ruta, autorización del servidor, plantilla, navegación y pruebas del flujo.
2. No confiar solo en ocultar enlaces con Jinja2; proteger también cada ruta mediante decoradores.
3. Las operaciones de escritura deben validar la propiedad del registro usando la sesión autenticada, no datos de propiedad enviados por el cliente.
4. Mantener la regla de negocio para cotizaciones canceladas en todos los puntos que creen operaciones relacionadas.
5. Si se requiere eliminar físicamente una cotización, revisar antes las claves foráneas y el historial de asignaciones, seguimientos e incidencias. El comportamiento actual conserva el historial cambiando el estado y ocultando el pedido de las vistas activas.
6. Si se necesita garantía de unicidad de razón social ante concurrencia, planear una migración y una estrategia compatible con la base configurada; la validación actual de aplicación no es una restricción transaccional.
7. Aplicar las migraciones antes de desplegar cambios que dependan de nuevas columnas.
