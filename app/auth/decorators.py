from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def student_required(f):
    """
    Decorator para rutas que requieren que el usuario sea un Alumno autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debe iniciar sesión para acceder a esta página.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Verificar que el usuario actual sea un Alumno (ID empieza con 'alumno_')
        if not current_user.get_id().startswith('alumno_'):
            flash('Acceso denegado. Esta área es solo para estudiantes.', 'danger')
            return redirect(url_for('core.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator para rutas que requieren que el usuario sea un Administrador
    autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debe iniciar sesión para acceder a esta página.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Verificar que el usuario actual sea un Admin (empieza con 'admin_')
        if not current_user.get_id().startswith('admin_'):
            flash('Acceso denegado. Esta área es solo para administradores.',
                  'danger')
            return redirect(url_for('core.index'))
        
        return f(*args, **kwargs)
    return decorated_function