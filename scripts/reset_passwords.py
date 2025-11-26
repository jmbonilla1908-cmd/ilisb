import os
import sys

# Añade el directorio raíz del proyecto al path de Python
# para que podamos importar 'app' y sus modelos.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import create_app, db
from app.auth.models import Alumno

# Lista de correos electrónicos de los usuarios a actualizar
emails_to_update = [
    "mad8827@gmail.com",
    "madeleine.buenano.b@gmail.com",
    "ilisb.institute@gmail.com",
    "madeleine.b.b@outlook.com",
    "m_ade12@hotmail.com",
    "sersup.peru@gmail.com",
    "logistica.sersup@gmail.com"
]

# La nueva contraseña que se asignará a todos
new_password = "9QCJjw2g1980gMz"

# Crea una instancia de la aplicación Flask para tener el contexto correcto
app = create_app(os.getenv('FLASK_CONFIG') or 'development')

with app.app_context():
    print("--- Iniciando script de reseteo de contraseñas ---")
    for email in emails_to_update:
        alumno = Alumno.query.filter_by(email=email).first()
        if alumno:
            alumno.set_password(new_password)
            print(f"[ÉXITO] Contraseña actualizada para: {email} (ID: {alumno.id})")
        else:
            print(f"[ERROR] No se encontró al alumno con email: {email}")

    # Guarda todos los cambios en la base de datos
    db.session.commit()
    print("--- Proceso finalizado. Cambios guardados en la base de datos. ---")