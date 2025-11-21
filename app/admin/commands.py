import click
from app.admin import bp
from app.admin.models import User
from app import db

@bp.cli.command('create-superuser')
def create_superuser():
    """Crea un nuevo usuario administrador."""
    username = click.prompt('Username')
    first_name = click.prompt('Nombres')
    last_name = click.prompt('Apellidos')
    email = click.prompt('Email', type=click.STRING)
    password = click.prompt(
        'Contraseña', hide_input=True, confirmation_prompt=True
    )

    if User.query.filter_by(email=email).first():
        click.echo(
            click.style(
                f'Error: El email "{email}" ya está en uso.', fg='red'
            ),
            err=True
        )
        return
    
    if User.query.filter_by(username=username).first():
        click.echo(
            click.style(
                f'Error: El username "{username}" ya está en uso.', fg='red'
            ),
            err=True
        )
        return

    user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        is_superuser=True,
        is_active=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(
        click.style(
            f'Superusuario "{username}" ({email}) creado exitosamente.',
            fg='green'
        )
    )