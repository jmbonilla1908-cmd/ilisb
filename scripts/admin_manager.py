#!/usr/bin/env python3
"""
Gestión de administradores del sistema ILISB.

Este script permite crear, listar y gestionar administradores del sistema.
"""

import sys
import os
import getpass
from datetime import datetime

# Agregar el directorio padre al path para poder importar la app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from app.admin.models import User


class AdminManager:
    """Gestor de administradores del sistema."""
    
    def __init__(self):
        self.app = create_app()
    
    def create_superuser(self):
        """Crear un super administrador interactivamente."""
        
        with self.app.app_context():
            print("=" * 50)
            print("🔥 CREACIÓN DE SUPER ADMINISTRADOR ILISB")
            print("=" * 50)
            print()
            
            try:
                # Recopilar información
                user_data = self._collect_user_data()
                if not user_data:
                    return False
                
                # Crear el usuario
                superuser = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_superuser=True,
                    is_active=True,
                    notes="Super administrador creado mediante script"
                )
                superuser.set_password(user_data['password'])
                
                # Guardar en la base de datos
                db.session.add(superuser)
                db.session.commit()
                
                # Mostrar confirmación
                self._show_success(superuser)
                return True
                
            except KeyboardInterrupt:
                print("\n\n❌ Operación cancelada por el usuario.")
                return False
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ Error al crear el super administrador: {e}")
                return False
    
    def _collect_user_data(self):
        """Recopilar datos del usuario de forma interactiva."""
        print("📝 Por favor, ingresa los datos del super administrador:\n")
        
        # Username
        while True:
            username = input("👤 Username: ").strip()
            if not username:
                print("   ⚠️  El username es obligatorio.")
                continue
            
            if User.query.filter_by(username=username).first():
                print(f"   ⚠️  El username '{username}' ya existe.")
                continue
            break
        
        # Email
        while True:
            email = input("📧 Email: ").strip()
            if not email:
                print("   ⚠️  El email es obligatorio.")
                continue
            
            if '@' not in email:
                print("   ⚠️  Ingresa un email válido.")
                continue
                
            if User.query.filter_by(email=email).first():
                print(f"   ⚠️  El email '{email}' ya existe.")
                continue
            break
        
        # Nombre
        while True:
            first_name = input("🏷️  Nombre: ").strip()
            if first_name:
                break
            print("   ⚠️  El nombre es obligatorio.")
        
        # Apellido
        while True:
            last_name = input("🏷️  Apellido: ").strip()
            if last_name:
                break
            print("   ⚠️  El apellido es obligatorio.")
        
        # Contraseña
        while True:
            print("🔐 Contraseña:")
            password = getpass.getpass("   Password: ")
            if len(password) < 6:
                print("   ⚠️  La contraseña debe tener al menos 6 caracteres.")
                continue
            
            password_confirm = getpass.getpass("   Confirmar: ")
            if password != password_confirm:
                print("   ⚠️  Las contraseñas no coinciden.")
                continue
            break
        
        return {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password
        }
    
    def _show_success(self, user):
        """Mostrar información de éxito."""
        print("\n" + "=" * 50)
        print("✅ SUPER ADMINISTRADOR CREADO EXITOSAMENTE")
        print("=" * 50)
        print(f"👤 Username: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🏷️  Nombre: {user.full_name}")
        print(f"🆔 ID: {user.id}")
        print(f"🔥 Superuser: SÍ")
        print(f"✅ Estado: ACTIVO")
        print(f"📅 Creado: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        print()
    
    def list_admins(self):
        """Listar todos los administradores existentes."""
        
        with self.app.app_context():
            print("=" * 60)
            print("👥 ADMINISTRADORES DEL SISTEMA ILISB")
            print("=" * 60)
            print()
            
            users = User.query.order_by(User.created_at.desc()).all()
            
            if not users:
                print("📭 No hay administradores registrados.\n")
                return
            
            for i, user in enumerate(users, 1):
                status = "✅ ACTIVO" if user.is_active else "❌ INACTIVO"
                user_type = "🔥 SUPER ADMIN" if user.is_superuser else "👤 ADMIN"
                
                print(f"【{i}】 {user.username}")
                print(f"    🆔 ID: {user.id}")
                print(f"    📧 Email: {user.email}")
                print(f"    🏷️  Nombre: {user.full_name}")
                print(f"    🔰 Tipo: {user_type}")
                print(f"    📊 Estado: {status}")
                print(f"    📅 Creado: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if user.last_login:
                    print(f"    🕐 Último login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"    🕐 Último login: Nunca")
                
                if user.notes:
                    print(f"    📝 Notas: {user.notes}")
                
                print("    " + "-" * 50)
            
            print(f"\n📊 Total: {len(users)} administrador(es)\n")
    
    def delete_user(self, username):
        """Eliminar un administrador (solo para superusuarios)."""
        
        with self.app.app_context():
            user = User.query.filter_by(username=username).first()
            
            if not user:
                print(f"❌ Usuario '{username}' no encontrado.")
                return False
            
            if user.is_superuser:
                confirm = input(f"⚠️  ¿Estás seguro de eliminar al SUPER ADMIN '{username}'? (escriba 'CONFIRMAR'): ")
                if confirm != 'CONFIRMAR':
                    print("❌ Operación cancelada.")
                    return False
            
            try:
                db.session.delete(user)
                db.session.commit()
                print(f"✅ Usuario '{username}' eliminado exitosamente.")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error al eliminar usuario: {e}")
                return False


def show_help():
    """Mostrar ayuda del script."""
    print("""
🔧 GESTIÓN DE ADMINISTRADORES ILISB

Uso: python admin_manager.py [comando]

Comandos disponibles:
  create, new          Crear un nuevo super administrador
  list, ls             Listar todos los administradores
  delete <username>    Eliminar un administrador
  help, -h, --help     Mostrar esta ayuda

Ejemplos:
  python admin_manager.py create
  python admin_manager.py list
  python admin_manager.py delete usuario123
""")


def main():
    """Función principal del script."""
    manager = AdminManager()
    
    if len(sys.argv) == 1:
        # Sin argumentos, crear superusuario por defecto
        manager.create_superuser()
    
    elif len(sys.argv) >= 2:
        command = sys.argv[1].lower()
        
        if command in ['create', 'new']:
            manager.create_superuser()
        
        elif command in ['list', 'ls']:
            manager.list_admins()
        
        elif command == 'delete' and len(sys.argv) == 3:
            username = sys.argv[2]
            manager.delete_user(username)
        
        elif command in ['help', '-h', '--help']:
            show_help()
        
        else:
            print("❌ Comando no reconocido.")
            show_help()
    
    else:
        show_help()


if __name__ == "__main__":
    main()