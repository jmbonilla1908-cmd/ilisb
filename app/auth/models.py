from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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
    
    # Relación con la tabla de asociación AlumnoGrupo
    grupos_asociados = db.relationship('AlumnoGrupo', back_populates='alumno', cascade="all, delete-orphan")
    
    # ... (podemos añadir el resto de campos después)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f'alumno_{self.id}'

    @property
    def es_miembro_activo(self):
        """Verifica si el alumno tiene una membresía activa y no revertida."""
        from datetime import datetime
        membresia_activa = self.membresias.filter(
            AlumnoMembresia.revertido == False,
            AlumnoMembresia.fecha_fin >= datetime.utcnow()
        ).first()
        return membresia_activa is not None

    def __repr__(self):
        return f'<Alumno {self.nombres} {self.apellidos}>'


class AlumnoMembresia(db.Model):
    """
    Modelo para registrar las membresías de los alumnos.
    """
    __tablename__ = 'alumno_membresia'

    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.idAlumno'), nullable=False)
    tipo_membresia = db.Column(db.String(50), nullable=False, default='anual') # Ej: anual, semestral
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

    def __repr__(self):
        return f'<AlumnoMembresia id:{self.id} alumno:{self.alumno_id}>'
