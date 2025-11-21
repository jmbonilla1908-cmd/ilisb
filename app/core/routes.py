from flask import render_template
from app.core import bp
from app import htmx
from app.auth.forms import LoginForm

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('core/index.html', title='Inicio')

@bp.route('/membresia')
def membresia():
    # Pasamos el formulario de login a la plantilla por si el usuario no está logueado
    form = LoginForm()
    return render_template('core/membresia.html', title='Membresía', form=form)

@bp.route('/nosotros')
def nosotros():
    return render_template('core/nosotros.html', title='Nosotros')

@bp.route('/membresia_slides')
def membresia_slides():
    return render_template('core/_membresia_slides.html')

@bp.route('/terminos_y_condiciones')
def terminos_y_condiciones():
    return render_template('core/terminos_y_condiciones.html', title='Términos y Condiciones')