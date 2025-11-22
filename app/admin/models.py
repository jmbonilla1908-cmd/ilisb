from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone


class User(UserMixin, db.Model):
    """
    Modelo para Administradores del sistema.
    Separado completamente del modelo Alumno por razones de seguridad.
    """
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    
    # Campos de control administrativo
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    last_login = db.Column(db.DateTime)
    
    # Campo para notas administrativas
    notes = db.Column(db.Text)

    def set_password(self, password):
        """Establece la contraseña hasheada."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña."""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Retorna ID con prefijo para evitar conflictos con Alumno."""
        return f"admin_{self.id}"

    @property
    def full_name(self):
        """Retorna nombre completo."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<User {self.username}>'

    @staticmethod
    def create_superuser(username, email, password, first_name, last_name):
        """Crear un super administrador."""
        admin = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_superuser=True,
            is_active=True
        )
        admin.set_password(password)
        return admin


class ConfiguracionApp(db.Model):
    """
    Modelo para configuraciones globales de la aplicación.
    Permite personalizar comportamiento sin cambiar código.
    """
    __tablename__ = 'configuracion_app'
    
    id = db.Column('idconfiguracion', db.Integer, primary_key=True)
    clave = db.Column('clave', db.String(100), unique=True, nullable=False)
    valor = db.Column('valor', db.Text, nullable=False)
    descripcion = db.Column('descripcion', db.Text)
    tipo_dato = db.Column('tipo', db.String(20), default='string')
    categoria = db.Column('categoria', db.String(50), default='general')
    es_publico = db.Column('publico', db.Boolean, default=False)
    fecha_actualizacion = db.Column(
        'fecha_actualizacion', db.TIMESTAMP,
        default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f'<ConfiguracionApp {self.clave}>'
    
    @property
    def valor_tipado(self):
        """Retorna valor convertido al tipo correcto."""
        if self.tipo_dato == 'boolean':
            return self.valor.lower() in ('true', '1', 'yes', 'on')
        elif self.tipo_dato == 'integer':
            return int(self.valor)
        elif self.tipo_dato == 'float':
            return float(self.valor)
        return self.valor

    @classmethod
    def obtener_valor(cls, clave, default=None):
        """Obtiene valor de configuración por clave."""
        config = cls.query.filter_by(clave=clave).first()
        return config.valor_tipado if config else default


class Auditoria(db.Model):
    """
    Modelo para registro de auditoría del sistema.
    Registra acciones importantes para seguridad y trazabilidad.
    """
    __tablename__ = 'auditoria'
    
    id = db.Column('idauditoria', db.Integer, primary_key=True)
    usuario_id = db.Column(
        'usuario_id', db.Integer,
        db.ForeignKey('user.id'), nullable=True
    )
    accion = db.Column('accion', db.String(100), nullable=False)
    tabla_afectada = db.Column('tabla', db.String(100))
    registro_id = db.Column('registro_id', db.Integer)
    valores_anteriores = db.Column('valores_antes', db.JSON)
    valores_nuevos = db.Column('valores_despues', db.JSON)
    ip_address = db.Column('ip', db.String(45))
    user_agent = db.Column('user_agent', db.String(500))
    fecha_registro = db.Column(
        'fecha', db.TIMESTAMP,
        default=datetime.now(timezone.utc), nullable=False
    )
    
    # Relación
    usuario = db.relationship('User', backref='auditorias')

    def __repr__(self):
        return f'<Auditoria {self.accion} por {self.usuario_id}>'


class Notificacion(db.Model):
    """
    Modelo para notificaciones del sistema.
    Permite enviar mensajes a usuarios y administradores.
    """
    __tablename__ = 'notificacion'
    
    id = db.Column('idnotificacion', db.Integer, primary_key=True)
    destinatario_tipo = db.Column(
        'tipo_destinatario', db.String(20), nullable=False
    )  # 'admin', 'alumno', 'todos'
    destinatario_id = db.Column('destinatario_id', db.Integer)
    titulo = db.Column('titulo', db.String(200), nullable=False)
    mensaje = db.Column('mensaje', db.Text, nullable=False)
    tipo = db.Column('tipo', db.String(20), default='info')
    # tipos: info, success, warning, error
    leida = db.Column('leida', db.Boolean, default=False, nullable=False)
    enlace = db.Column('enlace', db.String(500))
    fecha_creacion = db.Column(
        'fecha_creacion', db.TIMESTAMP,
        default=datetime.now(timezone.utc), nullable=False
    )
    fecha_lectura = db.Column('fecha_lectura', db.TIMESTAMP)

    def __repr__(self):
        return f'<Notificacion {self.titulo}>'
    
    def marcar_leida(self):
        """Marca notificación como leída."""
        self.leida = True
        self.fecha_lectura = datetime.now(timezone.utc)
        db.session.commit()
    
    @classmethod
    def crear_para_admin(cls, titulo, mensaje, admin_id=None, tipo='info'):
        """Crea notificación para administrador específico o todos."""
        notif = cls(
            destinatario_tipo='admin',
            destinatario_id=admin_id,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo
        )
        db.session.add(notif)
        db.session.commit()
        return notif
    
    @classmethod
    def crear_para_alumno(cls, titulo, mensaje, alumno_id, tipo='info'):
        """Crea notificación para alumno específico."""
        notif = cls(
            destinatario_tipo='alumno',
            destinatario_id=alumno_id,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo
        )
        db.session.add(notif)
        db.session.commit()
        return notif
