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
            # En caso de error, volvemos a renderizar la plantilla.
            # HTMX intercambiará el contenido, una petición normal mostrará la página completa.
            return render_template('auth/login.html', title='Ingresar', form=form), 422

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        # Si no hay página siguiente o si la URL es externa, redirigir al dashboard
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('intranet.dashboard')

        # En caso de éxito, le decimos al cliente que redirija.
        response = make_response()
        response.headers['HX-Redirect'] = next_page
        return response

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

        response = make_response()
        response.headers['HX-Redirect'] = url_for('auth.login')
        return response

    # Si el formulario no es válido en una petición POST, lo volvemos a renderizar con errores.
    if request.method == 'POST' and form.errors:
         return render_template('auth/register.html', title='Registro', form=form), 422

    return render_template('auth/register.html', title='Registro', form=form)
