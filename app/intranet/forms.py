from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired


class DashboardConfigForm(FlaskForm):
    """Formulario para la configuración del dashboard del alumno."""
    mostrar_proximos_cursos = BooleanField('Mostrar Próximos Cursos')
    mostrar_calendario = BooleanField('Mostrar Calendario')
    mostrar_certificados = BooleanField('Mostrar Certificados')
    tema_preferido = SelectField('Tema Preferido', choices=[
        ('claro', 'Claro'),
        ('oscuro', 'Oscuro')
    ], validators=[DataRequired()])
    submit = SubmitField('Guardar Configuración')