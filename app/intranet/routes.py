from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.auth.decorators import student_required
from app.intranet import intranetModule
from .models import IntranetDashboard, ActividadAlumno
from .forms import DashboardConfigForm
from app.matriculas.models import AlumnoGrupo
from app.auth.models import AlumnoMembresia  # Corregido: Importar desde auth.models
from app.cursos.models import Grupo, Sesion
from sqlalchemy import desc
from app import db
from datetime import datetime, timedelta


@intranetModule.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Dashboard principal del alumno en la intranet."""
    alumno_id = current_user.id
    
    # Registrar actividad
    ActividadAlumno.registrar_actividad(
        alumno_id=alumno_id,
        tipo='dashboard_view',
        descripcion='Vista del dashboard principal',
        ip=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    # Obtener configuración del dashboard
    dashboard_config = IntranetDashboard.query.filter_by(
        alumno_id=alumno_id
    ).first()
    
    if not dashboard_config:
        # Crear configuración por defecto
        dashboard_config = IntranetDashboard(alumno_id=alumno_id)
        db.session.add(dashboard_config)
        db.session.commit()
    
    # Obtener cursos matriculados
    matriculas = AlumnoGrupo.query.filter_by(
        alumno_id=alumno_id
    ).join(Grupo).all()
    
    # Obtener próximas sesiones (próximos 30 días)
    fecha_limite = datetime.now().date() + timedelta(days=30)
    proximas_sesiones = []
    
    for matricula in matriculas:
        sesiones = Sesion.query.filter(
            Sesion.id_grupo == matricula.grupo_id,
            Sesion.fecha >= datetime.now().date(),
            Sesion.fecha <= fecha_limite
        ).order_by(Sesion.fecha.asc()).limit(5).all()
        
        for sesion in sesiones:
            proximas_sesiones.append({
                'sesion': sesion,
                'grupo': matricula.grupo,
                'curso': matricula.grupo.curso if matricula.grupo else None
            })
    
    # Ordenar por fecha
    proximas_sesiones.sort(key=lambda x: x['sesion'].fecha)
    
    # Obtener la membresía más reciente para mostrar su información
    membresia = AlumnoMembresia.query.filter_by(
        alumno_id=alumno_id
    ).order_by(desc(AlumnoMembresia.fecha_fin)).first()
    
    return render_template('intranet/dashboard.html',
                         dashboard_config=dashboard_config,
                         matriculas=matriculas,
                         proximas_sesiones=proximas_sesiones[:5],
                         membresia=membresia)


@intranetModule.route('/mis-cursos')
@login_required
@student_required
def mis_cursos():
    """Vista detallada de cursos del alumno - complementa matriculas."""
    alumno_id = current_user.id
    
    # Registrar actividad
    ActividadAlumno.registrar_actividad(
        alumno_id=alumno_id,
        tipo='mis_cursos_view',
        descripcion='Vista de mis cursos',
        ip=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    # Obtener cursos con más detalles que en matriculas
    matriculas = db.session.query(AlumnoGrupo).filter_by(
        alumno_id=alumno_id
    ).join(Grupo).join(Grupo.curso).all()
    
    # Agrupar por estado
    cursos_activos = []
    cursos_completados = []
    
    for matricula in matriculas:
        # Obtener sesiones del grupo
        sesiones = Sesion.query.filter_by(
            id_grupo=matricula.grupo_id
        ).order_by(Sesion.fecha).all()
        
        # Determinar estado basado en fechas de sesiones
        hoy = datetime.now().date()
        sesiones_futuras = [s for s in sesiones if s.fecha >= hoy]
        
        curso_info = {
            'matricula': matricula,
            'grupo': matricula.grupo,
            'curso': matricula.grupo.curso,
            'sesiones': sesiones,
            'sesiones_futuras': len(sesiones_futuras),
            'progreso': matricula.calificacion or 0
        }
        
        if sesiones_futuras:
            cursos_activos.append(curso_info)
        else:
            cursos_completados.append(curso_info)
    
    return render_template('intranet/mis_cursos.html',
                         cursos_activos=cursos_activos,
                         cursos_completados=cursos_completados)


@intranetModule.route('/mis-datos')
@login_required
@student_required
def mis_datos():
    """Página para que el alumno vea y edite sus datos personales."""
    return render_template('intranet/mis_datos.html', title='Mis Datos')


@intranetModule.route('/configuracion', methods=['GET', 'POST'])
@login_required
@student_required
def configuracion():
    """Configuración personalizada del dashboard del alumno."""
    dashboard_config = IntranetDashboard.query.filter_by(alumno_id=current_user.id).first()
    
    if not dashboard_config:
        dashboard_config = IntranetDashboard(alumno_id=current_user.id)
        db.session.add(dashboard_config)
        db.session.commit()

    form = DashboardConfigForm(obj=dashboard_config)

    if form.validate_on_submit():
        form.populate_obj(dashboard_config)
        try:
            db.session.commit()
            flash('Configuración guardada exitosamente.', 'success')
            return redirect(url_for('intranet.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar la configuración: {e}', 'danger')

    return render_template('intranet/configuracion.html',
                         form=form,
                         title='Configuración del Dashboard')


@intranetModule.route('/actividad')
@login_required
@student_required
def mi_actividad():
    """Historial de actividad del alumno."""
    alumno_id = current_user.id
    page = request.args.get('page', 1, type=int)
    
    actividades = ActividadAlumno.query.filter_by(
        alumno_id=alumno_id
    ).order_by(ActividadAlumno.fecha_actividad.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('intranet/mi_actividad.html',
                         actividades=actividades)
