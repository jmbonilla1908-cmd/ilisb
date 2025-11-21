from app import db
from datetime import datetime, date
from app.cursos.models import Grupo, Sesion
from app.matriculas.models import AlumnoGrupo


class EventoCalendario(db.Model):
    """
    Modelo para eventos personalizados en el calendario.
    Permite agregar eventos institucionales, recordatorios, etc.
    """
    __tablename__ = 'evento_calendario'
    
    id = db.Column('id_evento', db.Integer, primary_key=True)
    titulo = db.Column('titulo', db.String(200), nullable=False)
    descripcion = db.Column('descripcion', db.Text)
    fecha_evento = db.Column('fecha', db.Date, nullable=False)
    hora_inicio = db.Column('hora_inicio', db.Time)
    hora_fin = db.Column('hora_fin', db.Time)
    tipo_evento = db.Column('tipo', db.String(50), default='general')
    # Tipos: 'general', 'institucional', 'festivo', 'mantenimiento'
    color = db.Column('color', db.String(20), default='#007bff')
    visible_para_todos = db.Column(
        'publico', db.Boolean, default=True, nullable=False
    )
    activo = db.Column('activo', db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(
        'fecha_creacion', db.TIMESTAMP,
        default=datetime.utcnow, nullable=False
    )
    
    def __repr__(self):
        return f'<EventoCalendario {self.titulo}>'
    
    @classmethod
    def obtener_eventos_mes(cls, year, month):
        """Obtiene eventos de un mes específico."""
        # Primer y último día del mes
        primer_dia = date(year, month, 1)
        if month == 12:
            ultimo_dia = date(year + 1, 1, 1)
        else:
            ultimo_dia = date(year, month + 1, 1)
        
        return cls.query.filter(
            cls.fecha_evento >= primer_dia,
            cls.fecha_evento < ultimo_dia,
            cls.activo == True,
            cls.visible_para_todos == True
        ).all()


class RecordatorioPersonal(db.Model):
    """
    Modelo para recordatorios personales del alumno.
    Permite que cada alumno cree sus propios recordatorios.
    """
    __tablename__ = 'recordatorio_personal'
    
    id = db.Column('id_recordatorio', db.Integer, primary_key=True)
    alumno_id = db.Column(
        'idAlumno', db.Integer,
        db.ForeignKey('alumno.idAlumno'), nullable=False
    )
    titulo = db.Column('titulo', db.String(200), nullable=False)
    descripcion = db.Column('descripcion', db.Text)
    fecha_recordatorio = db.Column('fecha', db.Date, nullable=False)
    hora_recordatorio = db.Column('hora', db.Time)
    completado = db.Column(
        'completado', db.Boolean, default=False, nullable=False
    )
    fecha_creacion = db.Column(
        'fecha_creacion', db.TIMESTAMP,
        default=datetime.utcnow, nullable=False
    )
    
    # Relación con Alumno
    alumno = db.relationship('Alumno', backref='recordatorios')

    def __repr__(self):
        return f'<RecordatorioPersonal {self.titulo} - {self.alumno_id}>'
    
    @classmethod
    def obtener_recordatorios_alumno_mes(cls, alumno_id, year, month):
        """Obtiene recordatorios de un alumno para un mes específico."""
        primer_dia = date(year, month, 1)
        if month == 12:
            ultimo_dia = date(year + 1, 1, 1)
        else:
            ultimo_dia = date(year, month + 1, 1)
        
        return cls.query.filter(
            cls.alumno_id == alumno_id,
            cls.fecha_recordatorio >= primer_dia,
            cls.fecha_recordatorio < ultimo_dia
        ).all()


class CalendarioView:
    """
    Clase helper para generar datos del calendario integrado.
    Combina sesiones, eventos y recordatorios para un alumno específico.
    """
    
    @staticmethod
    def obtener_datos_calendario(alumno_id, year, month):
        """
        Obtiene todos los datos del calendario para un alumno y mes específico.
        Retorna diccionario con eventos organizados por día.
        """
        # Primer y último día del mes
        primer_dia = date(year, month, 1)
        if month == 12:
            ultimo_dia = date(year + 1, 1, 1)
        else:
            ultimo_dia = date(year, month + 1, 1)
        
        # Obtener matrículas del alumno
        matriculas = AlumnoGrupo.query.filter_by(alumno_id=alumno_id).all()
        grupo_ids = [m.grupo_id for m in matriculas]
        
        # Obtener sesiones de los grupos del alumno
        sesiones = Sesion.query.filter(
            Sesion.id_grupo.in_(grupo_ids),
            Sesion.fecha >= primer_dia,
            Sesion.fecha < ultimo_dia
        ).join(Grupo).all()
        
        # Obtener eventos institucionales
        eventos = EventoCalendario.obtener_eventos_mes(year, month)
        
        # Obtener recordatorios personales
        recordatorios = RecordatorioPersonal.obtener_recordatorios_alumno_mes(
            alumno_id, year, month
        )
        
        # Organizar por día
        calendario_datos = {}
        
        # Agregar sesiones
        for sesion in sesiones:
            dia = sesion.fecha.day
            if dia not in calendario_datos:
                calendario_datos[dia] = []
            
            calendario_datos[dia].append({
                'tipo': 'sesion',
                'titulo': f'Sesión: {sesion.grupo.curso.nombre}',
                'descripcion': f'Grupo {sesion.grupo.id}',
                'hora': None,
                'color': '#28a745',
                'url': f'/intranet/sesion/{sesion.id}',
                'objeto': sesion
            })
        
        # Agregar eventos institucionales
        for evento in eventos:
            dia = evento.fecha_evento.day
            if dia not in calendario_datos:
                calendario_datos[dia] = []
            
            calendario_datos[dia].append({
                'tipo': 'evento',
                'titulo': evento.titulo,
                'descripcion': evento.descripcion,
                'hora': evento.hora_inicio,
                'color': evento.color,
                'url': None,
                'objeto': evento
            })
        
        # Agregar recordatorios personales
        for recordatorio in recordatorios:
            dia = recordatorio.fecha_recordatorio.day
            if dia not in calendario_datos:
                calendario_datos[dia] = []
            
            calendario_datos[dia].append({
                'tipo': 'recordatorio',
                'titulo': recordatorio.titulo,
                'descripcion': recordatorio.descripcion,
                'hora': recordatorio.hora_recordatorio,
                'color': '#ffc107' if not recordatorio.completado else '#6c757d',
                'url': f'/intranet/recordatorio/{recordatorio.id}',
                'objeto': recordatorio
            })
        
        return calendario_datos
    
    @staticmethod
    def obtener_proximos_eventos(alumno_id, limite=5):
        """
        Obtiene los próximos eventos para un alumno.
        Útil para mostrar en dashboard.
        """
        hoy = date.today()
        
        # Obtener próximas sesiones
        matriculas = AlumnoGrupo.query.filter_by(alumno_id=alumno_id).all()
        grupo_ids = [m.grupo_id for m in matriculas]
        
        proximas_sesiones = Sesion.query.filter(
            Sesion.id_grupo.in_(grupo_ids),
            Sesion.fecha >= hoy
        ).join(Grupo).order_by(Sesion.fecha).limit(limite).all()
        
        # Obtener próximos eventos institucionales
        proximos_eventos = EventoCalendario.query.filter(
            EventoCalendario.fecha_evento >= hoy,
            EventoCalendario.activo == True,
            EventoCalendario.visible_para_todos == True
        ).order_by(EventoCalendario.fecha_evento).limit(limite).all()
        
        # Obtener próximos recordatorios
        proximos_recordatorios = RecordatorioPersonal.query.filter(
            RecordatorioPersonal.alumno_id == alumno_id,
            RecordatorioPersonal.fecha_recordatorio >= hoy,
            RecordatorioPersonal.completado == False
        ).order_by(RecordatorioPersonal.fecha_recordatorio).limit(limite).all()
        
        # Combinar y ordenar todos los eventos
        todos_eventos = []
        
        for sesion in proximas_sesiones:
            todos_eventos.append({
                'fecha': sesion.fecha,
                'tipo': 'sesion',
                'titulo': f'Sesión: {sesion.grupo.curso.nombre}',
                'descripcion': f'Grupo {sesion.grupo.id}',
                'color': '#28a745'
            })
        
        for evento in proximos_eventos:
            todos_eventos.append({
                'fecha': evento.fecha_evento,
                'tipo': 'evento',
                'titulo': evento.titulo,
                'descripcion': evento.descripcion,
                'color': evento.color
            })
        
        for recordatorio in proximos_recordatorios:
            todos_eventos.append({
                'fecha': recordatorio.fecha_recordatorio,
                'tipo': 'recordatorio',
                'titulo': recordatorio.titulo,
                'descripcion': recordatorio.descripcion,
                'color': '#ffc107'
            })
        
        # Ordenar por fecha y retornar los primeros
        todos_eventos.sort(key=lambda x: x['fecha'])
        return todos_eventos[:limite]