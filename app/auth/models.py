from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer


# Esta función es requerida por Flask-Login para cargar un usuario desde la sesión
@login_manager.user_loader
def load_user(id):
    # Intentamos cargar primero como Alumno, luego como User (admin)
    if id.startswith('alumno_'):
        alumno_id = id.replace('alumno_', '')
        return Alumno.query.get(int(alumno_id))
    elif id.startswith('admin_'):
        from app.admin.models import User
        admin_id = id.replace('admin_', '')
        return User.query.get(int(admin_id))
    else:
        # Compatibilidad hacia atrás: asumir que es un alumno
        return Alumno.query.get(int(id))


class Membresia(db.Model):
    """
    Define los tipos de membresía disponibles en el sistema.
    """
    __tablename__ = 'membresia'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False) # Ej: "Anual", "Mensual"
    precio_base = db.Column(db.Numeric(10, 2), nullable=False)
    moneda = db.Column(db.String(10), nullable=False, default='USD')
    duracion_cantidad = db.Column(db.Integer, nullable=False, default=1)
    duracion_unidad = db.Column(db.String(20), nullable=False, default='months') # 'days', 'months', 'years'

    def __repr__(self):
        return f'<Membresia {self.nombre}>'


class Alumno(UserMixin, db.Model):
    __tablename__ = 'alumno'
    
    id = db.Column('idAlumno', db.Integer, primary_key=True)
    email = db.Column(
        'emailAlumno', db.String(200), unique=True, nullable=False
    )
    nombres = db.Column('nombresAlumno', db.String(200), nullable=False)
    apellidos = db.Column('apellidosAlumno', db.String(200), nullable=False)
    password_hash = db.Column('claveAlumno', db.String(256), nullable=False)
    imagen = db.Column('imagenAlumno', db.String(500))
    telefono = db.Column('telefono', db.String(100))
    token_verificacion = db.Column('tokenVerificacion', db.String(500))
    correo_verificado = db.Column(
        'correoVerificado', db.Boolean, default=False, nullable=False
    )
    email_cambio = db.Column('emailCambio', db.String(100))
    token_email_cambio = db.Column('tokenEmailCambio', db.String(200))
    reset_password = db.Column('resetPassword', db.String(100))
    password_salt = db.Column('passwordSalt', db.String(10))
    fecha_verificacion = db.Column('fechaVerificacion', db.DateTime)
    fecha_reset = db.Column('fechaReset', db.DateTime)
    fecha_email_cambio = db.Column('fechaEmailCambio', db.DateTime)
    apuntes = db.Column('apuntes', db.String(500))
    
    # Las columnas 'es_miembro' y 'fecha_fin_membresia' han sido eliminadas.

    # Relación con la tabla de asociación AlumnoGrupo (importada desde matriculas)
    from app.matriculas.models import AlumnoGrupo
    grupos_asociados = db.relationship('AlumnoGrupo', back_populates='alumno', cascade="all, delete-orphan")
    
    # ... (podemos añadir el resto de campos después)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f'alumno_{self.id}'

    def get_reset_token(self, expires_sec=1800):
        """Genera un token seguro para restaurar la contraseña."""
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'alumno_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        """Verifica el token de restauración y devuelve el Alumno si es válido."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
            alumno_id = data.get('alumno_id')
        except Exception:
            return None
        return Alumno.query.get(alumno_id)

    def get_email_change_token(self, new_email, expires_sec=1800):
        """Genera un token seguro para el cambio de email."""
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'alumno_id': self.id, 'new_email': new_email})

    @staticmethod
    def verify_email_change_token(token, expires_sec=1800):
        """Verifica el token de cambio de email y devuelve el Alumno y el nuevo email."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
            alumno_id = data.get('alumno_id')
            new_email = data.get('new_email')
        except Exception:
            return None, None
        return Alumno.query.get(alumno_id), new_email

    @property
    def membresia_activa_obj(self):
        """Verifica si el alumno tiene una membresía activa y no revertida."""
        from datetime import datetime
        # Devuelve el objeto de la membresía activa más reciente, o None si no hay ninguna.
        return self.membresias.filter(
            AlumnoMembresia.revertido == False,
            # Reactivamos la validación de fecha, que es crucial para la lógica de negocio.
            AlumnoMembresia.fecha_fin >= datetime.now(timezone.utc)
        ).order_by(AlumnoMembresia.fecha_fin.desc()).first()

    @property
    def es_miembro_activo(self):
        """Propiedad simple que devuelve True o False."""
        return self.membresia_activa_obj is not None

    def __repr__(self):
        return f'<Alumno {self.nombres} {self.apellidos}>'


class AlumnoMembresia(db.Model):
    """
    Modelo para registrar las membresías de los alumnos.
    """
    __tablename__ = 'alumno_membresia'

    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.idAlumno', ondelete='CASCADE'), nullable=False)
    membresia_id = db.Column(db.Integer, db.ForeignKey('membresia.id'), nullable=False)
    
    fecha_inicio = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    fecha_fin = db.Column(db.DateTime, nullable=False)
    
    id_pago = db.Column(db.String(100)) # ID de la transacción (Stripe, PayPal, etc.)
    monto = db.Column(db.Numeric(10, 2))
    revertido = db.Column(db.Boolean, default=False, nullable=False)

    # Relación con el alumno
    alumno = db.relationship(
        'Alumno', 
        backref=db.backref('membresias', lazy='dynamic', cascade="all, delete-orphan")
    )
    # Relación con el tipo de membresía
    tipo_membresia_info = db.relationship(
        'Membresia',
        backref=db.backref('instancias', lazy='dynamic')
    )

    def __repr__(self):
        return f'<AlumnoMembresia id:{self.id} alumno:{self.alumno_id}>'
