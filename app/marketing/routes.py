from flask import (render_template, request, jsonify,
                   current_app, redirect, url_for, flash)
from flask_login import login_required
from app.auth.decorators import admin_required
from .models import Anuncio, TipoAnuncio, AliadoEstrategico
from app import db
from .forms import AliadoForm
from . import bp


# =================== RUTAS PÚBLICAS ===================

@bp.route('/aliados')
def aliados_publicos():
    """Vista pública de aliados estratégicos."""
    aliados = AliadoEstrategico.obtener_activos()
    
    # Incrementar impresiones para todos los aliados mostrados
    for aliado in aliados:
        aliado.incrementar_impresiones()
    db.session.commit()
    
    return render_template('marketing/aliados_publicos.html', aliados=aliados)


@bp.route('/aliados-carousel')
def aliados_carousel():
    """Template parcial para carousel de aliados (usar en otras páginas)."""
    aliados = AliadoEstrategico.obtener_destacados(limite=12)
    
    # Incrementar impresiones
    for aliado in aliados:
        aliado.incrementar_impresiones()
    db.session.commit()
    
    return render_template('marketing/aliados_carousel.html', aliados=aliados)


@bp.route('/api/aliado/<int:aliado_id>/clic', methods=['POST'])
def registrar_clic_aliado(aliado_id):
    """API para registrar clic en aliado."""
    try:
        aliado = AliadoEstrategico.query.get_or_404(aliado_id)
        if aliado.activo:
            aliado.incrementar_clics()
            db.session.commit()
            return jsonify({'success': True, 'redirect_url': aliado.sitio_web})
        return jsonify({'error': 'Aliado no disponible'}), 404
    except Exception as e:
        current_app.logger.error(f'Error registrando clic aliado: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500


# =================== RUTAS ADMINISTRATIVAS ===================

@bp.route('/admin/aliados')
@login_required
@admin_required
def admin_aliados():
    """Vista administrativa de aliados estratégicos."""
    page = request.args.get('page', 1, type=int)
    aliados = AliadoEstrategico.query.order_by(
        AliadoEstrategico.orden_presentacion.asc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('marketing/admin_aliados.html', aliados=aliados)


@bp.route('/admin/aliado/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_aliado():
    """Crear nuevo aliado estratégico."""
    form = AliadoForm()
    if form.validate_on_submit():
        aliado = AliadoEstrategico()
        form.populate_obj(aliado)
        try:
            db.session.add(aliado)
            db.session.commit()
            flash('Aliado estratégico creado exitosamente', 'success')
            return redirect(url_for('marketing.admin_aliados'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creando aliado: {e}')
            flash('Error al crear aliado estratégico', 'danger')
    
    return render_template('marketing/form_aliado.html', form=form, title='Nuevo Aliado')


@bp.route('/admin/aliado/<int:aliado_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_aliado(aliado_id):
    """Editar aliado estratégico."""
    aliado = AliadoEstrategico.query.get_or_404(aliado_id)
    form = AliadoForm(obj=aliado)
    if form.validate_on_submit():
        try:
            form.populate_obj(aliado)
            db.session.commit()
            flash('Aliado estratégico actualizado exitosamente', 'success')
            return redirect(url_for('marketing.admin_aliados'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error actualizando aliado: {e}')
            flash('Error al actualizar aliado estratégico', 'danger')
    
    return render_template('marketing/form_aliado.html', form=form, title='Editar Aliado', aliado=aliado)


@bp.route('/api/aliado/<int:aliado_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_aliado(aliado_id):
    """API para activar/desactivar aliado."""
    try:
        aliado = AliadoEstrategico.query.get_or_404(aliado_id)
        aliado.activo = not aliado.activo
        db.session.commit()
        
        return jsonify({
            'success': True,
            'activo': aliado.activo,
            'message': 'Estado actualizado correctamente'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error toggleando aliado: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500


# =================== RUTAS DE ANUNCIOS ORIGINALES ===================


@bp.route('/admin/anuncios')
@login_required
@admin_required
def admin_anuncios():
    """Vista administrativa de todos los anuncios."""
    page = request.args.get('page', 1, type=int)
    anuncios = Anuncio.query.order_by(
        Anuncio.fecha_registro.desc()
    ).paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    tipos = TipoAnuncio.query.filter_by(activo=True).all()
    return render_template(
        'marketing/admin_anuncios.html',
        anuncios=anuncios,
        tipos=tipos
    )


@bp.route('/admin/tipos-anuncio')
@login_required
@admin_required
def admin_tipos_anuncio():
    """Vista administrativa de tipos de anuncio."""
    tipos = TipoAnuncio.query.all()
    return render_template(
        'marketing/admin_tipos.html',
        tipos=tipos
    )


@bp.route('/admin/anuncio/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_anuncio():
    """Crear nuevo anuncio."""
    if request.method == 'POST':
        try:
            data = request.form
            anuncio = Anuncio(
                tipo_anuncio_id=data['tipo_anuncio_id'],
                titulo=data['titulo'],
                descripcion=data.get('descripcion'),
                imagen_url=data.get('imagen_url'),
                enlace_url=data.get('enlace_url'),
                fecha_fin=data.get('fecha_fin') or None,
                posicion=int(data.get('posicion', 1)),
                activo=bool(data.get('activo'))
            )
            db.session.add(anuncio)
            db.session.commit()
            flash('Anuncio creado exitosamente', 'success')
            return redirect(url_for('marketing.admin_anuncios'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creando anuncio: {e}')
            flash('Error al crear anuncio', 'danger')
    
    tipos = TipoAnuncio.query.filter_by(activo=True).all()
    return render_template(
        'marketing/nuevo_anuncio.html',
        tipos=tipos
    )


@bp.route('/api/anuncio/<int:anuncio_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_anuncio(anuncio_id):
    """API para activar/desactivar anuncio."""
    try:
        anuncio = Anuncio.query.get_or_404(anuncio_id)
        anuncio.activo = not anuncio.activo
        db.session.commit()
        
        return jsonify({
            'success': True,
            'activo': anuncio.activo,
            'message': 'Estado actualizado correctamente'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error toggleando anuncio: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500


@bp.route('/api/anuncio/<int:anuncio_id>/clic', methods=['POST'])
def registrar_clic(anuncio_id):
    """API pública para registrar clic en anuncio."""
    try:
        anuncio = Anuncio.query.get_or_404(anuncio_id)
        if anuncio.activo and anuncio.esta_vigente:
            anuncio.incrementar_clics()
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'error': 'Anuncio no disponible'}), 404
    except Exception as e:
        current_app.logger.error(f'Error registrando clic: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500


@bp.route('/anuncios/<tipo>')
def anuncios_publicos(tipo):
    """API pública para obtener anuncios por tipo."""
    try:
        tipo_obj = TipoAnuncio.query.filter_by(
            nombre=tipo, activo=True
        ).first_or_404()
        
        anuncios = Anuncio.query.filter_by(
            tipo_anuncio_id=tipo_obj.id,
            activo=True
        ).filter(
            db.and_(
                Anuncio.fecha_inicio <= db.func.now(),
                db.or_(
                    Anuncio.fecha_fin.is_(None),
                    Anuncio.fecha_fin >= db.func.now()
                )
            )
        ).order_by(Anuncio.posicion.asc()).all()
        
        # Incrementar impresiones
        for anuncio in anuncios:
            anuncio.incrementar_impresiones()
        db.session.commit()
        
        return render_template(
            'marketing/anuncios_publicos.html',
            anuncios=anuncios,
            tipo=tipo
        )
    except Exception as e:
        current_app.logger.error(f'Error obteniendo anuncios: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500
