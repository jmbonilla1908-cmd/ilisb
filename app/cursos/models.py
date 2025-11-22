from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.mysql import TEXT

# Tabla de asociación para la relación muchos-a-muchos entre Curso y Especializacion
especializacion_curso = db.Table('especializacion_curso',
    db.Column('idEspecializacion_curso', db.Integer, primary_key=True),
    db.Column('idEspecializacion', db.Integer, db.ForeignKey('especializacion.idEspecializacion')),
    db.Column('idCurso', db.Integer, db.ForeignKey('curso.idcurso'))
)

class Especializacion(db.Model):
    __tablename__ = 'especializacion'
    id = db.Column('idEspecializacion', db.Integer, primary_key=True)
    descripcion = db.Column('descEspecializacion', db.String(200), nullable=False)
    slug = db.Column('slugEspecializacion', db.String(500), nullable=False, unique=True)

    # Relación bidireccional con Curso
    cursos = db.relationship('Curso', secondary=especializacion_curso, back_populates='especializaciones')

    def __repr__(self):
        return f'<Especializacion {self.descripcion}>'

class Docente(db.Model):
    __tablename__ = 'docente'
    id = db.Column('iddocente', db.Integer, primary_key=True)
    nombre = db.Column('nombredocente', db.String(200), nullable=False)
    cargo = db.Column('cargodocente', db.String(200))
    descripcion = db.Column('descripciondocente', db.String(3000), nullable=False)
    imagen = db.Column('imagendocente', db.String(200))
    
    # Relación uno-a-muchos: Un docente puede tener muchos grupos
    grupos = db.relationship('Grupo', back_populates='docente')

    def __repr__(self):
        return f'<Docente {self.nombre}>'

class Curso(db.Model):
    __tablename__ = 'curso'
    id = db.Column('idcurso', db.Integer, primary_key=True)
    nombre = db.Column('nombrecurso', db.String(200), nullable=False, unique=True)
    slug = db.Column('slugcurso', db.String(100), nullable=False, unique=True)
    duracion = db.Column('duracioncurso', db.Integer, nullable=False)
    # texto_corto = db.Column('textocortocurso', db.String(500), nullable=False)
    # descripcion = db.Column('descripcioncurso', TEXT, nullable=False)
    # footer = db.Column('footercurso', TEXT)
    # temario = db.Column('temariocurso', TEXT, nullable=False)
    texto_corto = db.Column("textocortocurso", db.Text, nullable=False)
    descripcion = db.Column("descripcioncurso", db.Text, nullable=False)
    footer = db.Column("footercurso", db.Text)
    temario = db.Column("temariocurso", db.Text, nullable=False)
    foto = db.Column('fotocurso', db.String(1000))
    banner = db.Column('bannerCurso', db.String(100))
    banner2 = db.Column('banner2Curso', db.String(100))
    thumbnail = db.Column('thumbnailCurso', db.String(100))

    # Relación uno-a-muchos: Un curso puede tener muchos grupos
    grupos = db.relationship('Grupo', back_populates='curso', lazy='dynamic')
    
    # Relación muchos-a-muchos con Especializacion
    especializaciones = db.relationship('Especializacion', secondary=especializacion_curso, back_populates='cursos')

    def __repr__(self):
        return f'<Curso {self.nombre}>'

class Grupo(db.Model):
    __tablename__ = 'grupo'
    id = db.Column('idgrupo', db.Integer, primary_key=True)
    id_curso = db.Column('idcurso', db.Integer, db.ForeignKey('curso.idcurso'), nullable=False)
    id_docente = db.Column('iddocente', db.Integer, db.ForeignKey('docente.iddocente'), nullable=False)
    precio_usuario = db.Column(
        'preciousuario', db.Numeric(10, 2), nullable=False
    )
    precio_usuario_preinscripcion = db.Column(
        'preciousuariopreinscripcion', db.Numeric(10, 2), nullable=False
    )
    precio_miembro = db.Column(
        'preciomiembro', db.Numeric(10, 2), nullable=False
    )
    precio_miembro_preinscripcion = db.Column(
        'preciomiembropreinscripcion', db.Numeric(10, 2), nullable=False
    )
    visible = db.Column('visible', db.Boolean, default=True, nullable=False)
    
    # --- Nuevos campos para una gestión profesional de fechas y estado ---
    estado = db.Column(db.String(50), default='PROPUESTO', nullable=False) # PROPUESTO, CONFIRMADO, CANCELADO, EN_CURSO, FINALIZADO
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=True)
    horario_descripcion = db.Column('horario', db.Text, nullable=True)
    capacidad_minima = db.Column(db.Integer, default=5)
    capacidad_maxima = db.Column(db.Integer, default=20)

    # Relación para contar alumnos inscritos
    alumnos_asociados = db.relationship('AlumnoGrupo', back_populates='grupo', cascade="all, delete-orphan")

    # Relaciones
    curso = db.relationship('Curso', back_populates='grupos')
    docente = db.relationship('Docente', back_populates='grupos')
    sesiones = db.relationship(
        'Sesion', back_populates='grupo', cascade="all, delete-orphan", lazy='dynamic'
    )

    @property # type: ignore
    def inscritos(self):
        return len(self.alumnos_asociados)

    def __repr__(self):
        return f'<Grupo {self.id} del curso {self.id_curso}>'


class Sesion(db.Model):
    __tablename__ = 'sesion'
    id = db.Column('idsesion', db.Integer, primary_key=True)
    fecha = db.Column('fechasesion', db.Date, nullable=False)
    id_grupo = db.Column(
        'idgrupo', db.Integer, db.ForeignKey('grupo.idgrupo'), nullable=False
    )
    link = db.Column('link', db.String(200))

    grupo = db.relationship('Grupo', back_populates='sesiones') # type: ignore

    def __repr__(self):
        return f'<Sesion {self.id} del grupo {self.id_grupo}>'


class GrupoSesion(db.Model):
    """
    Modelo para la relación entre grupos y sesiones con información adicional.
    Permite gestionar asistencia, grabaciones y estado de cada sesión.
    """
    __tablename__ = 'grupo_sesion'
    
    id = db.Column('idgruposesion', db.Integer, primary_key=True)
    grupo_id = db.Column(
        'idgrupo', db.Integer,
        db.ForeignKey('grupo.idgrupo'), nullable=False
    )
    sesion_id = db.Column(
        'idsesion', db.Integer,
        db.ForeignKey('sesion.idsesion'), nullable=False
    )
    orden = db.Column('orden', db.Integer, nullable=False)
    titulo = db.Column('titulo', db.String(200))
    descripcion = db.Column('descripcion', db.Text)
    duracion_minutos = db.Column('duracion', db.Integer, default=60)
    url_grabacion = db.Column('grabacion', db.String(500))
    url_materiales = db.Column('materiales', db.String(500))
    activa = db.Column('activa', db.Boolean, default=True, nullable=False)
    
    # Relaciones
    grupo = db.relationship('Grupo', backref=db.backref('grupo_sesiones', cascade="all, delete-orphan"))
    sesion = db.relationship('Sesion', backref=db.backref('sesion_grupos', cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<GrupoSesion grupo:{self.grupo_id} sesion:{self.sesion_id}>'
