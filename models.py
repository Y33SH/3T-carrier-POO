from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Cliente(db.Model):
    __tablename__ = "clientes"

    id_cliente = db.Column(db.Integer, primary_key=True)
    razon_social = db.Column(db.String(150), nullable=False)
    nombre_contacto = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(30))
    correo = db.Column(db.String(150), index=True)
    direccion = db.Column(db.String(255))
    pais = db.Column(db.String(80))
    estado = db.Column(db.String(80))


class TipoServicio(db.Model):
    __tablename__ = "tipos_servicio"

    id_tipo_servicio = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))
    requiere_cruce = db.Column(db.Boolean, default=False)
    tarifa_base = db.Column(db.Numeric(10, 2), nullable=False)
    activo = db.Column(db.Boolean, default=True)


class Operador(db.Model):
    __tablename__ = "operadores"

    id_operador = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(30))
    numero_licencia = db.Column(db.String(100), unique=True, nullable=False)
    tipo_licencia = db.Column(db.String(50))
    vigencia_licencia = db.Column(db.Date)
    disponibilidad = db.Column(db.Boolean, default=True)
    horas_servicio = db.Column(db.Integer, default=0)


class Unidad(db.Model):
    __tablename__ = "unidades"

    id_unidad = db.Column(db.Integer, primary_key=True)
    numero_economico = db.Column(db.String(50), unique=True, nullable=False)
    placas = db.Column(db.String(30), unique=True, nullable=False)
    marca = db.Column(db.String(80))
    modelo = db.Column(db.String(80))
    capacidad = db.Column(db.Numeric(10, 2))
    ubicacion_actual = db.Column(db.String(150))
    estado = db.Column(db.String(50), index=True)


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id_pedido = db.Column(db.Integer, primary_key=True)

    id_cliente = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id_cliente"),
        nullable=False
    )

    id_tipo_servicio = db.Column(
        db.Integer,
        db.ForeignKey("tipos_servicio.id_tipo_servicio"),
        nullable=False
    )

    folio = db.Column(db.String(50), unique=True, nullable=False)
    origen = db.Column(db.String(150), nullable=False)
    destino = db.Column(db.String(150), nullable=False)
    mercancia = db.Column(db.String(255))
    tarifa = db.Column(db.Numeric(10, 2))
    fecha_estimada = db.Column(db.DateTime)
    estado = db.Column(db.String(50), index=True, default="REGISTRADO")


class Incidencia(db.Model):
    __tablename__ = "incidencias"

    id_incidencia = db.Column(db.Integer, primary_key=True)

    id_pedido = db.Column(
        db.Integer,
        db.ForeignKey("pedidos.id_pedido"),
        nullable=False
    )

    tipo = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    fecha_hora = db.Column(db.DateTime)
    estado = db.Column(db.String(50), index=True)
    solucion = db.Column(db.Text)