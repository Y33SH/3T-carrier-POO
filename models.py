from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class ModeloBase(db.Model):
    __abstract__ = True

    @property
    def id(self):
        primary_key = self.__mapper__.primary_key[0]
        return getattr(self, primary_key.name)

    def obtener_resumen(self):
        return f"{type(self).__name__} #{self.id}"


class Usuario(ModeloBase):
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellidos = db.Column(db.String(100))
    usuario = db.Column(db.String(50), nullable=False, unique=True)
    _contrasena = db.Column("contrasena", db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='usuario') # Ej. 'Administrador', 'Editor', 'Consultor'
    id_cliente = db.Column(db.Integer, db.ForeignKey("clientes.id_cliente"), nullable=True)
    cliente = db.relationship("Cliente")
    estado = db.Column(db.String(20), default="ACTIVO")
    fecha_registro = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    @property
    def password(self):
        return self._contrasena

    @password.setter
    def password(self, password):
        self._contrasena = generate_password_hash(password)

    def set_password(self, password):
        self.password = password

    def verificar_password(self, password):
        return check_password_hash(self._contrasena, password)

    def obtener_resumen(self):
        return f"Usuario: {self.usuario} | Rol: {self.rol or 'Sin rol'}"


class Cliente(ModeloBase):
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


class TipoServicio(ModeloBase):
    __tablename__ = "tipos_servicio"

    id_tipo_servicio = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    requiere_cruce = db.Column(db.Boolean, default=False)
    tarifa_base = db.Column(db.Numeric(10, 2), default=0.00)
    activo = db.Column(db.Boolean, default=True)


class Operador(ModeloBase):
    __tablename__ = "operadores"

    id_operador = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20))
    numero_licencia = db.Column(db.String(50), nullable=False, unique=True)
    tipo_licencia = db.Column(db.String(50))
    vigencia_licencia = db.Column(db.Date)
    disponibilidad = db.Column(db.Boolean, default=True)
    horas_servicio = db.Column(db.Numeric(5, 2), default=0.00)


class Unidad(ModeloBase):
    __tablename__ = "unidades"

    id_unidad = db.Column(db.Integer, primary_key=True)
    numero_economico = db.Column(db.String(30), nullable=False, unique=True)
    placas = db.Column(db.String(20), nullable=False, unique=True)
    marca = db.Column(db.String(60))
    modelo = db.Column(db.String(60))
    capacidad = db.Column(db.Numeric(10, 2))
    ubicacion_actual = db.Column(db.String(150))
    estado = db.Column(db.String(30), default="DISPONIBLE")


class Pedido(ModeloBase):
    __tablename__ = "pedidos"

    id_pedido = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("clientes.id_cliente"), nullable=False)
    id_tipo_servicio = db.Column(db.Integer, db.ForeignKey("tipos_servicio.id_tipo_servicio"), nullable=False)
    folio = db.Column(db.String(50), nullable=False, unique=True)
    origen = db.Column(db.String(150), nullable=False)
    destino = db.Column(db.String(150), nullable=False)
    mercancia = db.Column(db.String(255))
    tarifa = db.Column(db.Numeric(10, 2))
    fecha_estimada = db.Column(db.DateTime)
    estado = db.Column(db.String(30), default="REGISTRADO")
    cliente = db.relationship("Cliente")
    tipo_servicio = db.relationship("TipoServicio")

    def obtener_resumen(self):
        folio = self.folio or f"#{self.id_pedido}"
        estado = self.estado or "Sin estado"
        return f"Pedido {folio} | Estado: {estado}"


class Asignacion(ModeloBase):
    __tablename__ = "asignaciones"

    id_asignacion = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedidos.id_pedido"), nullable=False)
    id_operador = db.Column(db.Integer, db.ForeignKey("operadores.id_operador"), nullable=False)
    id_unidad = db.Column(db.Integer, db.ForeignKey("unidades.id_unidad"), nullable=False)
    pedido = db.relationship("Pedido")
    operador = db.relationship("Operador")
    unidad = db.relationship("Unidad")
    fecha_asignacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)
    estado = db.Column(db.String(30), default="ASIGNADA")


class Seguimiento(ModeloBase):
    __tablename__ = "seguimientos"

    id_seguimiento = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedidos.id_pedido"), nullable=False)
    fecha_hora = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    ubicacion = db.Column(db.String(150))
    estatus = db.Column(db.String(50))
    eta = db.Column(db.DateTime)
    observaciones = db.Column(db.String(255))


class Incidencia(ModeloBase):
    __tablename__ = "incidencias"

    id_incidencia = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedidos.id_pedido"), nullable=False)
    tipo = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    fecha_hora = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    estado = db.Column(db.String(30), default="ABIERTA")
    solucion = db.Column(db.String(255))

    def obtener_resumen(self):
        return (
            f"Incidencia #{self.id_incidencia} | {self.tipo} | "
            f"Estado: {self.estado or 'Sin estado'}"
        )
