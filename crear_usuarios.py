from app import app
from models import db, Usuario
from werkzeug.security import generate_password_hash

with app.app_context():

    editor = Usuario(
        nombre="Editor",
        usuario="2066273",

        contrasena=generate_password_hash("6oTfUDE512@"),
        rol="Editor"
    )

    
    usuario_normal = Usuario(
        nombre="",
        usuario="comun3!",
        contrasena=generate_password_hash("2143@!"), 
        rol="Usuario"
    )


    db.session.add(editor)
    db.session.add(usuario_normal)
    db.session.commit()

    print("")