from app import app
from models import db, Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    # 1. Crear usuario con rol de Editor
    editor = Usuario(
        nombre="Editor",
        usuario="2066273",
        # Si NO estás encriptando contraseñas, déjalo así: contrasena="12345"
        # Si SÍ estás encriptando (hash), usa la línea de abajo:
        contrasena=generate_password_hash("6oTfUDE512@"),
        rol="Editor"
    )

    # 2. Crear usuario con rol de Usuario (Consultor)
    usuario_normal = Usuario(
        nombre="",
        usuario="comun3!",
        contrasena=generate_password_hash("2143@!"), # Aplica la misma regla de arriba
        rol="Usuario"
    )

    # Agregarlos a la base de datos
    db.session.add(editor)
    db.session.add(usuario_normal)
    db.session.commit()

    print("¡Usuarios de prueba creados exitosamente en Aiven!")