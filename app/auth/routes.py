from flask import render_template, redirect, url_for, flash, request, make_response
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.auth.models import Alumno

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
