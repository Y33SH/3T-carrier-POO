from app import app
from models import db, Usuario

with app.app_context():

    editor = Usuario(
        nombre="Editor",
        usuario="2066273",

        password="6oTfUDE512@",
        rol="Editor"
    )

    
    usuario_normal = Usuario(
        nombre="",
        usuario="comun3!",
        password="2143@!",
        rol="Usuario"
    )


    db.session.add(editor)
    db.session.add(usuario_normal)
    db.session.commit()

    print("")