from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, BooleanField, IntegerField,
                     SubmitField)
from wtforms.validators import DataRequired, Optional, URL, Email


class AliadoForm(FlaskForm):
    """Formulario para crear y editar Aliados Estratégicos."""
    nombre_empresa = StringField('Nombre de la Empresa', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[Optional()])
    logo_url = StringField('URL del Logo', validators=[DataRequired(), URL()])
    sitio_web = StringField('Sitio Web', validators=[Optional(), URL()])
    email_contacto = StringField('Email de Contacto', validators=[Optional(), Email()])
    categoria = StringField('Categoría', default='general', validators=[Optional()])
    orden_presentacion = IntegerField('Orden de Presentación', default=1, validators=[Optional()])
    destacado = BooleanField('Destacado (aparece en carousel)', default=False)
    activo = BooleanField('Activo (visible públicamente)', default=True)
    submit = SubmitField('Guardar Aliado')