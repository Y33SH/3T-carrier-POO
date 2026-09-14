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

    pedidos_activos = Pedido.query.filter(
        Pedido.estado.in_(["REGISTRADO", "EN TRANSITO"])
    ).count()

    unidades_disponibles = Unidad.query.filter_by(
        estado="DISPONIBLE"
    ).count()

    operadores_disponibles = Operador.query.filter_by(
        disponibilidad=True
    ).count()

    incidencias_abiertas = Incidencia.query.filter(
        Incidencia.estado != "RESUELTA"
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

    lista_clientes = Cliente.query.order_by(
        Cliente.id_cliente.desc()
    ).all()

    return render_template(
        "clientes.html",
        clientes=lista_clientes
    )


if __name__ == "__main__":
    app.run(debug=True)