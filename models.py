from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Cliente(db.Model):
    __tablename__ = "clientes"

    id_cliente = db.Column(db.Integer, primary_key=True)
    razon_social = db.Column(db.String(150), nullable=False)
    rfc = db.Column(db.String(13))
    nombre_contacto = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(120))
    direccion = db.Column(db.String(255))
    pais = db.Column(db.String(60), default="México")
    estado = db.Column(db.String(60))


class TipoServicio(db.Model):
    __tablename__ = "tipos_servicio"

    id_tipo_servicio = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    requiere_cruce = db.Column(db.Boolean, default=False)
    tarifa_base = db.Column(db.Numeric(10, 2), default=0.00)
    activo = db.Column(db.Boolean, default=True)


class Operador(db.Model):
    __tablename__ = "operadores"

    id_operador = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20))
    numero_licencia = db.Column(db.String(50), nullable=False, unique=True)
    tipo_licencia = db.Column(db.String(50))
    vigencia_licencia = db.Column(db.Date)
    disponibilidad = db.Column(db.Boolean, default=True)
    horas_servicio = db.Column(db.Numeric(5, 2), default=0.00)


class Unidad(db.Model):
    __tablename__ = "unidades"

    id_unidad = db.Column(db.Integer, primary_key=True)
    numero_economico = db.Column(db.String(30), nullable=False, unique=True)
    placas = db.Column(db.String(20), nullable=False, unique=True)
    marca = db.Column(db.String(60))
    modelo = db.Column(db.String(60))
    capacidad = db.Column(db.Numeric(10, 2))
    ubicacion_actual = db.Column(db.String(150))
    estado = db.Column(db.String(30), default="DISPONIBLE")


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

    folio = db.Column(db.String(50), nullable=False, unique=True)
    origen = db.Column(db.String(150), nullable=False)
    destino = db.Column(db.String(150), nullable=False)
    mercancia = db.Column(db.String(255))
    tarifa = db.Column(db.Numeric(10, 2))
    fecha_estimada = db.Column(db.DateTime)
    estado = db.Column(db.String(30), default="REGISTRADO")


class Asignacion(db.Model):
    __tablename__ = "asignaciones"

    id_asignacion = db.Column(db.Integer, primary_key=True)

    id_pedido = db.Column(
        db.Integer,
        db.ForeignKey("pedidos.id_pedido"),
        nullable=False
    )

    id_operador = db.Column(
        db.Integer,
        db.ForeignKey("operadores.id_operador"),
        nullable=False
    )

    id_unidad = db.Column(
        db.Integer,
        db.ForeignKey("unidades.id_unidad"),
        nullable=False
    )

    fecha_asignacion = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )
    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)
    estado = db.Column(db.String(30), default="ASIGNADA")


class Seguimiento(db.Model):
    __tablename__ = "seguimientos"

    id_seguimiento = db.Column(db.Integer, primary_key=True)

    id_pedido = db.Column(
        db.Integer,
        db.ForeignKey("pedidos.id_pedido"),
        nullable=False
    )

    fecha_hora = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )
    ubicacion = db.Column(db.String(150))
    estatus = db.Column(db.String(50))
    eta = db.Column(db.DateTime)
    observaciones = db.Column(db.String(255))


class Incidencia(db.Model):
    __tablename__ = "incidencias"

    id_incidencia = db.Column(db.Integer, primary_key=True)

    id_pedido = db.Column(
        db.Integer,
        db.ForeignKey("pedidos.id_pedido"),
        nullable=False
    )

    tipo = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    fecha_hora = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )
    estado = db.Column(db.String(30), default="ABIERTA")
    solucion = db.Column(db.String(255))