from flask import Flask, render_template
from flask_migrate import Migrate

from config import Config
from models import (
    db,
    Cliente,
    Pedido,
    Unidad,
    Operador,
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

    pedidos_activos = 0
    unidades_disponibles = 0
    operadores_disponibles = 0
    incidencias_abiertas = 0

    return render_template(
        "dashboard.html",
        pedidos_activos=pedidos_activos,
        unidades_disponibles=unidades_disponibles,
        operadores_disponibles=operadores_disponibles,
        incidencias_abiertas=incidencias_abiertas
    )


@app.route("/clientes")
def clientes():

    lista_clientes = []

    return render_template(
        "clientes.html",
        clientes=lista_clientes
    )


@app.route("/nuevo-cliente")
def nuevo_cliente():
    return render_template("nuevo_cliente.html")


@app.route("/pedidos")
def pedidos():
    lista_pedidos = []
    return render_template("pedidos.html", pedidos=lista_pedidos)

@app.route("/nuevo-pedido")
def nuevo_pedido():

    clientes = []
    servicios = []

    return render_template(
        "nuevo_pedido.html",
        clientes=clientes,
        servicios=servicios
    )

@app.route("/operadores")
def operadores():
    lista_operadores = []
    return render_template("operadores.html", operadores=lista_operadores)


@app.route("/unidades")
def unidades():
    lista_unidades = []
    return render_template("unidades.html", unidades=lista_unidades)

@app.route("/nueva-unidad")
def nueva_unidad():
    return render_template("nuevo_unidad.html")


@app.route("/asignaciones")
def asignaciones():
    lista_asignaciones = []
    return render_template(
        "asignaciones.html",
        asignaciones=lista_asignaciones
    )

@app.route("/nueva-asignacion")
def nueva_asignacion():

    pedidos = []
    operadores = []
    unidades = []

    return render_template(
        "nueva_asignacion.html",
        pedidos=pedidos,
        operadores=operadores,
        unidades=unidades
    )


@app.route("/seguimiento")
def seguimiento():

    lista_seguimientos = []

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

    lista_incidencias = []

    return render_template(
        "incidencias.html",
        incidencias=lista_incidencias
    )

@app.route("/nueva-incidencia")
def nueva_incidencia():
    pedidos = []

    return render_template(
        "nueva_incidencia.html",
        pedidos=pedidos
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)