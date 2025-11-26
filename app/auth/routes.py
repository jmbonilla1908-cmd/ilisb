from flask import render_template, redirect, url_for, flash, request, make_response
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, ChangeEmailForm, ChangePasswordForm
from app.auth.models import Alumno
from app.auth.email import send_reset_email, send_email_change_confirmation

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Alumno.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Email o contraseña inválidos', 'danger')
            # Si las credenciales son incorrectas, se vuelve a renderizar el formulario
            return render_template('auth/login.html', title='Ingresar', form=form)

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        # Si no hay página siguiente o si la URL es externa, redirigir al dashboard
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('intranet.dashboard')

        # Redirección estándar de Flask
        return redirect(next_page)

    return render_template('auth/login.html', title='Ingresar', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Alumno(nombres=form.nombres.data, apellidos=form.apellidos.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('¡Felicidades, ahora eres un usuario registrado!', 'success')

        return redirect(url_for('auth.login'))

    # Si el formulario no es válido en una petición POST, lo volvemos a renderizar con errores.
    if request.method == 'POST' and form.errors:
         return render_template('auth/register.html', title='Registro', form=form)

    return render_template('auth/register.html', title='Registro', form=form)


@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    """Ruta para que el alumno solicite el reseteo."""
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        alumno = Alumno.query.filter_by(email=form.email.data).first()
        send_reset_email(alumno)
        flash('Se ha enviado un correo con las instrucciones para restablecer tu contraseña.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html', title='Restablecer Contraseña', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    """Ruta para que el alumno ingrese la nueva contraseña tras validar el token."""
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    alumno = Alumno.verify_reset_token(token)
    if alumno is None:
        flash('El token es inválido o ha expirado.', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        alumno.set_password(form.password.data)
        db.session.commit()
        flash('Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html', title='Restablecer Contraseña', form=form)


@bp.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """Ruta para que un alumno solicite el cambio de su email."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        # Verificar la contraseña actual del usuario
        if not current_user.check_password(form.password.data):
            flash('La contraseña actual es incorrecta.', 'danger')
            return render_template('auth/change_email.html', title='Cambiar Correo', form=form)
        
        # Enviar correo de confirmación al nuevo email
        new_email = form.new_email.data
        send_email_change_confirmation(new_email, current_user)
        flash(f'Se ha enviado un correo de confirmación a {new_email}. Por favor, revisa tu bandeja de entrada.', 'info')
        return redirect(url_for('intranet.dashboard')) # O a la página de perfil

    return render_template('auth/change_email.html', title='Cambiar Correo', form=form)


@bp.route('/change_email/<token>')
@login_required
def change_email_token(token):
    """Ruta que valida el token y efectúa el cambio de email."""
    alumno, new_email = Alumno.verify_email_change_token(token)

    if alumno is None or alumno.id != current_user.id:
        flash('El enlace de confirmación es inválido o ha expirado.', 'warning')
        return redirect(url_for('intranet.dashboard'))

    alumno.email = new_email
    db.session.commit()
    flash('Tu dirección de correo ha sido actualizada exitosamente.', 'success')
    return redirect(url_for('intranet.dashboard'))



@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('La contraseña actual es incorrecta.', 'danger')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Tu contraseña ha sido cambiada exitosamente.', 'success')
            return redirect(url_for('intranet.mis_datos'))
    return render_template('auth/change_password.html', title='Cambiar Contraseña', form=form)
