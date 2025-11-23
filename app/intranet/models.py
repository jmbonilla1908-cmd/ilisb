from app import db
from datetime import datetime, timezone
from app.cursos.models import Grupo, Sesion


class IntranetDashboard(db.Model):
    """
    Modelo para configurar el dashboard personalizado de cada alumno.
    Permite personalizar qué información mostrar en la intranet.
    """
    __tablename__ = 'intranet_dashboard'
    
    id = db.Column('id_dashboard', db.Integer, primary_key=True)
    alumno_id = db.Column(
        'idAlumno', db.Integer,
        db.ForeignKey('alumno.idAlumno'), nullable=False
    )
    mostrar_proximos_cursos = db.Column(
        'mostrar_proximos', db.Boolean, default=True, nullable=False
    )
    mostrar_calendario = db.Column(
        'mostrar_calendario', db.Boolean, default=True, nullable=False
    )
    mostrar_certificados = db.Column(
        'mostrar_certificados', db.Boolean, default=True, nullable=False
    )
    tema_preferido = db.Column('tema', db.String(20), default='claro')
    fecha_ultima_visita = db.Column(
        'ultima_visita', db.TIMESTAMP, 
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relación con Alumno
    alumno = db.relationship('Alumno', backref='dashboard_config')

    def __repr__(self):
        return f'<IntranetDashboard alumno:{self.alumno_id}>'


class ActividadAlumno(db.Model):
    """
    Modelo para registrar actividad del alumno en la intranet.
    Útil para analytics y seguimiento de engagement.
    """
    __tablename__ = 'actividad_alumno'
    
    id = db.Column('id_actividad', db.Integer, primary_key=True)
    alumno_id = db.Column(
        'idAlumno', db.Integer,
        db.ForeignKey('alumno.idAlumno'), nullable=False
    )
    tipo_actividad = db.Column('tipo', db.String(50), nullable=False)
    # Tipos: 'login', 'ver_curso', 'descargar_material', 'ver_sesion', etc.
    descripcion = db.Column('descripcion', db.String(200))
    url_visitada = db.Column('url', db.String(300))
    fecha_actividad = db.Column(
        'fecha', db.TIMESTAMP, 
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    ip_address = db.Column('ip', db.String(45))
    user_agent = db.Column('user_agent', db.String(500))
    
    # Relación con Alumno
    alumno = db.relationship('Alumno', backref='actividades')

    def __repr__(self):
        return f'<ActividadAlumno {self.tipo_actividad} - {self.alumno_id}>'
    
    @classmethod
    def registrar_actividad(cls, alumno_id, tipo, descripcion=None, 
                           url=None, ip=None, user_agent=None):
        """Método helper para registrar actividad."""
        actividad = cls(
            alumno_id=alumno_id,
            tipo_actividad=tipo,
            descripcion=descripcion,
            url_visitada=url,
            ip_address=ip,
            user_agent=user_agent
        )
        db.session.add(actividad)
        return actividad
