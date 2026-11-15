from app import app
from models import db, Usuario

with app.app_context():
    
    admin = Usuario(
        nombre="Yeshua",
        apellidos="Administrador",
        usuario="yeshua_3t",
        rol="Administrador",
    )
    admin.set_password("3T_Carrier_YGF26!")
    

    editor = Usuario(
        nombre="Editor",
        apellidos="Logistica",
        usuario="2066273",
        rol="Editor",
    )
    editor.set_password("6oTfUDE512@")
    
  
    usuario_normal = Usuario(
        nombre="Cliente",
        apellidos="Prueba",
        usuario="comun3!",
        rol="Consultor",
    )
    usuario_normal.set_password("2143@!")

    db.session.add(admin)
    db.session.add(editor)
    db.session.add(usuario_normal)
    db.session.commit()
