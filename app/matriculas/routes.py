from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.auth.decorators import student_required, admin_required
# Importamos el blueprint 'bp' desde el __init__.py del módulo
from app.matriculas import bp
from .models import AlumnoGrupo #, AlumnoMembresia
from app import db


@bp.route('/mis-cursos')
@login_required
@student_required
def mis_cursos():
    """Vista de cursos del alumno matriculado."""
    alumno_id = current_user.id
    matriculas = AlumnoGrupo.query.filter_by(alumno_id=alumno_id).all()
    return render_template(
        'matriculas/mis_cursos.html',
        matriculas=matriculas
    )


# @bp.route('/mi-membresia')
# @login_required
# @student_required
# def mi_membresia():
#     """Vista de membresía activa del alumno."""
#     alumno_id = current_user.id
#     membresia = AlumnoMembresia.query.filter_by(
#         alumno_id=alumno_id,
#         revertido=False
#     ).order_by(AlumnoMembresia.fecha_inicio.desc()).first()
#     return render_template(
#         'matriculas/mi_membresia.html',
#         membresia=membresia
#     )



@bp.route('/admin/matriculas')
@login_required
@admin_required
def admin_matriculas():
    """Vista administrativa de todas las matrículas."""
    page = request.args.get('page', 1, type=int)
    matriculas = AlumnoGrupo.query.paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    return render_template(
        'matriculas/admin_matriculas.html',
        matriculas=matriculas
    )


# @bp.route('/admin/membresias')
# @login_required
# @admin_required
# def admin_membresias():
#     """Vista administrativa de todas las membresías."""
#     page = request.args.get('page', 1, type=int)
#     membresias = AlumnoMembresia.query.paginate(
#         page=page,
#         per_page=20,
#         error_out=False
#     )
#     return render_template(
#         'matriculas/admin_membresias.html',
#         membresias=membresias
#     )



@bp.route('/api/matricula/<int:matricula_id>/calificacion',
                     methods=['POST'])
@login_required
@admin_required
def actualizar_calificacion(matricula_id):
    """API para actualizar calificación de una matrícula."""
    try:
        matricula = AlumnoGrupo.query.get_or_404(matricula_id)
        data = request.get_json()
        calificacion = data.get('calificacion')
        
        if calificacion is None or not (0 <= float(calificacion) <= 20):
            return jsonify({
                'error': 'Calificación debe estar entre 0 y 20'
            }), 400
        
        matricula.calificacion = calificacion
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Calificación actualizada correctamente'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error actualizando calificación: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500


# @bp.route('/api/membresia/<int:membresia_id>/revertir',
#                      methods=['POST'])
# @login_required
# @admin_required
# def revertir_membresia(membresia_id):
#     """API para revertir una membresía."""
#     try:
#         membresia = AlumnoMembresia.query.get_or_404(membresia_id)
#         membresia.revertido = True
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Membresía revertida correctamente'
#         })
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f'Error revirtiendo membresía: {e}')
#         return jsonify({'error': 'Error interno del servidor'}), 500