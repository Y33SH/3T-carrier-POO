from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate

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
    Incidencia
)

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/dashboard")
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
        incidencias_abiertas=incidencias_abiertas
    )


@app.route("/clientes")
def clientes():

    lista_clientes = Cliente.query.all()

    return render_template(
        "clientes.html",
        clientes=lista_clientes
    )


@app.route("/nuevo-cliente", methods=["GET", "POST"])
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
def pedidos():
    lista_pedidos = Pedido.query.all()

    return render_template(
        "pedidos.html",
        pedidos=lista_pedidos
    )

@app.route("/nuevo-pedido")
def nuevo_pedido():

    clientes = Cliente.query.all()
    servicios = TipoServicio.query.all()

    return render_template(
        "nuevo_pedido.html",
        clientes=clientes,
        servicios=servicios
    )

@app.route("/operadores")
def operadores():
    lista_operadores = Operador.query.all()

    return render_template(
        "operadores.html",
        operadores=lista_operadores
    )

@app.route("/unidades")
def unidades():
    lista_unidades = Unidad.query.all()

    return render_template(
        "unidades.html",
        unidades=lista_unidades
    )
@app.route("/nueva-unidad", methods=["GET", "POST"])
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
def asignaciones():
    lista_asignaciones = Asignacion.query.all()

    return render_template(
        "asignaciones.html",
        asignaciones=lista_asignaciones
    )
@app.route("/nueva-asignacion", methods=["GET", "POST"])
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

    return render_template(
        "nueva_asignacion.html",
        pedidos=pedidos,
        operadores=operadores,
        unidades=unidades
    )


@app.route("/seguimiento")
def seguimiento():

    lista_seguimientos = Seguimiento.query.all()

    return render_template(
        "seguimiento.html",
        seguimientos=lista_seguimientos,
        unidades_ruta=0,
        entregas_tiempo=0,
        retrasos=0,
        incidencias_activas=0
    )

@app.route("/incidencias")
def incidencias():

    lista_incidencias = Incidencia.query.all()

    return render_template(
        "incidencias.html",
        incidencias=lista_incidencias
    )

@app.route("/nueva-incidencia", methods=["GET", "POST"])
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

    return render_template(
        "nueva_incidencia.html",
        pedidos=pedidos
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)