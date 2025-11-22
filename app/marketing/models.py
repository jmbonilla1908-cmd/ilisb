from app import db
from datetime import datetime, timezone


class TipoAnuncio(db.Model):
    """
    Modelo para tipos de anuncios publicitarios.
    Define categorías como banner, popup, lateral, aliados, etc.
    """
    __tablename__ = 'tipo_anuncio'
    
    id = db.Column('idtipoanuncio', db.Integer, primary_key=True)
    nombre = db.Column('nombre', db.String(100), nullable=False)
    descripcion = db.Column('descripcion', db.Text)
    activo = db.Column('activo', db.Boolean, default=True, nullable=False)
    
    # Relación inversa
    anuncios = db.relationship('Anuncio', backref='tipo', lazy=True)

    def __repr__(self):
        return f'<TipoAnuncio {self.nombre}>'


class AliadoEstrategico(db.Model):
    """
    Modelo específico para aliados estratégicos/anunciantes.
    Separado de Anuncio para mejor gestión de partners.
    """
    __tablename__ = 'aliado_estrategico'
    
    id = db.Column('idaliado', db.Integer, primary_key=True)
    nombre_empresa = db.Column('nombre', db.String(200), nullable=False)
    descripcion = db.Column('descripcion', db.Text)
    logo_url = db.Column('logo', db.String(500), nullable=False)
    sitio_web = db.Column('sitio_web', db.String(300))
    email_contacto = db.Column('email', db.String(100))
    
    # Categorización
    categoria = db.Column('categoria', db.String(50), default='general')
    # Categorías: 'tecnologia', 'consultoria', 'educacion', 'servicios', etc.
    
    # Control de visualización
    activo = db.Column('activo', db.Boolean, default=True, nullable=False)
    destacado = db.Column('destacado', db.Boolean, default=False, nullable=False)
    orden_presentacion = db.Column('orden', db.Integer, default=1)
    
    # Analytics
    impresiones = db.Column('impresiones', db.Integer, default=0, nullable=False)
    clics = db.Column('clics', db.Integer, default=0, nullable=False)
    
    # Fechas
    fecha_alianza = db.Column('fecha_alianza', db.Date)
    fecha_registro = db.Column(
        'fecha_registro', db.TIMESTAMP,
        default=datetime.now(timezone.utc), nullable=False
    )
    
    def __repr__(self):
        return f'<AliadoEstrategico {self.nombre_empresa}>'
    
    @property
    def ctr(self):
        """Calcula Click Through Rate (CTR)."""
        if self.impresiones == 0:
            return 0.0
        return (self.clics / self.impresiones) * 100
    
    def incrementar_impresiones(self):
        """Incrementa contador de impresiones."""
        self.impresiones += 1
        db.session.commit()
    
    def incrementar_clics(self):
        """Incrementa contador de clics."""
        self.clics += 1
        db.session.commit()
    
    @classmethod
    def obtener_activos(cls, limite=None):
        """Obtiene aliados activos ordenados."""
        query = cls.query.filter_by(activo=True).order_by(cls.orden_presentacion.asc())
        if limite:
            query = query.limit(limite)
        return query.all()
    
    @classmethod
    def obtener_por_categoria(cls, categoria):
        """Obtiene aliados por categoría."""
        return cls.query.filter_by(categoria=categoria, activo=True).order_by(cls.orden_presentacion.asc()).all()
    
    @classmethod
    def obtener_destacados(cls, limite=8):
        """Obtiene aliados destacados para carousel."""
        return cls.query.filter_by(activo=True, destacado=True).order_by(cls.orden_presentacion.asc()).limit(limite).all()


class Anuncio(db.Model):
    """
    Modelo para anuncios publicitarios mostrados en el sitio web.
    Incluye configuración de posición, fechas de vigencia y estadísticas.
    """
    __tablename__ = 'anuncio'
    
    id = db.Column('idanuncio', db.Integer, primary_key=True)
    tipo_anuncio_id = db.Column(
        'idtipoanuncio', db.Integer,
        db.ForeignKey('tipo_anuncio.idtipoanuncio'), nullable=False
    )
    titulo = db.Column('titulo', db.String(200), nullable=False)
    descripcion = db.Column('descripcion', db.Text)
    imagen_url = db.Column('imagen', db.String(500))
    enlace_url = db.Column('enlace', db.String(500))
    fecha_inicio = db.Column(
        'fechainicio', db.TIMESTAMP,
        default=datetime.now(timezone.utc), nullable=False
    )
    fecha_fin = db.Column('fechafin', db.TIMESTAMP)
    activo = db.Column('activo', db.Boolean, default=True, nullable=False)
    posicion = db.Column('posicion', db.Integer, default=1)
    impresiones = db.Column(
        'impresiones', db.Integer, default=0, nullable=False
    )
    clics = db.Column('clics', db.Integer, default=0, nullable=False)
    fecha_registro = db.Column(
        'fecharegistro', db.TIMESTAMP,
        default=datetime.now(timezone.utc), nullable=False
    )
    
    def __repr__(self):
        return f'<Anuncio {self.titulo}>'
    
    @property
    def esta_vigente(self):
        """Verifica si el anuncio está en fechas válidas."""
        ahora = datetime.now(timezone.utc)
        inicio_valido = self.fecha_inicio <= ahora
        fin_valido = (self.fecha_fin is None or
                      self.fecha_fin >= ahora)
        return inicio_valido and fin_valido
    
    @property
    def ctr(self):
        """Calcula Click Through Rate (CTR)."""
        if self.impresiones == 0:
            return 0.0
        return (self.clics / self.impresiones) * 100
    
    def incrementar_impresiones(self):
        """Incrementa contador de impresiones."""
        self.impresiones += 1
        db.session.commit()
    
    def incrementar_clics(self):
        """Incrementa contador de clics."""
        self.clics += 1
        db.session.commit()