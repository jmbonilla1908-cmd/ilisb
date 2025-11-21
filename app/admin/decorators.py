from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """
    Decorator para rutas que requieren autenticación de administrador.
    Solo permite acceso a usuarios del modelo User (admin).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(
                'Debe iniciar sesión como administrador para acceder.',
                'danger'
            )
            return redirect(url_for('admin.login'))
        
        # Verificar que sea un administrador (ID empieza con 'admin_')
        if not current_user.get_id().startswith('admin_'):
            flash(
                'Acceso denegado. Esta área es solo para administradores.',
                'danger'
            )
            return redirect(url_for('core.index'))
        
        # Verificar que el administrador esté activo
        if not getattr(current_user, 'is_active', True):
            flash('Su cuenta de administrador está desactivada.', 'danger')
            return redirect(url_for('core.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def superuser_required(f):
    """
    Decorator para rutas que requieren permisos de super administrador.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(
                'Debe iniciar sesión como administrador para acceder.',
                'danger'
            )
            return redirect(url_for('admin.login'))
        
        # Verificar que sea un administrador
        if not current_user.get_id().startswith('admin_'):
            flash(
                'Acceso denegado. Esta área es solo para administradores.',
                'danger'
            )
            return redirect(url_for('core.index'))
        
        # Verificar que sea superusuario
        if not getattr(current_user, 'is_superuser', False):
            flash(
                'Se requieren permisos de super administrador.',
                'danger'
            )
            return redirect(url_for('admin.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function