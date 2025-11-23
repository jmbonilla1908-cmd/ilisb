from app import db
from datetime import datetime, timezone


class ConfiguracionSitio(db.Model):
    """
    Modelo para configuraciones generales del sitio web.
    Maneja información institucional, contacto, etc.
    """
    __tablename__ = 'configuracion_sitio'
    
    id = db.Column('id_config', db.Integer, primary_key=True)
    nombre_institucion = db.Column(
        'nombre_institucion', db.String(200), nullable=False
    )
    descripcion_corta = db.Column('descripcion_corta', db.String(500))
    descripcion_larga = db.Column('descripcion_larga', db.Text)
    
    # Información de contacto
    telefono = db.Column('telefono', db.String(20))
    email_contacto = db.Column('email', db.String(100))
    direccion = db.Column('direccion', db.String(300))
    
    # URLs redes sociales
    facebook_url = db.Column('facebook', db.String(200))
    instagram_url = db.Column('instagram', db.String(200))
    linkedin_url = db.Column('linkedin', db.String(200))
    youtube_url = db.Column('youtube', db.String(200))
    
    # Configuraciones de funcionamiento
    sitio_activo = db.Column(
        'sitio_activo', db.Boolean, default=True, nullable=False
    )
    mensaje_mantenimiento = db.Column('mensaje_mantenimiento', db.Text)
    permitir_registro = db.Column(
        'permitir_registro', db.Boolean, default=True, nullable=False
    )
    
    # Metadatos SEO
    meta_titulo = db.Column('meta_titulo', db.String(100))
    meta_descripcion = db.Column('meta_descripcion', db.String(300))
    meta_keywords = db.Column('meta_keywords', db.String(500))
    
    fecha_actualizacion = db.Column(
        'fecha_actualizacion', db.TIMESTAMP,
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f'<ConfiguracionSitio {self.nombre_institucion}>'
    
    @classmethod
    def obtener_configuracion(cls):
        """Obtiene la configuración activa del sitio."""
        return cls.query.first()


class TestimonioAlumno(db.Model):
    """
    Modelo para testimonios de alumnos.
    Para mostrar en página principal y landing pages.
    """
    __tablename__ = 'testimonio_alumno'
    
    id = db.Column('id_testimonio', db.Integer, primary_key=True)
    alumno_id = db.Column(
        'idAlumno', db.Integer,
        db.ForeignKey('alumno.idAlumno'), nullable=True
    )  # Puede ser NULL para testimonios anónimos
    nombre_mostrar = db.Column('nombre', db.String(200), nullable=False)
    cargo_empresa = db.Column('cargo', db.String(200))
    testimonio = db.Column('testimonio', db.Text, nullable=False)
    calificacion = db.Column('calificacion', db.Integer, default=5)  # 1-5
    imagen_url = db.Column('imagen', db.String(300))
    
    # Control de publicación
    aprobado = db.Column('aprobado', db.Boolean, default=False, nullable=False)
    destacado = db.Column('destacado', db.Boolean, default=False, nullable=False)
    activo = db.Column('activo', db.Boolean, default=True, nullable=False)
    
    fecha_creacion = db.Column(
        'fecha_creacion', db.TIMESTAMP,
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    fecha_aprobacion = db.Column('fecha_aprobacion', db.TIMESTAMP)
    
    # Relación con Alumno (opcional)
    alumno = db.relationship('Alumno', backref='testimonios')

    def __repr__(self):
        return f'<TestimonioAlumno {self.nombre_mostrar}>'
    
    @classmethod
    def obtener_destacados(cls, limite=3):
        """Obtiene testimonios destacados para homepage."""
        return cls.query.filter_by(
            aprobado=True, destacado=True, activo=True
        ).order_by(cls.fecha_aprobacion.desc()).limit(limite).all()
    
    @classmethod
    def obtener_aprobados(cls, limite=10):
        """Obtiene todos los testimonios aprobados."""
        return cls.query.filter_by(
            aprobado=True, activo=True
        ).order_by(cls.fecha_aprobacion.desc()).limit(limite).all()


class EstadisticaSitio(db.Model):
    """
    Modelo para estadísticas generales del sitio.
    Para mostrar números de impacto en landing pages.
    """
    __tablename__ = 'estadistica_sitio'
    
    id = db.Column('id_estadistica', db.Integer, primary_key=True)
    tipo_estadistica = db.Column('tipo', db.String(50), nullable=False)
    # Tipos: 'alumnos_graduados', 'cursos_activos', 'horas_formacion', etc.
    valor = db.Column('valor', db.Integer, nullable=False)
    titulo_mostrar = db.Column('titulo', db.String(100), nullable=False)
    descripcion = db.Column('descripcion', db.String(200))
    icono = db.Column('icono', db.String(50))  # Clase CSS del icono
    orden = db.Column('orden', db.Integer, default=1)
    activo = db.Column('activo', db.Boolean, default=True, nullable=False)
    
    fecha_actualizacion = db.Column(
        'fecha_actualizacion', db.TIMESTAMP,
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f'<EstadisticaSitio {self.tipo_estadistica}: {self.valor}>'
    
    @classmethod
    def obtener_estadisticas_activas(cls):
        """Obtiene estadísticas para mostrar en homepage."""
        return cls.query.filter_by(activo=True).order_by(cls.orden).all()
    
    @classmethod
    def actualizar_estadistica(cls, tipo, nuevo_valor):
        """Actualiza o crea una estadística."""
        estadistica = cls.query.filter_by(tipo_estadistica=tipo).first()
        if estadistica:
            estadistica.valor = nuevo_valor
        else:
            # Crear nueva estadística con valores por defecto
            titulos_default = {
                'alumnos_graduados': 'Alumnos Graduados',
                'cursos_activos': 'Cursos Disponibles',
                'horas_formacion': 'Horas de Formación',
                'empresas_aliadas': 'Empresas Aliadas'
            }
            estadistica = cls(
                tipo_estadistica=tipo,
                valor=nuevo_valor,
                titulo_mostrar=titulos_default.get(tipo, tipo.title())
            )
            db.session.add(estadistica)
        
        return estadistica


class PaginaEstatica(db.Model):
    """
    Modelo para páginas estáticas del sitio.
    Permite gestionar contenido de páginas como "Nosotros", "Términos", etc.
    """
    __tablename__ = 'pagina_estatica'
    
    id = db.Column('id_pagina', db.Integer, primary_key=True)
    slug = db.Column('slug', db.String(100), unique=True, nullable=False)
    titulo = db.Column('titulo', db.String(200), nullable=False)
    contenido = db.Column('contenido', db.Text, nullable=False)
    
    # SEO
    meta_titulo = db.Column('meta_titulo', db.String(100))
    meta_descripcion = db.Column('meta_descripcion', db.String(300))
    
    # Control de publicación
    publicada = db.Column('publicada', db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(
        'fecha_creacion', db.TIMESTAMP,
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    fecha_actualizacion = db.Column(
        'fecha_actualizacion', db.TIMESTAMP,
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f'<PaginaEstatica {self.slug}>'
    
    @classmethod
    def obtener_por_slug(cls, slug):
        """Obtiene página por slug."""
        return cls.query.filter_by(slug=slug, publicada=True).first()