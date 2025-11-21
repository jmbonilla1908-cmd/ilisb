#!/usr/bin/env python3
"""
Script para crear un super administrador del sistema ILISB.
"""

from app import create_app, db
from app.admin.models import User
import getpass
import sys


def create_superuser():
    """Crear un super administrador interactivamente."""
    
    app = create_app()
    
    with app.app_context():
        print("=== Creación de Super Administrador ILISB ===\n")
        
        # Solicitar información del administrador
        username = input("Username: ").strip()
        if not username:
            print("❌ El username es obligatorio.")
            return False
            
        # Verificar si el username ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"❌ El username '{username}' ya existe.")
            return False
            
        email = input("Email: ").strip()
        if not email:
            print("❌ El email es obligatorio.")
            return False
            
        # Verificar si el email ya existe
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            print(f"❌ El email '{email}' ya existe.")
            return False
            
        first_name = input("Nombre: ").strip()
        if not first_name:
            print("❌ El nombre es obligatorio.")
            return False
            
        last_name = input("Apellido: ").strip()
        if not last_name:
            print("❌ El apellido es obligatorio.")
            return False
            
        # Solicitar contraseña de forma segura
        password = getpass.getpass("Contraseña: ")
        if len(password) < 6:
            print("❌ La contraseña debe tener al menos 6 caracteres.")
            return False
            
        password_confirm = getpass.getpass("Confirmar contraseña: ")
        if password != password_confirm:
            print("❌ Las contraseñas no coinciden.")
            return False
            
        try:
            # Crear el super administrador
            superuser = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_superuser=True,
                is_active=True,
                notes="Super administrador creado mediante script"
            )
            superuser.set_password(password)
            
            # Guardar en la base de datos
            db.session.add(superuser)
            db.session.commit()
            
            print(f"\n✅ Super administrador creado exitosamente!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Nombre: {first_name} {last_name}")
            print(f"   ID: {superuser.id}")
            print(f"   Superuser: ✅")
            print(f"   Activo: ✅")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear el super administrador: {e}")
            return False


def list_admins():
    """Listar todos los administradores existentes."""
    
    app = create_app()
    
    with app.app_context():
        print("=== Administradores Existentes ===\n")
        
        users = User.query.all()
        
        if not users:
            print("No hay administradores registrados.")
            return
            
        for user in users:
            status = "✅ Activo" if user.is_active else "❌ Inactivo"
            superuser = "🔥 SUPER" if user.is_superuser else "👤 Normal"
            
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Nombre: {user.full_name}")
            print(f"Tipo: {superuser}")
            print(f"Estado: {status}")
            print(f"Creado: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if user.last_login:
                print(f"Último login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 40)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_admins()
    else:
        create_superuser()