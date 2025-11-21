import json
from flask import render_template, request, jsonify, url_for, abort
from app.cursos import bp
from .models import Curso, Especializacion, Grupo, Sesion, db
from werkzeug.exceptions import NotFound
from app import htmx # Importamos la extensión htmx

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
    # Usamos .first_or_404() para simplificar el manejo de errores si el curso no existe.
    curso = Curso.query.filter_by(slug=slug).first_or_404()

    # Buscamos el primer grupo visible para este curso.
    # En el futuro, podrías tener una lógica más compleja para seleccionar el grupo
    # (por ejemplo, el más próximo a empezar).
    grupo_activo = curso.grupos.filter_by(visible=True).order_by(Grupo.id.desc()).first()

    # Pasamos tanto el 'curso' como el 'grupo_activo' a la plantilla.
    # La plantilla principal ahora solo necesita el curso y el grupo para el layout.
    # El contenido de la primera pestaña se cargará a través de HTMX.
    return render_template('cursos/detalle_curso.html', title=curso.nombre, curso=curso, grupo=grupo_activo)

@bp.route('/curso/<slug>/<tab>')
def curso_tab(slug, tab):
    """Devuelve el fragmento de HTML para una pestaña específica del curso."""
    if not htmx:
        # Esta ruta solo debe ser accesible a través de peticiones HTMX.
        abort(400, "Esta URL solo responde a peticiones HTMX.")

    curso = Curso.query.filter_by(slug=slug).first_or_404()
    grupo_activo = curso.grupos.filter_by(visible=True).order_by(Grupo.id.desc()).first()

    # Mapeo de pestañas a plantillas parciales
    template_map = {
        'overview': 'cursos/_tab_overview.html',
        'contenido': 'cursos/_tab_contenido.html',
        'instructor': 'cursos/_tab_instructor.html',
        'horarios': 'cursos/_tab_horarios.html',
        'pagos': 'cursos/_tab_pagos.html',
    }

    template = template_map.get(tab, '404.html') # Devuelve 404 si la pestaña no es válida
    return render_template(template, curso=curso, grupo=grupo_activo)