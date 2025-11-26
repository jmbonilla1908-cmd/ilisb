from flask import render_template, url_for, current_app
from flask_mail import Message
from app import mail

def send_reset_email(alumno):
    """
    Envía el correo de reseteo de contraseña a un alumno.
    """
    token = alumno.get_reset_token()
    
    # Configura el remitente con un nombre para mostrar
    sender_tuple = (
        current_app.config.get('MAIL_SENDER_DISPLAY_NAME', 'ILISB'),
        current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    msg = Message('Solicitud de Reseteo de Contraseña - ILISB',
                  sender=sender_tuple,
                  recipients=[alumno.email])
    
    msg.body = f'''Para restablecer tu contraseña, visita el siguiente enlace:
{url_for('auth.reset_token', token=token, _external=True)}

Si no solicitaste este cambio, por favor ignora este correo.'''
    msg.html = render_template('auth/password_reset_email.html',
                               alumno=alumno, token=token)
    mail.send(msg)


def send_email_change_confirmation(new_email, alumno):
    """
    Envía el correo de confirmación para el cambio de email.
    """
    token = alumno.get_email_change_token(new_email)
    
    sender_tuple = (
        current_app.config.get('MAIL_SENDER_DISPLAY_NAME', 'ILISB'),
        current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    msg = Message('Confirmación de Cambio de Correo Electrónico - ILISB',
                  sender=sender_tuple,
                  recipients=[new_email])
    
    msg.body = f'''Para confirmar tu nueva dirección de correo, visita el siguiente enlace:
{url_for('auth.change_email_token', token=token, _external=True)}

Si no solicitaste este cambio, por favor ignora este correo.'''
    msg.html = render_template('auth/email_change_confirmation.html',
                               alumno=alumno, token=token)
    mail.send(msg)