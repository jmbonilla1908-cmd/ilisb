from app import db
from datetime import datetime

class AlumnoGrupo(db.Model):
    """
    Modelo de asociación que representa la inscripción de un Alumno en un Grupo.
    Esta tabla intermedia permite registrar cuándo se inscribió un alumno y
    el estado de su matrícula en ese grupo específico.
    """
    __tablename__ = 'alumno_grupo'

    id = db.Column('idAlumnoGrupo', db.Integer, primary_key=True)
    alumno_id = db.Column('idAlumno', db.Integer, db.ForeignKey('alumno.idAlumno'), nullable=False)
    grupo_id = db.Column('idGrupo', db.Integer, db.ForeignKey('grupo.idgrupo'), nullable=False)
    
    fecha_inscripcion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    estado_matricula = db.Column(db.String(50), default='INSCRITO', nullable=False) # Ej: INSCRITO, RETIRADO, COMPLETADO
    calificacion = db.Column(db.Numeric(4, 2), nullable=True)

    # Relaciones bidireccionales
    alumno = db.relationship('Alumno', back_populates='grupos_asociados')
    grupo = db.relationship('Grupo', back_populates='alumnos_asociados')

    def __repr__(self):
        return f'<AlumnoGrupo alumno:{self.alumno_id} grupo:{self.grupo_id}>'