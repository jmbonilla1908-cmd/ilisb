from flask import (render_template, redirect, url_for, flash, request, 
                   jsonify, current_app)
from flask_login import login_required, current_user
import numpy as np
from app.auth.decorators import admin_required
from app.webapps import bp
from .models import Aplicativo, TipoAplicativo
from app import db


@bp.route('/')
def index():
    """Página principal de aplicativos web."""
    tipos = TipoAplicativo.query.filter_by(activo=True).all()
    populares = Aplicativo.obtener_populares(limite=6)
    recientes = Aplicativo.obtener_recientes(limite=6)
    return render_template('webapps/index.html', 
                         tipos=tipos, populares=populares, recientes=recientes)


@bp.route('/tipo/<int:tipo_id>')
def por_tipo(tipo_id):
    """Aplicativos filtrados por tipo."""
    tipo = TipoAplicativo.query.get_or_404(tipo_id)
    aplicativos = Aplicativo.obtener_por_tipo(tipo_id)
    return render_template('webapps/por_tipo.html', 
                         tipo=tipo, aplicativos=aplicativos)


@bp.route('/<slug>')
def aplicativo_detail(slug):
    """Vista detalle de un aplicativo específico."""
    aplicativo = Aplicativo.query.filter(
        db.func.lower(db.func.replace(
            db.func.replace(Aplicativo.nombre, ' ', '-'), 
            '_', '-'
        )) == slug.lower()
    ).first_or_404()
    
    # Verificar acceso
    if aplicativo.requiere_membresia and not hasattr(current_user, 'es_miembro_activo'):
        flash('Necesitas una membresía activa para acceder a esta herramienta.')
        return redirect(url_for('core.membresia'))
    
    if aplicativo.es_premium and not hasattr(current_user, 'es_premium'):
        flash('Esta herramienta requiere membresía premium.')
        return redirect(url_for('core.premium'))
    
    # Incrementar vistas
    aplicativo.incrementar_vistas()
    
    return render_template('webapps/aplicativo.html', aplicativo=aplicativo)


@bp.route('/curvas-bomba')
@login_required
def curvas_bomba():
    """Calculadora de curvas de bomba - compatibilidad con código existente."""
    if not current_user.es_miembro_activo:
        flash('Necesitas una membresía activa para acceder a esta herramienta.')
        return redirect(url_for('core.membresia'))
    
    tipos = TipoAplicativo.query.filter_by(activo=True).order_by(TipoAplicativo.nombre).all()
    
    return render_template('webapps/curvas.html', tipos=tipos, tipo=None)


@bp.route('/api/calcular-curvas', methods=['POST'])
@login_required
def calcular_curvas():
    """
    API endpoint para procesar los datos de la calculadora de curvas de bomba.
    Recibe los datos del formulario en JSON y devuelve los puntos para las gráficas.
    """
    if not current_user.is_authenticated or not hasattr(current_user, 'es_miembro_activo'):
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        data = request.json
        puntos_bomba = data.get('puntos_bomba', [])

        if len(puntos_bomba) < 3:
            return jsonify({'success': False, 'error': 'Se necesitan al menos 3 puntos para el cálculo.'}), 400

        # Extraer los puntos Q (caudal) y H (altura)
        q_vals = [p['q'] for p in puntos_bomba]
        h_vals = [p['h'] for p in puntos_bomba]

        # --- Lógica de Cálculo con NumPy ---
        # Ajustar un polinomio de 2º grado (H = a*Q^2 + b*Q + c)
        # Esto nos da los coeficientes de la ecuación de la curva de la bomba
        coeficientes = np.polyfit(q_vals, h_vals, 2)
        polinomio = np.poly1d(coeficientes)

        # Generar puntos para la curva de la bomba para graficar
        q_max = max(q_vals)
        q_grafico = np.linspace(0, q_max, 50)  # 50 puntos para una curva suave
        h_grafico = polinomio(q_grafico)

        puntos_curva_bomba = [{'x': round(q, 2), 'y': round(h, 2)} for q, h in zip(q_grafico, h_grafico)]

        # --- Lógica para la curva del sistema (simplificada por ahora) ---
        # H_sistema = hk + K * Q^2
        hk = data.get('datos_instalacion', {}).get('altura_estatica', 0)
        q_op = data.get('punto_operacion', {}).get('q', 0)
        h_op = data.get('punto_operacion', {}).get('h', 0)
        
        # Calcular la constante K del sistema
        K = (h_op - hk) / (q_op**2) if q_op > 0 else 0
        h_sistema_grafico = hk + K * (q_grafico**2)
        puntos_curva_sistema = [{'x': round(q, 2), 'y': round(h, 2)} for q, h in zip(q_grafico, h_sistema_grafico)]

        return jsonify({'success': True, 'puntos_curva_bomba': puntos_curva_bomba, 'puntos_curva_sistema': puntos_curva_sistema})

    except Exception as e:
        current_app.logger.error(f"Error en el cálculo de curvas: {e}")
        return jsonify({'success': False, 'error': 'Ocurrió un error durante el cálculo.'}), 500


@bp.route('/admin/aplicativos')
@login_required
@admin_required
def admin_aplicativos():
    """Vista administrativa de aplicativos."""
    page = request.args.get('page', 1, type=int)
    aplicativos = Aplicativo.query.order_by(
        Aplicativo.fecha_registro.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    tipos = TipoAplicativo.query.filter_by(activo=True).all()
    return render_template('webapps/admin_aplicativos.html',
                         aplicativos=aplicativos, tipos=tipos)


@bp.route('/admin/tipos-aplicativo')
@login_required
@admin_required
def admin_tipos():
    """Vista administrativa de tipos de aplicativo."""
    tipos = TipoAplicativo.query.all()
    return render_template('webapps/admin_tipos.html', tipos=tipos)


@bp.route('/api/aplicativo/<int:aplicativo_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_aplicativo(aplicativo_id):
    """API para activar/desactivar aplicativo."""
    try:
        aplicativo = Aplicativo.query.get_or_404(aplicativo_id)
        aplicativo.activo = not aplicativo.activo
        db.session.commit()
        
        return jsonify({
            'success': True,
            'activo': aplicativo.activo,
            'message': 'Estado actualizado correctamente'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error toggleando aplicativo: {e}')
        return jsonify({'error': 'Error interno del servidor'}), 500
