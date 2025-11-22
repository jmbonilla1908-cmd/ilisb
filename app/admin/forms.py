from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, BooleanField, SubmitField, 
                     TextAreaField, SelectField, DateField, IntegerField, FieldList, FormField, TimeField,
                     DecimalField, EmailField)
from wtforms.validators import DataRequired, ValidationError, Optional, Email, EqualTo, NumberRange, Length
from app.admin.models import User
from app.auth.models import Alumno
from app.cursos.models import Curso, Docente


class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Iniciar Sesión')


class AdminUserForm(FlaskForm):
    """Formulario para crear y editar usuarios administradores."""
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=25)])
    full_name = StringField('Nombre Completo', validators=[DataRequired(), Length(min=4, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[
        Optional(),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres.'),
        EqualTo('confirm_password', message='Las contraseñas deben coincidir.')
    ])
    confirm_password = PasswordField('Confirmar Contraseña')
    is_active = BooleanField('Activo', default=True)
    is_superuser = BooleanField('Es Superusuario (Otorga todos los permisos)')
    submit = SubmitField('Guardar Usuario')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso. Por favor, elija otro.')


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


# --- Definimos una lista centralizada de países para los formularios ---
LISTA_PAISES = sorted([
    'Argentina', 'Bolivia', 'Chile', 'Colombia', 'Costa Rica', 'Ecuador',
    'El Salvador', 'EEUU', 'Guatemala', 'Honduras', 'México', 'Nicaragua',
    'Panamá', 'Paraguay', 'Perú', 'República Dominicana', 'Uruguay', 'Venezuela'
])
PAISES_CHOICES = [(pais, pais) for pais in LISTA_PAISES]


class PaisHorarioForm(FlaskForm):
    """Subformulario para un país dentro de un horario."""
    class Meta:
        csrf = False
    # ¡EL CAMBIO CLAVE! Usamos SelectField en lugar de StringField.
    nombre = SelectField('País', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(PaisHorarioForm, self).__init__(*args, **kwargs)
        # Asignamos la lista de países a las opciones del campo.
        self.nombre.choices = PAISES_CHOICES

class HorarioForm(FlaskForm):
    """Subformulario para un bloque de horario."""
    class Meta:
        csrf = False
    horainicio = StringField('Hora Inicio (HH:MM)', validators=[DataRequired()])
    horafin = StringField('Hora Fin (HH:MM)', validators=[DataRequired()])
    paises = FieldList(FormField(PaisHorarioForm), min_entries=0, label='Países')

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
    precio_usuario = DecimalField('Precio Normal', places=2, validators=[DataRequired()], use_locale=False)
    precio_usuario_preinscripcion = DecimalField('Precio Preinscripción', places=2, validators=[Optional()], use_locale=False)
    precio_miembro = DecimalField('Precio Miembro', places=2, validators=[DataRequired()], use_locale=False)
    precio_miembro_preinscripcion = DecimalField('Precio Miembro Preinscripción', places=2, validators=[Optional()], use_locale=False)
    horario_descripcion = TextAreaField('Descripción General del Horario (ej. "Lunes y Miércoles")', validators=[Optional()])
    horarios = FieldList(FormField(HorarioForm), min_entries=0, label='Bloques de Horario por Zona')
    submit = SubmitField('Guardar Grupo')

    def __init__(self, *args, **kwargs):
        super(GrupoForm, self).__init__(*args, **kwargs)
        self.id_curso.choices = [(c.id, c.nombre) for c in Curso.query.order_by(Curso.nombre).all()]
        self.id_docente.choices = [(d.id, d.nombre) for d in Docente.query.order_by(Docente.nombre).all()]

    def validate_fecha_fin(self, field):
        if field.data and self.fecha_inicio.data and field.data < self.fecha_inicio.data:
            raise ValidationError('La fecha de fin no puede ser anterior a la fecha de inicio.')

    def validate_capacidad_maxima(self, field):
        if field.data and self.capacidad_minima.data and field.data < self.capacidad_minima.data:
            raise ValidationError('La capacidad máxima no puede ser menor que la mínima.')


class ItemTemarioForm(FlaskForm):
    """Subformulario para un ítem del temario."""
    class Meta:
        csrf = False  # Deshabilitar CSRF para subformularios
    contenido = StringField('Contenido del Ítem', validators=[DataRequired()])


class ModuloForm(FlaskForm):
    """Subformulario para un módulo del temario."""
    class Meta:
        csrf = False
    titulo = StringField('Título del Módulo', validators=[DataRequired()])
    items = FieldList(FormField(ItemTemarioForm), min_entries=1, label='Ítems del Módulo')


class CursoForm(FlaskForm):
    """Formulario para crear y editar cursos."""
    nombre = StringField('Nombre del Curso', validators=[DataRequired()])
    duracion = IntegerField('Duración (horas)', validators=[DataRequired(), NumberRange(min=1)])
    texto_corto = TextAreaField('Texto Corto (Resumen)', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción Completa', validators=[DataRequired()])
    footer = TextAreaField('Contenido del Pie de Página (Opcional)', validators=[Optional()])
    banner = FileField('Imagen del Banner', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], '¡Solo se permiten imágenes (jpg, png)!')
    ])
    modulos = FieldList(FormField(ModuloForm), min_entries=1, label='Temario del Curso')
    submit = SubmitField('Guardar Cambios')