from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.auth.models import Alumno

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    nombres = StringField('Nombres', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField(
        'Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

    def validate_email(self, email):
        """
        Valida que el email no esté ya registrado en la base de datos.
        """
        user = Alumno.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Por favor, use un email diferente.')


class RequestResetForm(FlaskForm):
    """Formulario para solicitar el reseteo de contraseña."""
    email = StringField('Correo Electrónico',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar Reseteo de Contraseña')

    def validate_email(self, email):
        alumno = Alumno.query.filter_by(email=email.data).first()
        if alumno is None:
            raise ValidationError('No existe una cuenta con ese correo. Debes registrarte primero.')

class ResetPasswordForm(FlaskForm):
    """Formulario para establecer la nueva contraseña."""
    password = PasswordField('Nueva Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Nueva Contraseña',
                                     validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir.')])
    submit = SubmitField('Restablecer Contraseña')


class ChangeEmailForm(FlaskForm):
    """Formulario para solicitar el cambio de email."""
    new_email = StringField('Nuevo Correo Electrónico',
                            validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña Actual',
                             validators=[DataRequired()])
    submit = SubmitField('Solicitar Cambio de Correo')

    def validate_new_email(self, new_email):
        """Valida que el nuevo email no esté ya en uso."""
        if Alumno.query.filter_by(email=new_email.data).first():
            raise ValidationError('Este correo electrónico ya está registrado. Por favor, elija otro.')


class ChangeUserDataForm(FlaskForm):
    """Formulario para que el usuario edite sus datos personales."""
    nombres = StringField('Nombres', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[])
    submit = SubmitField('Actualizar Datos')


class ChangePasswordForm(FlaskForm):
    """Formulario para cambiar la contraseña de un usuario logueado."""
    current_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Nueva Contraseña',
                                     validators=[DataRequired(), EqualTo('new_password', message='Las contraseñas deben coincidir.')])
    submit = SubmitField('Cambiar Contraseña')