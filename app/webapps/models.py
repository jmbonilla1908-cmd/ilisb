from app import db
from datetime import datetime, timezone


class TipoAplicativo(db.Model):
    """
    Modelo para tipos de aplicativos web.
    Define categorías como calculadoras, herramientas, simuladores, etc.
    """
    __tablename__ = 'tipo_aplicativo'
    
    id = db.Column('idtipoaplicativo', db.Integer, primary_key=True)
    nombre = db.Column('nombre', db.String(100), nullable=False)
    descripcion = db.Column('descripcion', db.Text)
    icono = db.Column('icono', db.String(100))  # CSS class o imagen
    color = db.Column('color', db.String(20))   # Color hex para UI
    orden = db.Column('orden', db.Integer, default=99, nullable=False)
    activo = db.Column('activo', db.Boolean, default=True, nullable=False)
    
    # Relación inversa
    aplicativos = db.relationship('Aplicativo', backref='tipo', lazy=True)

    def __repr__(self):
        return f'<TipoAplicativo {self.nombre}>'

    @property
    def slug(self):
        """Genera un slug para URLs amigables."""
        import re
        slug = re.sub(r'[^\w\s-]', '', self.nombre.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')


class Aplicativo(db.Model):
    """
    Modelo para aplicativos web disponibles en el sitio.
    Incluye calculadoras, herramientas y simuladores técnicos.
    """
    __tablename__ = 'aplicativo'
    
    id = db.Column('idAplicativo', db.Integer, primary_key=True)
    tipo_aplicativo_id = db.Column(
        'idTipoaplicativo', db.Integer,
        db.ForeignKey('tipo_aplicativo.idtipoaplicativo'), nullable=False
    )
    nombre = db.Column('nombreaplicativo', db.String(500), nullable=False)
    descripcion = db.Column('descripcion', db.Text)
    descripcion_corta = db.Column('descripcion_corta', db.String(300))
    ruta_archivo = db.Column('ruta_archivo', db.String(500), nullable=False)
    url_help = db.Column('urlhelpAplicativo', db.String(500))
    imagen_preview = db.Column('imagen_preview', db.String(500))
    template_file = db.Column(db.String(120), nullable=True) # El campo que queríamos añadir
    requiere_membresia = db.Column(
        'requiere_membresia', db.Boolean, default=False, nullable=False
    )
    es_premium = db.Column(
        'premium', db.Boolean, default=False, nullable=False
    )
    activo = db.Column('activo', db.Boolean, default=True, nullable=False)
    orden = db.Column('orden', db.Integer, default=1, nullable=False)
    vistas = db.Column('vistas', db.Integer, default=0, nullable=False)
    fecha_registro = db.Column(
        'fecharegistro', db.TIMESTAMP,
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    fecha_actualizacion = db.Column(
        'fechaactualizacion', db.TIMESTAMP,
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Metadatos para SEO
    meta_titulo = db.Column('meta_titulo', db.String(100))
    meta_descripcion = db.Column('meta_descripcion', db.String(300))
    meta_keywords = db.Column('meta_keywords', db.String(500))

    def __repr__(self):
        return f'<Aplicativo {self.nombre}>'
    
    @property
    def slug(self):
        """Genera slug para URLs amigables."""
        import re
        slug = re.sub(r'[^\w\s-]', '', self.nombre.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    @property
    def es_gratuito(self):
        """Verifica si el aplicativo es gratuito."""
        return not self.requiere_membresia and not self.es_premium
    
    def incrementar_vistas(self):
        """Incrementa contador de vistas."""
        self.vistas += 1
        db.session.commit()
    
    @classmethod
    def obtener_por_tipo(cls, tipo_id, solo_activos=True):
        """Obtiene aplicativos por tipo."""
        query = cls.query.filter_by(tipo_aplicativo_id=tipo_id)
        if solo_activos:
            query = query.filter_by(activo=True)
        return query.order_by(cls.orden.asc()).all()
    
    @classmethod
    def obtener_populares(cls, limite=5):
        """Obtiene aplicativos más visitados."""
        return (cls.query.filter_by(activo=True)
                .order_by(cls.vistas.desc())
                .limit(limite).all())
    
    @classmethod
    def obtener_recientes(cls, limite=5):
        """Obtiene los aplicativos más recientemente actualizados o creados."""
        return (cls.query.filter_by(activo=True)
                .order_by(cls.fecha_actualizacion.desc())
                .limit(limite).all())
