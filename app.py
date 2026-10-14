from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from functools import wraps
from werkzeug.security import check_password_hash # Para validar contraseñas seguras

from config import Config
from models import (
    db,
    Cliente,
    TipoServicio,
    Pedido,
    Unidad,
    Operador,
    Asignacion,
    Seguimiento,
    Incidencia,
    Usuario  # <-- Importamos el modelo Usuario
)

app = Flask(__name__)

app.config.from_object(Config)
# Necesario para manejar sesiones en Flask. Si no está en tu config.py, defínelo aquí:
app.secret_key = app.config.get('SECRET_KEY', 'e902e1c0487a95a51b43705fb95e0d4e8012c16cf2285b490cf65824de21ac31')

db.init_app(app)
migrate = Migrate(app, db)

# ==========================================
# DECORADORES PARA VALIDAR SESIÓN Y ROLES
# ==========================================

def login_requerido(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Por favor, inicia sesión para acceder.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

def roles_requeridos(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'usuario_id' not in session:
                flash("Por favor, inicia sesión para acceder.", "error")
                return redirect(url_for('login'))
            if session.get('rol') not in roles:
                flash("Acceso denegado: No tienes permisos para realizar esta acción.", "error")
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper

# ==========================================
# RUTAS DE AUTENTICACIÓN
# ==========================================

@app.route("/", methods=["GET", "POST"])
def login():
    # Si ya hay sesión activa, mandarlo directo al dashboard
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        usuario_input = request.form.get("usuario")
        password_input = request.form.get("password")

        # Buscar en la BD
        user = Usuario.query.filter_by(usuario=usuario_input).first()

        # Validar contraseña. 
        # OJO: Si guardaste las contraseñas sin encriptar en tu BD usa: 
        # if user and user.contrasena == password_input:
        if user and check_password_hash(user.contrasena, password_input):
            # Guardar datos en la sesión
            session['usuario_id'] = user.id_usuario
            session['usuario_nombre'] = user.nombre
            session['rol'] = user.rol # 'Administrador', 'Editor', o 'Consultor/Usuario'
            
            return redirect(url_for("dashboard"))
        else:
            flash("Usuario o contraseña incorrectos", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ==========================================
# RUTAS DEL SISTEMA
# ==========================================

@app.route("/dashboard")
@login_requerido # Todos los logueados pueden ver el dashboard
def dashboard():
    pedidos_activos = Pedido.query.filter(
        Pedido.estado.in_(["REGISTRADO", "ASIGNADO", "EN TRANSITO"])
    ).count()

    unidades_disponibles = Unidad.query.filter_by(
        estado="DISPONIBLE"
    ).count()

    operadores_disponibles = Operador.query.filter_by(
        disponibilidad=True
    ).count()

    incidencias_abiertas = Incidencia.query.filter(
        Incidencia.estado.in_(["ABIERTA", "EN PROCESO"])
    ).count()

    return render_template(
        "dashboard.html",
        pedidos_activos=pedidos_activos,
        unidades_disponibles=unidades_disponibles,
        operadores_disponibles=operadores_disponibles,
        incidencias_abiertas=incidencias_abiertas,
        rol=session.get('rol') # Pasamos el rol a la plantilla por si quieres ocultar botones
    )

@app.route("/clientes")
@login_requerido
def clientes():
    lista_clientes = Cliente.query.all()
    return render_template("clientes.html", clientes=lista_clientes)

@app.route("/nuevo-cliente", methods=["GET", "POST"])
@roles_requeridos('Administrador') # Solo el Administrador puede crear clientes
def nuevo_cliente():
    if request.method == "POST":
        cliente = Cliente(
            razon_social=request.form["razon_social"],
            nombre_contacto=request.form["nombre_contacto"],
            telefono=request.form.get("telefono"),
            correo=request.form.get("correo"),
            direccion=request.form.get("direccion"),
            pais=request.form.get("pais"),
            estado=request.form.get("estado")
        )
        db.session.add(cliente)
        db.session.commit()
        return redirect(url_for("clientes"))

    return render_template("nuevo_cliente.html")

@app.route("/pedidos")
@login_requerido
def pedidos():
    lista_pedidos = Pedido.query.all()
    return render_template("pedidos.html", pedidos=lista_pedidos)

@app.route("/nuevo-pedido")
@roles_requeridos('Administrador', 'Editor') # Admin y Editor pueden crear pedidos
def nuevo_pedido():
    clientes = Cliente.query.all()
    servicios = TipoServicio.query.all()
    return render_template("nuevo_pedido.html", clientes=clientes, servicios=servicios)

@app.route("/operadores")
@login_requerido
def operadores():
    lista_operadores = Operador.query.all()
    return render_template("operadores.html", operadores=lista_operadores)

@app.route("/unidades")
@login_requerido
def unidades():
    lista_unidades = Unidad.query.all()
    return render_template("unidades.html", unidades=lista_unidades)

@app.route("/nueva-unidad", methods=["GET", "POST"])
@roles_requeridos('Administrador')
def nueva_unidad():
    if request.method == "POST":
        capacidad = request.form.get("capacidad")
        unidad = Unidad(
            numero_economico=request.form["numero_economico"],
            placas=request.form["placas"],
            marca=request.form.get("marca"),
            modelo=request.form.get("modelo"),
            capacidad=capacidad if capacidad else None,
            ubicacion_actual=request.form.get("ubicacion_actual"),
            estado=request.form["estado"]
        )
        db.session.add(unidad)
        db.session.commit()
        return redirect(url_for("unidades"))

    return render_template("nuevo_unidad.html")

@app.route("/asignaciones")
@login_requerido
def asignaciones():
    lista_asignaciones = Asignacion.query.all()
    return render_template("asignaciones.html", asignaciones=lista_asignaciones)

@app.route("/nueva-asignacion", methods=["GET", "POST"])
@roles_requeridos('Administrador', 'Editor')
def nueva_asignacion():
    pedidos = Pedido.query.all()
    operadores = Operador.query.all()
    unidades = Unidad.query.all()

    if request.method == "POST":
        asignacion = Asignacion(
            id_pedido=request.form["id_pedido"],
            id_operador=request.form["id_operador"],
            id_unidad=request.form["id_unidad"],
            fecha_asignacion=request.form["fecha_asignacion"],
            fecha_inicio=request.form.get("fecha_inicio") or None,
            fecha_fin=request.form.get("fecha_fin") or None,
            estado=request.form["estado"]
        )
        db.session.add(asignacion)
        db.session.commit()
        return redirect(url_for("asignaciones"))

    return render_template("nueva_asignacion.html", pedidos=pedidos, operadores=operadores, unidades=unidades)

@app.route("/seguimiento")
@login_requerido
def seguimiento():
    lista_seguimientos = Seguimiento.query.all()
    return render_template("seguimiento.html", seguimientos=lista_seguimientos, unidades_ruta=0, entregas_tiempo=0, retrasos=0, incidencias_activas=0)

@app.route("/incidencias")
@login_requerido
def incidencias():
    lista_incidencias = Incidencia.query.all()
    return render_template("incidencias.html", incidencias=lista_incidencias)

@app.route("/nueva-incidencia", methods=["GET", "POST"])
@roles_requeridos('Administrador', 'Editor')
def nueva_incidencia():
    pedidos = Pedido.query.all()
    if request.method == "POST":
        incidencia = Incidencia(
            id_pedido=request.form["id_pedido"],
            tipo=request.form["tipo"],
            descripcion=request.form["descripcion"],
            fecha_hora=request.form["fecha_hora"],
            estado=request.form["estado"],
            solucion=request.form.get("solucion")
        )
        db.session.add(incidencia)
        db.session.commit()
        return redirect(url_for("incidencias"))

    return render_template("nueva_incidencia.html", pedidos=pedidos)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)