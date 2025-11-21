from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SubmitField, 
                     TextAreaField, SelectField, DateField, IntegerField, 
                     DecimalField)
from wtforms.validators import DataRequired, ValidationError, Optional, Email, EqualTo, NumberRange
from app.admin.models import User
from app.auth.models import Alumno
from app.cursos.models import Curso, Docente


class AdminLoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Entrar')


class DocenteForm(FlaskForm):
    """Formulario para crear y editar docentes."""
    nombre = StringField('Nombre Completo', validators=[DataRequired()])
    cargo = StringField('Cargo', validators=[Optional()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    imagen = StringField('URL de la Imagen', validators=[Optional()])
    submit = SubmitField('Guardar Docente')


class AlumnoForm(FlaskForm):
    """Formulario para crear y editar alumnos."""
    nombres = StringField('Nombres', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña (dejar en blanco para no cambiar)', 
                             validators=[Optional(), EqualTo('password2', message='Las contraseñas deben coincidir.')])
    password2 = PasswordField('Confirmar Contraseña', validators=[Optional()])
    imagen = StringField('URL de la Imagen', validators=[Optional()])
    submit = SubmitField('Guardar Alumno')

    def __init__(self, original_email=None, *args, **kwargs):
        super(AlumnoForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data.lower() != self.original_email:
            if Alumno.query.filter_by(email=email.data.lower()).first():
                raise ValidationError('Este email ya está registrado por otro usuario.')


class GrupoForm(FlaskForm):
    """Formulario para crear y editar grupos de cursos."""
    id_curso = SelectField('Curso', coerce=int, validators=[DataRequired()])
    id_docente = SelectField('Docente', coerce=int, validators=[DataRequired()])
    estado = SelectField('Estado', choices=[
        ('PROPUESTO', 'Propuesto'),
        ('CONFIRMADO', 'Confirmado'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado')
    ], validators=[DataRequired()])
    fecha_inicio = DateField('Fecha de Inicio', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_fin = DateField('Fecha de Fin', format='%Y-%m-%d', validators=[Optional()])
    visible = BooleanField('Visible para el público', default=True)
    capacidad_minima = IntegerField('Capacidad Mínima', default=5, validators=[DataRequired(), NumberRange(min=1)])
    capacidad_maxima = IntegerField('Capacidad Máxima', default=20, validators=[DataRequired(), NumberRange(min=1)])
    precio_usuario = DecimalField('Precio Normal', places=2, validators=[DataRequired()])
    precio_usuario_preinscripcion = DecimalField('Precio Preinscripción', places=2, validators=[Optional()])
    precio_miembro = DecimalField('Precio Miembro', places=2, validators=[DataRequired()])
    precio_miembro_preinscripcion = DecimalField('Precio Miembro Preinscripción', places=2, validators=[Optional()])
    horario_descripcion = TextAreaField('Descripción del Horario (ej. "Lunes y Miércoles de 7-9pm")', validators=[Optional()])
    submit = SubmitField('Guardar Grupo')

    def __init__(self, *args, **kwargs):
        super(GrupoForm, self).__init__(*args, **kwargs)
        self.id_curso.choices = [(c.id, c.nombre) for c in Curso.query.order_by('nombre').all()]
        self.id_docente.choices = [(d.id, d.nombre) for d in Docente.query.order_by('nombre').all()]

    def validate_fecha_fin(self, field):
        if field.data and self.fecha_inicio.data and field.data < self.fecha_inicio.data:
            raise ValidationError('La fecha de fin no puede ser anterior a la fecha de inicio.')

    def validate_capacidad_maxima(self, field):
        if field.data and self.capacidad_minima.data and field.data < self.capacidad_minima.data:
            raise ValidationError('La capacidad máxima no puede ser menor que la mínima.')


class CursoForm(FlaskForm):
    """Formulario para crear y editar cursos."""
    nombre = StringField('Nombre del Curso', validators=[DataRequired()])
    duracion = IntegerField('Duración (horas)', validators=[DataRequired(), NumberRange(min=1)])
    texto_corto = TextAreaField('Texto Corto (Resumen)', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción Completa', validators=[DataRequired()])
    temario = TextAreaField('Temario (formato JSON)', validators=[DataRequired()])
    footer = TextAreaField('Contenido del Pie de Página (Opcional)', validators=[Optional()])
    submit = SubmitField('Guardar Cambios')