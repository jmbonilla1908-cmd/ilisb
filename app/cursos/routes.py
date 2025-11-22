import json
from flask import render_template, request, jsonify, url_for, abort, flash, redirect
from flask_login import login_required, current_user
from app.cursos import bp
from werkzeug.exceptions import NotFound
from .models import Curso, Especializacion, Grupo, Sesion, db
from .forms import MatriculaForm # Importamos el nuevo formulario
from app.matriculas.models import AlumnoGrupo # Importar desde el módulo correcto

@bp.route('/cursos')
def lista_cursos():
    """Muestra la lista de cursos públicos con filtros por especialidad."""
    especializaciones = Especializacion.query.order_by(Especializacion.descripcion).all()
    
    # Obtener el ID de especialización del request si existe
    especializacion_id = request.args.get('especializacion_id', type=int)
    page = request.args.get('page', 1, type=int)

    query = Curso.query.order_by(Curso.nombre)
    if especializacion_id:
        # Filtrar cursos por especialización usando la relación muchos-a-muchos
        query = query.join(Curso.especializaciones).filter(Especializacion.id == especializacion_id)

    # Usamos el objeto de paginación de Flask-SQLAlchemy
    pagination = query.paginate(page=page, per_page=6, error_out=False)
    cursos = pagination.items

    return render_template('cursos/lista_cursos.html', title='Nuestros Cursos', cursos=cursos, especializaciones=especializaciones, pagination=pagination, especializacion_id=especializacion_id)

@bp.route('/curso/<slug>')
def detalle_curso(slug):
    """Muestra la página de detalle de un curso específico."""
    # Obtener la pestaña activa de la URL, por defecto 'overview'
    active_tab = request.args.get('tab', 'overview')
    # Usamos .first_or_404() para simplificar el manejo de errores si el curso no existe.
    curso = Curso.query.filter_by(slug=slug).first_or_404()

    form = MatriculaForm() # Creamos una instancia del formulario
    # Buscamos el primer grupo ACTIVO y CONFIRMADO para mostrar en la página.
    grupo_activo = curso.grupos.filter(
        Grupo.visible == True,
        Grupo.estado == 'CONFIRMADO'
    ).order_by(Grupo.fecha_inicio.asc()).first()

    return render_template('cursos/detalle_curso.html', 
                           title=curso.nombre, 
                           curso=curso, 
                           form=form, # Pasamos el formulario a la plantilla
                           grupo=grupo_activo,
                           active_tab=active_tab)
    
@bp.route('/curso/<slug>/matricular', methods=['POST'])
@login_required
def matricular_curso(slug):
    """Inscribe al alumno actual en un curso."""
    curso = Curso.query.filter_by(slug=slug).first_or_404()
    form = MatriculaForm()

    if not form.validate_on_submit():
        flash('Error de validación. Por favor, intente de nuevo.', 'danger')
        return redirect(url_for('cursos.detalle_curso', slug=slug))
    
    # Lógica corregida: Buscamos el primer grupo visible y confirmado para este curso.
    grupo_disponible = Grupo.query.filter(
        Grupo.id_curso == curso.id,
        Grupo.visible == True,
        Grupo.estado == 'CONFIRMADO'
    ).order_by(Grupo.fecha_inicio.asc()).first()

    if not grupo_disponible:
        flash('Lo sentimos, no hay grupos disponibles para este curso en este momento.', 'warning')
        return redirect(url_for('cursos.detalle_curso', slug=slug))

    # Verificamos si el alumno ya está inscrito
    inscripcion_existente = AlumnoGrupo.query.filter_by(alumno_id=current_user.id, grupo_id=grupo_disponible.id).first()
    if inscripcion_existente:
        flash('Ya te encuentras matriculado en este curso.', 'info')
        return redirect(url_for('cursos.detalle_curso', slug=slug))

    # Creamos la nueva inscripción
    nueva_inscripcion = AlumnoGrupo(alumno_id=current_user.id, grupo_id=grupo_disponible.id)
    db.session.add(nueva_inscripcion)
    db.session.commit()

    flash(f'¡Felicidades! Te has matriculado exitosamente en el curso "{curso.nombre}".', 'success')
    return redirect(url_for('intranet.mis_cursos'))