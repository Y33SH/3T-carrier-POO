from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from functools import wraps
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
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
        password_input = request.form.get("password", "")

        # Buscar en la BD
        user = Usuario.query.filter_by(usuario=usuario_input).first()

        if user is None:
            flash(
                "No encontramos ninguna cuenta con ese nombre de usuario. "
                "Por favor, revisa que esté bien escrito.",
                "error",
            )
        elif not check_password_hash(user.contrasena, password_input):
            flash(
                "Parece que la contraseña es incorrecta,  inténtalo de nuevo.",
                "error",
            )
        else:
            # Guardar datos en la sesión
            session['usuario_id'] = user.id_usuario
            session['usuario_nombre'] = user.nombre
            session['rol'] = user.rol # 'Administrador', 'Editor', o 'Consultor/Usuario'
            
            return redirect(url_for("dashboard"))

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

@app.route("/nuevo_cliente", methods=["GET", "POST"])
@app.route("/nuevo-cliente", methods=["GET", "POST"])
@roles_requeridos('Administrador')
def nuevo_cliente():
    if request.method == "POST":
        datos_cliente = {
            campo: request.form.get(campo)
            for campo in (
                "razon_social",
                "rfc",
                "nombre_contacto",
                "telefono",
                "correo",
                "direccion",
                "pais",
                "estado",
            )
        }

        if not datos_cliente["razon_social"] or not datos_cliente["razon_social"].strip():
            flash("Parece que olvidaste la Razón Social. Este dato es obligatorio para registrar al cliente.", "error")
            return redirect(url_for("nuevo_cliente"))
            
        if not datos_cliente["nombre_contacto"] or not datos_cliente["nombre_contacto"].strip():
            flash("Necesitamos el Nombre de Contacto para saber con quién comunicarnos.", "error")
            return redirect(url_for("nuevo_cliente"))

        if datos_cliente["telefono"] and not datos_cliente["telefono"].isdigit():
            flash("El número de teléfono tiene letras o espacios. Por favor, escribe solo números (ej. 8123456789).", "error")
            return redirect(url_for("nuevo_cliente"))
            
        if datos_cliente["telefono"] and len(datos_cliente["telefono"]) < 10:
             flash("El teléfono parece estar muy corto. Revisa que tenga al menos 10 números.", "error")
             return redirect(url_for("nuevo_cliente"))

        if datos_cliente["correo"] and "@" not in datos_cliente["correo"]:
            flash("El correo electrónico está incompleto. Asegúrate de que incluya el símbolo '@'.", "error")
            return redirect(url_for("nuevo_cliente"))

        rfc = datos_cliente["rfc"]
        if rfc and Cliente.query.filter_by(rfc=rfc).first():
            flash(
                "Ups, parece que el RFC que ingresaste ya pertenece a otro cliente registrado. ¿Podrías revisarlo?",
                "warning",
            )
            return redirect(url_for("nuevo_cliente"))

        try:
            cliente = Cliente(**datos_cliente)
            db.session.add(cliente)
            db.session.commit()
            
            flash(
                "¡Listo! El cliente se registró correctamente. Ya puedes asignarle servicios.",
                "success",
            )
            return redirect(url_for("clientes"))
            
        except SQLAlchemyError:
            db.session.rollback()
            flash("Ups, hubo un problema al intentar guardar en la base de datos.", "error")
            return redirect(url_for("nuevo_cliente"))

    return render_template("nuevo_cliente.html")

@app.route("/editar_cliente/<int:id_cliente>", methods=["POST"])
@roles_requeridos('Administrador')
def editar_cliente(id_cliente):
    cliente = Cliente.query.get_or_404(id_cliente)
    campos = (
        "razon_social",
        "rfc",
        "nombre_contacto",
        "telefono",
        "correo",
        "direccion",
        "pais",
        "estado",
    )
    datos_cliente = {campo: request.form.get(campo) for campo in campos}

    rfc = datos_cliente["rfc"]
    if rfc and Cliente.query.filter(
        Cliente.rfc == rfc,
        Cliente.id_cliente != id_cliente,
    ).first():
        flash(
            "Ups, parece que el RFC que ingresaste ya pertenece a otro cliente registrado. ¿Podrías revisarlo?",
            "warning",
        )
        return redirect(url_for("clientes"))

    try:
        for campo, valor in datos_cliente.items():
            setattr(cliente, campo, valor)
        db.session.commit()
        flash("Los datos del cliente se actualizaron perfectamente.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("No pudimos guardar los cambios del cliente. Inténtalo de nuevo.", "error")

    return redirect(url_for("clientes"))

@app.route("/eliminar_cliente/<int:id_cliente>", methods=["POST"])
@app.route("/eliminar-cliente/<int:id_cliente>", methods=["POST"])
@roles_requeridos('Administrador')
def eliminar_cliente(id_cliente):
    cliente = Cliente.query.get_or_404(id_cliente)

    try:
        db.session.delete(cliente)
        db.session.commit()
        flash("El cliente ha sido eliminado de tus registros.", "info")
    except SQLAlchemyError:
        db.session.rollback()
        flash("No pudimos eliminar al cliente. Puede que aún esté relacionado con otros registros.", "error")

    return redirect(url_for("clientes"))
    
@app.route("/pedidos")
@login_requerido
def pedidos():
    lista_pedidos = Pedido.query.all()
    return render_template("pedidos.html", pedidos=lista_pedidos)

@app.route("/nuevo-pedido", methods=["GET", "POST"])
@app.route("/nuevo_pedido", methods=["GET", "POST"])
@roles_requeridos('Administrador', 'Editor') # Admin y Editor pueden crear pedidos
def nuevo_pedido():
    if request.method == "POST":
        try:
            id_cliente = int(request.form.get("id_cliente", ""))
            id_tipo_servicio = int(request.form.get("id_tipo_servicio", ""))
        except (TypeError, ValueError):
            flash("Selecciona un cliente y un servicio para poder registrar el pedido.", "error")
            return redirect(url_for("nuevo_pedido"))

        folio = (request.form.get("folio") or "").strip()
        if Pedido.query.filter_by(folio=folio).first():
            flash(
                "El folio que intentas registrar ya existe en el sistema. Por favor, verifica el número de orden.",
                "warning",
            )
            return redirect(url_for("nuevo_pedido"))

        origen = (request.form.get("origen") or "").strip()
        destino = (request.form.get("destino") or "").strip()
        if not folio or not origen or not destino:
            flash("Completa el folio, el origen y el destino para registrar el pedido.", "error")
            return redirect(url_for("nuevo_pedido"))

        tarifa_form = request.form.get("tarifa", "").strip()
        try:
            tarifa = Decimal(tarifa_form) if tarifa_form else None
            fecha_form = request.form.get("fecha_estimada", "").strip()
            fecha_estimada = datetime.fromisoformat(fecha_form) if fecha_form else None
        except (InvalidOperation, ValueError):
            flash("Revisa la tarifa y la fecha estimada; alguno de esos datos no tiene un formato válido.", "error")
            return redirect(url_for("nuevo_pedido"))

        pedido = Pedido(
            id_cliente=id_cliente,
            id_tipo_servicio=id_tipo_servicio,
            folio=folio,
            origen=origen,
            destino=destino,
            mercancia=request.form.get("mercancia") or None,
            tarifa=tarifa,
            fecha_estimada=fecha_estimada,
            estado=request.form.get("estado") or "REGISTRADO",
        )
        try:
            db.session.add(pedido)
            db.session.commit()
            flash(
                "¡Excelente! El pedido se registró correctamente y está listo para ser asignado a una unidad.",
                "success",
            )
            return redirect(url_for("pedidos"))
        except SQLAlchemyError:
            db.session.rollback()
            flash("No pudimos guardar el pedido en este momento. Revisa los datos e inténtalo de nuevo.", "error")
            return redirect(url_for("nuevo_pedido"))

    clientes = Cliente.query.all()
    servicios = TipoServicio.query.all()
    return render_template("nuevo_pedido.html", clientes=clientes, servicios=servicios)

@app.route("/eliminar_pedido/<int:id_pedido>", methods=["POST"])
@app.route("/eliminar-pedido/<int:id_pedido>", methods=["POST"])
@roles_requeridos('Administrador', 'Editor')
def eliminar_pedido(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)

    try:
        db.session.delete(pedido)
        db.session.commit()
        flash("El pedido ha sido cancelado y eliminado del sistema.", "info")
    except SQLAlchemyError:
        db.session.rollback()
        flash("No pudimos eliminar el pedido porque todavía está relacionado con otros registros.", "error")

    return redirect(url_for("pedidos"))

@app.route("/operadores")
@login_requerido
def operadores():
    lista_operadores = Operador.query.all()
    return render_template("operadores.html", operadores=lista_operadores)

@app.route("/nuevo_operador", methods=["GET", "POST"])
@roles_requeridos('Administrador')
def nuevo_operador():
    if request.method == "GET":
        return render_template("nuevo_operador.html")

    datos, error = validar_datos_operador(request.form)
    if error:
        flash(error, "error")
        return render_template("nuevo_operador.html", datos_operador=request.form)

    if Operador.query.filter_by(numero_licencia=datos["numero_licencia"]).first():
        flash(
            "El número de licencia ingresado ya está registrado con otro operador. Por favor, verifica el dato.",
            "warning",
        )
        return render_template("nuevo_operador.html", datos_operador=request.form)

    try:
        operador = Operador(**datos)
        db.session.add(operador)
        db.session.commit()
        flash(
            f"¡Listo! El operador {operador.nombre} se ha registrado correctamente y está listo para ruta.",
            "success",
        )
    except IntegrityError:
        db.session.rollback()
        flash(
            "El número de licencia ingresado ya está registrado con otro operador. Por favor, verifica el dato.",
            "warning",
        )
        return render_template("nuevo_operador.html", datos_operador=request.form)
    except SQLAlchemyError:
        db.session.rollback()
        flash("No pudimos guardar al operador. Revisa tus datos e inténtalo de nuevo.", "error")
        return render_template("nuevo_operador.html", datos_operador=request.form)

    return redirect(url_for("operadores"))

def validar_datos_operador(formulario):
    nombre = (formulario.get("nombre") or "").strip()
    telefono = (formulario.get("telefono") or "").strip()
    numero_licencia = (formulario.get("numero_licencia") or "").strip()
    tipo_licencia = (formulario.get("tipo_licencia") or "").strip()
    vigencia_form = (formulario.get("vigencia_licencia") or "").strip()
    horas_form = (formulario.get("horas_servicio") or "").strip()
    disponibilidad_form = (formulario.get("disponibilidad") or "").strip().lower()

    if not nombre:
        return None, "Escribe el nombre del operador para continuar."
    if len(nombre) > 120:
        return None, "El nombre es demasiado largo. Usa 120 caracteres o menos."
    if not numero_licencia:
        return None, "Escribe el número de licencia del operador para continuar."
    if len(numero_licencia) > 50:
        return None, "El número de licencia es demasiado largo. Revisa que esté escrito correctamente."
    if telefono and (
        len(telefono) > 20
        or not any(caracter.isdigit() for caracter in telefono)
        or not all(caracter.isdigit() or caracter in " +()-." for caracter in telefono)
    ):
        return None, "Revisa el teléfono: escribe números y, si hace falta, espacios, paréntesis o guiones."
    if len(tipo_licencia) > 50:
        return None, "El tipo de licencia es demasiado largo. Usa 50 caracteres o menos."
    if disponibilidad_form not in ("true", "false", "1", "0", "si", "sí", "no"):
        return None, "Selecciona si el operador está disponible o no."

    try:
        vigencia = date.fromisoformat(vigencia_form) if vigencia_form else None
    except ValueError:
        return None, "La fecha de vigencia no parece correcta. Selecciónala nuevamente."

    try:
        horas = Decimal(horas_form) if horas_form else Decimal("0")
        if not horas.is_finite() or horas < 0 or horas > Decimal("999.99"):
            return None, "Las horas de servicio deben ser un número entre 0 y 999.99."
    except InvalidOperation:
        return None, "Las horas de servicio deben escribirse como un número, por ejemplo 12.5."

    return {
        "nombre": nombre,
        "telefono": telefono or None,
        "numero_licencia": numero_licencia,
        "tipo_licencia": tipo_licencia or None,
        "vigencia_licencia": vigencia,
        "disponibilidad": disponibilidad_form in ("true", "1", "si", "sí"),
        "horas_servicio": horas,
    }, None

@app.route("/editar_operador/<int:id_operador>", methods=["POST"])
@roles_requeridos('Administrador')
def editar_operador(id_operador):
    operador = Operador.query.get_or_404(id_operador)
    datos, error = validar_datos_operador(request.form)
    if error:
        flash(error, "error")
        return redirect(url_for("operadores"))

    licencia_existente = Operador.query.filter(
        Operador.numero_licencia == datos["numero_licencia"],
        Operador.id_operador != id_operador,
    ).first()
    if licencia_existente:
        flash(
            "El número de licencia ingresado ya está registrado con otro operador. Por favor, verifica el dato.",
            "warning",
        )
        return redirect(url_for("operadores"))

    try:
        for campo, valor in datos.items():
            setattr(operador, campo, valor)
        db.session.commit()
        flash("Los datos del operador se actualizaron perfectamente.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(
            "El número de licencia ingresado ya está registrado con otro operador. Por favor, verifica el dato.",
            "warning",
        )
    except SQLAlchemyError:
        db.session.rollback()
        flash("No pudimos guardar los cambios. Revisa los datos e inténtalo de nuevo.", "error")

    return redirect(url_for("operadores"))

@app.route("/eliminar_operador/<int:id_operador>", methods=["POST"])
@roles_requeridos('Administrador')
def eliminar_operador(id_operador):
    operador = Operador.query.get_or_404(id_operador)
    try:
        db.session.delete(operador)
        db.session.commit()
        flash("El operador ha sido dado de baja del sistema.", "info")
    except SQLAlchemyError:
        db.session.rollback()
        flash("No pudimos dar de baja al operador porque aún está relacionado con otros registros.", "error")

    return redirect(url_for("operadores"))

@app.route("/unidades")
@login_requerido
def unidades():
    lista_unidades = Unidad.query.all()
    return render_template("unidades.html", unidades=lista_unidades)

@app.route("/nueva_unidad", methods=["GET", "POST"])
@app.route("/nueva-unidad", methods=["GET", "POST"])
@roles_requeridos('Administrador')
def nueva_unidad():
    if request.method == "POST":
        numero_economico = (request.form.get("numero_economico") or "").strip()
        placas = (request.form.get("placas") or "").strip()
        if (
            Unidad.query.filter_by(placas=placas).first()
            or Unidad.query.filter_by(numero_economico=numero_economico).first()
        ):
            flash(
                "Las placas o número económico ingresados ya pertenecen a otra unidad registrada. Verifica los datos.",
                "warning",
            )
            return redirect(url_for("nueva_unidad"))

        try:
            capacidad_form = (request.form.get("capacidad") or "").strip()
            capacidad = Decimal(capacidad_form) if capacidad_form else None
            unidad = Unidad(
                numero_economico=numero_economico,
                placas=placas,
                marca=request.form.get("marca"),
                modelo=request.form.get("modelo"),
                capacidad=capacidad,
                ubicacion_actual=request.form.get("ubicacion_actual"),
                estado=request.form.get("estado") or "DISPONIBLE",
            )
            db.session.add(unidad)
            db.session.commit()
            flash("¡Listo! La unidad se registró correctamente.", "success")
        except IntegrityError:
            db.session.rollback()
            flash(
                "Las placas o número económico ingresados ya pertenecen a otra unidad registrada. Verifica los datos.",
                "warning",
            )
            return redirect(url_for("nueva_unidad"))
        except (InvalidOperation, ValueError):
            db.session.rollback()
            flash("Revisa la capacidad de la unidad; debe ser un número válido.", "error")
            return redirect(url_for("nueva_unidad"))
        except SQLAlchemyError:
            db.session.rollback()
            flash("No pudimos guardar la unidad. Revisa los datos e inténtalo de nuevo.", "error")
            return redirect(url_for("nueva_unidad"))

        return redirect(url_for("unidades"))

    return render_template("nuevo_unidad.html")

@app.route("/editar_unidad/<int:id_unidad>", methods=["POST"])
@roles_requeridos('Administrador')
def editar_unidad(id_unidad):
    unidad = Unidad.query.get_or_404(id_unidad)
    numero_economico = (request.form.get("numero_economico") or "").strip()
    placas = (request.form.get("placas") or "").strip()
    if not numero_economico or not placas:
        flash("Completa el número económico y las placas para guardar los cambios.", "error")
        return redirect(url_for("unidades"))

    capacidad_form = request.form.get("capacidad", "").strip()
    try:
        capacidad = Decimal(capacidad_form) if capacidad_form else None
        unidad.numero_economico = numero_economico
        unidad.placas = placas
        unidad.marca = request.form.get("marca") or None
        unidad.modelo = request.form.get("modelo") or None
        unidad.capacidad = capacidad
        unidad.ubicacion_actual = request.form.get("ubicacion_actual") or None
        unidad.estado = request.form.get("estado") or unidad.estado
        db.session.commit()
        flash("Los datos de la unidad se actualizaron correctamente.", "success")
    except (InvalidOperation, ValueError):
        db.session.rollback()
        flash("Revisa la capacidad de la unidad e inténtalo de nuevo.", "error")
    except SQLAlchemyError:
        db.session.rollback()
        flash("No pudimos guardar los cambios de la unidad. Verifica que el número económico y las placas no estén repetidos.", "error")

    return redirect(url_for("unidades"))

@app.route("/eliminar_unidad/<int:id_unidad>", methods=["POST"])
@roles_requeridos('Administrador')
def eliminar_unidad(id_unidad):
    unidad = Unidad.query.get_or_404(id_unidad)
    try:
        db.session.delete(unidad)
        db.session.commit()
        flash("La unidad ha sido dada de baja del sistema.", "info")
    except SQLAlchemyError:
        db.session.rollback()
        flash("No pudimos eliminar la unidad porque aún está relacionada con otras asignaciones.", "error")

    return redirect(url_for("unidades"))

@app.route("/asignaciones")
@login_requerido
def asignaciones():
    lista_asignaciones = Asignacion.query.all()
    return render_template("asignaciones.html", asignaciones=lista_asignaciones)

@app.route("/nueva_asignacion", methods=["GET", "POST"])
@app.route("/nueva-asignacion", methods=["GET", "POST"])
@roles_requeridos('Administrador', 'Editor')
def nueva_asignacion():
    pedidos = Pedido.query.order_by(Pedido.folio).all()
    operadores = Operador.query.filter_by(disponibilidad=True).order_by(Operador.nombre).all()
    unidades = Unidad.query.filter(
        db.func.upper(db.func.trim(Unidad.estado)) == "DISPONIBLE"
    ).order_by(Unidad.numero_economico).all()

    if request.method == "POST":
        id_pedido_form = (request.form.get("id_pedido") or "").strip()
        id_operador_form = (request.form.get("id_operador") or "").strip()
        id_unidad_form = (request.form.get("id_unidad") or "").strip()
        fecha_asignacion_form = (request.form.get("fecha_asignacion") or "").strip()

        if not all((id_pedido_form, id_operador_form, id_unidad_form, fecha_asignacion_form)):
            flash(
                "Para continuar, elige un pedido, un operador, una unidad y la fecha de asignación.",
                "warning",
            )
            return render_template(
                "nueva_asignacion.html",
                pedidos=pedidos,
                operadores=operadores,
                unidades=unidades,
            )

        try:
            id_pedido = int(id_pedido_form)
            id_operador = int(id_operador_form)
            id_unidad = int(id_unidad_form)
            pedido_valido = Pedido.query.filter_by(id_pedido=id_pedido).first()
            operador_valido = Operador.query.filter_by(
                id_operador=id_operador,
                disponibilidad=True,
            ).first()
            unidad_valida = Unidad.query.filter(
                Unidad.id_unidad == id_unidad,
                db.func.upper(db.func.trim(Unidad.estado)) == "DISPONIBLE",
            ).first()
            if not pedido_valido or not operador_valido or not unidad_valida:
                flash(
                    "Alguna de las opciones ya no está disponible. Actualiza la página y vuelve a elegir.",
                    "warning",
                )
                return render_template(
                    "nueva_asignacion.html",
                    pedidos=pedidos,
                    operadores=operadores,
                    unidades=unidades,
                )

            asignacion = Asignacion(
                id_pedido=id_pedido,
                id_operador=id_operador,
                id_unidad=id_unidad,
                fecha_asignacion=datetime.fromisoformat(fecha_asignacion_form),
                fecha_inicio=datetime.fromisoformat(request.form["fecha_inicio"]) if request.form.get("fecha_inicio") else None,
                fecha_fin=datetime.fromisoformat(request.form["fecha_fin"]) if request.form.get("fecha_fin") else None,
                estado=(request.form.get("estado") or "ASIGNADA").strip(),
            )
            db.session.add(asignacion)
            db.session.commit()
            flash("¡Viaje despachado correctamente!", "success")
        except (TypeError, ValueError):
            db.session.rollback()
            flash("Revisa los datos del viaje y selecciona fechas válidas antes de guardar.", "error")
            return render_template(
                "nueva_asignacion.html",
                pedidos=pedidos,
                operadores=operadores,
                unidades=unidades,
            )
        except SQLAlchemyError:
            db.session.rollback()
            flash("No pudimos guardar la asignación. Revisa que el pedido, operador y unidad sigan disponibles.", "error")
            return render_template(
                "nueva_asignacion.html",
                pedidos=pedidos,
                operadores=operadores,
                unidades=unidades,
            )
        return redirect(url_for("asignaciones"))

    return render_template("nueva_asignacion.html", pedidos=pedidos, operadores=operadores, unidades=unidades)

@app.route("/editar_asignacion/<int:id>", methods=["GET", "POST"])
@roles_requeridos('Administrador', 'Editor')
def editar_asignacion(id):
    asignacion = Asignacion.query.get_or_404(id)
    pedidos = Pedido.query.order_by(Pedido.folio).all()
    operadores = Operador.query.filter(
        (Operador.disponibilidad.is_(True)) | (Operador.id_operador == asignacion.id_operador)
    ).order_by(Operador.nombre).all()
    unidades = Unidad.query.filter(
        (db.func.upper(db.func.trim(Unidad.estado)) == "DISPONIBLE")
        | (Unidad.id_unidad == asignacion.id_unidad)
    ).order_by(Unidad.numero_economico).all()

    if request.method == "POST":
        try:
            asignacion.id_pedido = int(request.form.get("id_pedido", ""))
            asignacion.id_operador = int(request.form.get("id_operador", ""))
            asignacion.id_unidad = int(request.form.get("id_unidad", ""))
            asignacion.fecha_asignacion = datetime.fromisoformat(request.form.get("fecha_asignacion", ""))
            asignacion.fecha_inicio = datetime.fromisoformat(request.form["fecha_inicio"]) if request.form.get("fecha_inicio") else None
            asignacion.fecha_fin = datetime.fromisoformat(request.form["fecha_fin"]) if request.form.get("fecha_fin") else None
            asignacion.estado = (request.form.get("estado") or "ASIGNADA").strip()
            db.session.commit()
            flash("Los datos de la asignación se actualizaron correctamente.", "success")
            return redirect(url_for("asignaciones"))
        except (TypeError, ValueError):
            db.session.rollback()
            flash("Revisa los datos del viaje y selecciona fechas válidas antes de guardar.", "error")
        except SQLAlchemyError:
            db.session.rollback()
            flash("No pudimos actualizar la asignación. Inténtalo de nuevo.", "error")

    return render_template(
        "nueva_asignacion.html",
        asignacion=asignacion,
        pedidos=pedidos,
        operadores=operadores,
        unidades=unidades,
    )

@app.route("/eliminar_asignacion/<int:id>", methods=["POST"])
@roles_requeridos('Administrador', 'Editor')
def eliminar_asignacion(id):
    asignacion = Asignacion.query.get_or_404(id)
    try:
        db.session.delete(asignacion)
        db.session.commit()
        flash("La asignación se eliminó correctamente.", "info")
    except SQLAlchemyError:
        db.session.rollback()
        flash("No pudimos eliminar la asignación porque sigue relacionada con otros registros.", "error")

    return redirect(url_for("asignaciones"))

@app.route("/seguimiento")
@login_requerido
def seguimiento():
    lista_seguimientos = Seguimiento.query.all()
    asignaciones_activas = Asignacion.query.filter(
        Asignacion.estado.in_(("ASIGNADA", "EN CURSO"))
    ).all()
    seguimientos_recientes = (
        Seguimiento.query
        .filter(Seguimiento.id_pedido.in_([a.id_pedido for a in asignaciones_activas]))
        .order_by(Seguimiento.fecha_hora.desc())
        .all()
    ) if asignaciones_activas else []
    seguimiento_por_pedido = {}
    for seguimiento_actual in seguimientos_recientes:
        seguimiento_por_pedido.setdefault(seguimiento_actual.id_pedido, seguimiento_actual)

    coordenadas_demo = (
        (25.6866, -100.3161),
        (19.4326, -99.1332),
        (20.6597, -103.3496),
        (25.5428, -103.4068),
        (21.1619, -86.8515),
        (29.0729, -110.9559),
    )
    mapa_unidades = []
    for asignacion in asignaciones_activas:
        seguimiento_actual = seguimiento_por_pedido.get(asignacion.id_pedido)
        estado_reportado = (
            seguimiento_actual.estatus if seguimiento_actual and seguimiento_actual.estatus
            else asignacion.estado
        ).strip().lower()
        if any(palabra in estado_reportado for palabra in ("deten", "parad", "paus")):
            estado_mapa = "Detenida"
        elif any(palabra in estado_reportado for palabra in ("retras", "demor")):
            estado_mapa = "Retraso"
        else:
            estado_mapa = "En ruta"

        lat, lng = coordenadas_demo[(asignacion.id_unidad - 1) % len(coordenadas_demo)]
        mapa_unidades.append({
            "id_unidad": asignacion.id_unidad,
            "numero_economico": asignacion.unidad.numero_economico,
            "operador": asignacion.operador.nombre,
            "destino": asignacion.pedido.destino,
            "estado": estado_mapa,
            "lat": lat,
            "lng": lng,
        })

    return render_template(
        "seguimiento.html",
        seguimientos=lista_seguimientos,
        asignaciones_activas=asignaciones_activas,
        mapa_unidades=mapa_unidades,
        unidades_ruta=len(asignaciones_activas),
        entregas_tiempo=0,
        retrasos=0,
        incidencias_activas=0,
    )

@app.route("/incidencias")
@login_requerido
def incidencias():
    lista_incidencias = Incidencia.query.all()
    return render_template("incidencias.html", incidencias=lista_incidencias)

@app.route("/nueva_incidencia", methods=["GET", "POST"])
@app.route("/nueva-incidencia", methods=["GET", "POST"])
@roles_requeridos('Administrador', 'Editor')
def nueva_incidencia():
    pedidos = Pedido.query.order_by(Pedido.folio).all()
    if request.method == "POST":
        id_pedido_form = (request.form.get("id_pedido") or "").strip()
        tipo = (request.form.get("tipo") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip()
        fecha_form = (request.form.get("fecha_hora") or "").strip()

        if not id_pedido_form:
            flash("Selecciona el pedido relacionado con esta incidencia.", "warning")
            return render_template("nueva_incidencia.html", pedidos=pedidos, datos_incidencia=request.form)
        if not tipo:
            flash("Cuéntanos qué tipo de problema ocurrió para continuar.", "warning")
            return render_template("nueva_incidencia.html", pedidos=pedidos, datos_incidencia=request.form)
        if not descripcion:
            flash("Agrega una breve descripción de lo que ocurrió.", "warning")
            return render_template("nueva_incidencia.html", pedidos=pedidos, datos_incidencia=request.form)
        if not fecha_form:
            flash("Indica la fecha y hora en que ocurrió la incidencia.", "warning")
            return render_template("nueva_incidencia.html", pedidos=pedidos, datos_incidencia=request.form)

        try:
            id_pedido = int(id_pedido_form)
            pedido = Pedido.query.filter_by(id_pedido=id_pedido).first()
            if pedido is None:
                flash("El pedido seleccionado ya no está disponible. Elige otro de la lista.", "warning")
                return render_template("nueva_incidencia.html", pedidos=pedidos, datos_incidencia=request.form)

            incidencia = Incidencia(
                id_pedido=id_pedido,
                tipo=tipo,
                descripcion=descripcion,
                fecha_hora=datetime.fromisoformat(fecha_form),
                estado=(request.form.get("estado") or "ABIERTA").strip(),
                solucion=(request.form.get("solucion") or "").strip() or None,
            )
            db.session.add(incidencia)
            db.session.commit()
            flash("El reporte se ha guardado correctamente.", "success")
        except (TypeError, ValueError):
            db.session.rollback()
            flash("Revisa la fecha y el pedido seleccionado; alguno de esos datos no parece correcto.", "warning")
            return render_template("nueva_incidencia.html", pedidos=pedidos, datos_incidencia=request.form)
        except SQLAlchemyError:
            db.session.rollback()
            flash("No pudimos guardar el reporte. Revisa la información e inténtalo de nuevo.", "error")
            return render_template("nueva_incidencia.html", pedidos=pedidos, datos_incidencia=request.form)
        return redirect(url_for("incidencias"))

    return render_template("nueva_incidencia.html", pedidos=pedidos)

@app.route("/editar_incidencia/<int:id>", methods=["GET", "POST"])
@roles_requeridos('Administrador', 'Editor')
def editar_incidencia(id):
    incidencia = Incidencia.query.get_or_404(id)
    pedidos = Pedido.query.order_by(Pedido.folio).all()

    if request.method == "POST":
        try:
            id_pedido_form = (request.form.get("id_pedido") or "").strip()
            tipo = (request.form.get("tipo") or "").strip()
            descripcion = (request.form.get("descripcion") or "").strip()
            fecha_form = (request.form.get("fecha_hora") or "").strip()
            if not id_pedido_form:
                flash("Selecciona el pedido relacionado con esta incidencia.", "warning")
                return render_template("nueva_incidencia.html", incidencia=incidencia, pedidos=pedidos, datos_incidencia=request.form)
            if not tipo:
                flash("Cuéntanos qué tipo de problema ocurrió para continuar.", "warning")
                return render_template("nueva_incidencia.html", incidencia=incidencia, pedidos=pedidos, datos_incidencia=request.form)
            if not descripcion:
                flash("Agrega una breve descripción de lo que ocurrió.", "warning")
                return render_template("nueva_incidencia.html", incidencia=incidencia, pedidos=pedidos, datos_incidencia=request.form)
            if not fecha_form:
                flash("Indica la fecha y hora en que ocurrió la incidencia.", "warning")
                return render_template("nueva_incidencia.html", incidencia=incidencia, pedidos=pedidos, datos_incidencia=request.form)

            incidencia.id_pedido = int(id_pedido_form)
            if Pedido.query.filter_by(id_pedido=incidencia.id_pedido).first() is None:
                flash("El pedido seleccionado ya no está disponible. Elige otro de la lista.", "warning")
                return render_template("nueva_incidencia.html", incidencia=incidencia, pedidos=pedidos, datos_incidencia=request.form)
            incidencia.tipo = tipo
            incidencia.descripcion = descripcion
            incidencia.fecha_hora = datetime.fromisoformat(fecha_form)
            incidencia.estado = (request.form.get("estado") or "ABIERTA").strip()
            incidencia.solucion = (request.form.get("solucion") or "").strip() or None
            db.session.commit()
            flash("El reporte se ha actualizado correctamente.", "success")
            return redirect(url_for("incidencias"))
        except (TypeError, ValueError):
            db.session.rollback()
            flash("Revisa la fecha y el pedido seleccionado; alguno de esos datos no parece correcto.", "warning")
        except SQLAlchemyError:
            db.session.rollback()
            flash("No pudimos actualizar el reporte. Revisa la información e inténtalo de nuevo.", "error")

    return render_template(
        "nueva_incidencia.html",
        incidencia=incidencia,
        pedidos=pedidos,
        datos_incidencia=request.form if request.method == "POST" else None,
    )

@app.route("/eliminar_incidencia/<int:id>", methods=["POST"])
@roles_requeridos('Administrador', 'Editor')
def eliminar_incidencia(id):
    incidencia = Incidencia.query.get_or_404(id)
    try:
        db.session.delete(incidencia)
        db.session.commit()
        flash("El reporte se eliminó correctamente.", "info")
    except SQLAlchemyError:
        db.session.rollback()
        flash("No pudimos eliminar el reporte porque sigue relacionado con otros registros.", "error")

    return redirect(url_for("incidencias"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)