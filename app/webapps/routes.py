from flask import (render_template, redirect, url_for, flash, request, 
                   jsonify, current_app)
from flask_login import login_required, current_user
from decimal import Decimal, getcontext
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from app.auth.decorators import admin_required
from . import bp
from .models import Aplicativo, TipoAplicativo
from app import db

# --- LÓGICA PARA EL CONVERSOR DE UNIDADES ---

# Precisión para los cálculos
getcontext().prec = 50

ACCESORIOS = {
    'valvulas': {
        'nombre': 'Válvulas',
        'items': {
            'valv_compuerta': {'nombre': 'Válvula de Compuerta (Abierta)', 'K': 0.15, 'imagen': 'img/accesorios/valv_compuerta.jpg'},
            'valv_bola': {'nombre': 'Válvula de Bola (Abierta)', 'K': 0.05, 'imagen': 'img/accesorios/valv_bola.jpg'},
            'valv_globo': {'nombre': 'Válvula de Globo (Abierta)', 'K': 6.0, 'imagen': 'img/accesorios/valv_globo.jpg'},
            'valv_check_clapeta': {'nombre': 'Válvula Check (Clapeta)', 'K': 2.0, 'imagen': 'img/accesorios/valv_check_clapeta.jpg'},
            'valv_check_bola': {'nombre': 'Válvula Check (de Bola)', 'K': 4.0, 'imagen': 'img/accesorios/valv_check_bola.jpg'},
            'valv_mariposa': {'nombre': 'Válvula Mariposa (Abierta)', 'K': 0.3, 'imagen': 'img/accesorios/valv_mariposa.jpg'},
            'valv_pie': {'nombre': 'Válvula de Pie', 'K': 1.75, 'imagen': 'img/accesorios/valv_pie.jpg'},
        }
    },
    'codos': {
        'nombre': 'Codos y Curvas',
        'items': {
            'codo_90_rl': {'nombre': 'Codo 90° (Radio Largo)', 'K': 0.2, 'imagen': 'img/accesorios/codo_90_rl.jpg'},
            'codo_90_rc': {'nombre': 'Codo 90° (Radio Corto)', 'K': 0.3, 'imagen': 'img/accesorios/codo_90_rc.jpg'},
            'codo_45': {'nombre': 'Codo 45°', 'K': 0.15, 'imagen': 'img/accesorios/codo_45.jpg'},
            'curva_180': {'nombre': 'Curva 180°', 'K': 0.4, 'imagen': 'img/accesorios/curva_180.jpg'},
        }
    },
    'uniones': {
        'nombre': 'Tees y Uniones',
        'items': {
            'tee_linea': {'nombre': 'Tee (Flujo en línea)', 'K': 0.4, 'imagen': 'img/accesorios/tee_linea.jpg'},
            'tee_derivacion': {'nombre': 'Tee (Flujo en derivación)', 'K': 1.0, 'imagen': 'img/accesorios/tee_derivacion.jpg'},
        }
    },
    'transiciones': {
        'nombre': 'Reducciones y Ampliaciones',
        'items': {
            'entrada_normal': {'nombre': 'Entrada Normal a Tubería', 'K': 0.5, 'imagen': 'img/accesorios/entrada_normal.jpg'},
            'salida_tuberia': {'nombre': 'Salida de Tubería', 'K': 1.0, 'imagen': 'img/accesorios/salida_tuberia.jpg'},
        }
    }
}

UNIDADES_CONVERSION = {
    'caudal': {
        'nombre': 'Caudal',
        'base_si': 'm3/s',
        'unidades': {
            'm3/s': {'nombre': 'm³/s', 'factor': Decimal('1')},
            'm3/h': {'nombre': 'm³/h', 'factor': Decimal('3600')},
            'l/s': {'nombre': 'L/s', 'factor': Decimal('1000')},
            'gpm_us': {'nombre': 'GPM (US)', 'factor': Decimal('15850.32314')},
        }
    },
    'presion': {
        'nombre': 'Presión',
        'base_si': 'Pa',
        'unidades': {
            'Pa': {'nombre': 'Pascal (Pa)', 'factor': Decimal('1')},
            'bar': {'nombre': 'bar', 'factor': Decimal('0.00001')},
            'psi': {'nombre': 'psi', 'factor': Decimal('0.000145038')},
            'atm': {'nombre': 'atm', 'factor': Decimal('0.00000986923')},
            'mca': {'nombre': 'm.c.a.', 'factor': Decimal('0.000101972')},
        }
    },
    'potencia': {
        'nombre': 'Potencia',
        'base_si': 'W',
        'unidades': {
            'W': {'nombre': 'Watt (W)', 'factor': Decimal('1')},
            'kW': {'nombre': 'Kilowatt (kW)', 'factor': Decimal('0.001')},
            'hp': {'nombre': 'HP (mecánico)', 'factor': Decimal('0.00134102')},
            'cv': {'nombre': 'CV (métrico)', 'factor': Decimal('0.00135962')},
        }
    },
    'longitud': {
        'nombre': 'Longitud',
        'base_si': 'm',
        'unidades': {
            'm': {'nombre': 'Metro (m)', 'factor': Decimal('1')},
            'km': {'nombre': 'Kilómetro (km)', 'factor': Decimal('0.001')},
            'cm': {'nombre': 'Centímetro (cm)', 'factor': Decimal('100')},
            'mm': {'nombre': 'Milímetro (mm)', 'factor': Decimal('1000')},
            'ft': {'nombre': 'Pie (ft)', 'factor': Decimal('3.28084')},
            'in': {'nombre': 'Pulgada (in)', 'factor': Decimal('39.3701')},
        }
    }
    # ... Se pueden añadir más magnitudes aquí (volumen, área, etc.)
}

def convertir_unidades(valor, unidad_origen, magnitud):
    """
    Realiza la conversión de una magnitud a todas sus unidades definidas.
    """
    if magnitud not in UNIDADES_CONVERSION or unidad_origen not in UNIDADES_CONVERSION[magnitud]['unidades']:
        return None

    config = UNIDADES_CONVERSION[magnitud]
    factor_origen = config['unidades'][unidad_origen]['factor']
    
    # 1. Convertir el valor de entrada a la unidad base del SI
    valor_base_si = Decimal(valor) / factor_origen

    # 2. Convertir el valor base a todas las demás unidades
    resultados = {}
    for slug, datos_unidad in config['unidades'].items():
        resultados[slug] = valor_base_si * datos_unidad['factor']
    
    return resultados


# --- Rutas existentes ---


@bp.route('/')
def index():
    """Página principal de aplicativos web."""
    populares = Aplicativo.obtener_populares(limite=6)
    recientes = Aplicativo.obtener_recientes(limite=6)
    return render_template('webapps/index.html', populares=populares, recientes=recientes)


@bp.route('/tipo/<slug>')
def por_tipo(slug):
    """Aplicativos filtrados por tipo."""
    # Buscamos el tipo de aplicativo
    tipo = TipoAplicativo.query.filter(db.func.lower(db.func.replace(TipoAplicativo.nombre, ' ', '-')) == slug.lower()).first_or_404()
    
    # Buscamos el primer aplicativo activo en esa categoría
    primer_aplicativo = Aplicativo.query.filter_by(tipo_aplicativo_id=tipo.id, activo=True).order_by(Aplicativo.orden).first()
    
    if primer_aplicativo:
        # Si encontramos uno, redirigimos directamente a él.
        return redirect(url_for('webapps.aplicativo_detail', slug=primer_aplicativo.slug))
    
    # Si no hay aplicativos en esa categoría, mostramos un mensaje (aunque la lógica del menú ya lo previene).
    flash('No hay aplicativos disponibles en esta categoría.', 'warning')
    return redirect(url_for('webapps.index'))


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
    
    # --- LÓGICA MEJORADA ---
    # Si el aplicativo tiene un archivo de plantilla específico, lo usamos.
    if aplicativo.template_file:
        # Pasamos el 'aplicativo' por si la plantilla específica lo necesita.
        # Para la calculadora, también pasamos el gráfico inicial.
        if aplicativo.template_file == 'webapps/calculadora_curva.html':
            # Obtenemos el valor de eficiencia del formulario, con 75 como valor por defecto.
            eficiencia = request.args.get('eficiencia', 75, type=float)

            # Obtenemos los parámetros del sistema del formulario de abajo
            altura_estatica = request.args.get('altura_estatica', 15.0, type=float)
            q_operacion = request.args.get('q_operacion', 40.0, type=float)
            h_operacion = request.args.get('h_operacion', 35.0, type=float)

            # Generar la explicación para la curva del sistema
            explicacion_sistema = None
            if 'calcular' in request.args:
                try:
                    if q_operacion > 0 and h_operacion > altura_estatica:
                        K = (h_operacion - altura_estatica) / (q_operacion**2)
                        explicacion_sistema = {
                            'ecuacion': f"H_sistema = {altura_estatica:.2f} + {K:.4f} * Q²",
                            'k_valor': f"{K:.4f}"
                        }
                except (ValueError, ZeroDivisionError):
                    pass # No se genera explicación si los datos son inválidos

            # Generar explicación para el BEP
            explicacion_bep = None
            if eficiencia > 0:
                 # Lógica de ejemplo: BEP al X% del caudal máximo
                caudal_max_bomba = 60 # Asumimos el caudal máximo de la curva de bomba fija
                caudal_bep = (eficiencia / 100) * caudal_max_bomba
                explicacion_bep = {
                    'eficiencia': f"{eficiencia:.0f}%",
                    'caudal_bep': f"{caudal_bep:.2f} m³/h"
                }

            # Generamos el gráfico SIEMPRE con el JS incluido, para no depender de scripts externos.
            initial_graph_html = _crear_grafico_interactivo(
                eficiencia_pct=eficiencia, incluir_js=True,
                altura_estatica=altura_estatica,
                q_operacion=q_operacion,
                h_operacion=h_operacion
            )
            return render_template(aplicativo.template_file, aplicativo=aplicativo, graph_html=initial_graph_html, explicacion_sistema=explicacion_sistema, explicacion_bep=explicacion_bep)
        
        elif aplicativo.template_file == 'webapps/calculadora_perdidas.html':
            resultados = None
            graph_html = None
            if 'calcular' in request.args:
                try:
                    # Recoger datos del formulario
                    Q_lps = request.args.get('caudal', type=float)
                    D_mm = request.args.get('diametro', type=float)
                    L_m = request.args.get('longitud', type=float)
                    C = request.args.get('coeficiente_c', type=float)

                    # Conversión de unidades
                    Q_m3s = Q_lps / 1000  # Caudal a m³/s
                    D_m = D_mm / 1000    # Diámetro a m

                    # Cálculo de Hazen-Williams
                    # S = (Q / (0.278 * C * D^2.63))^1.85
                    S = (Q_m3s / (0.2785 * C * (D_m**2.63)))**1.852
                    hf = S * L_m

                    resultados = {'hf': hf, 'S': S}

                    # Generar el gráfico
                    graph_html = _crear_grafico_perdidas(
                        Q_calculado_lps=Q_lps, hf_calculado_m=hf,
                        D_m=D_m, L_m=L_m, C=C, incluir_js=True
                    )
                except (ValueError, TypeError, ZeroDivisionError):
                    flash('Por favor, ingrese valores numéricos válidos y mayores que cero.', 'danger')
            
            return render_template(aplicativo.template_file, aplicativo=aplicativo, resultados=resultados, graph_html=graph_html)

        elif aplicativo.template_file == 'webapps/calculadora_perdida_accesorios.html':
            resultados = None
            # Solo calculamos si hay algún valor en la URL
            if request.args:
                try:
                    # 1. Recoger datos de la tubería
                    Q_m3h = request.args.get('caudal', type=float)
                    D_mm = request.args.get('diametro', type=float)
                    L_m = request.args.get('longitud', type=float)
                    C = request.args.get('coeficiente_c', type=float)

                    # 2. Conversión de unidades y cálculos básicos
                    Q_m3s = Q_m3h / 3600
                    D_m = D_mm / 1000
                    area = np.pi * (D_m**2) / 4
                    velocidad = Q_m3s / area
                    g = 9.81

                    # 3. Cálculo de pérdida por fricción (Hazen-Williams)
                    S = (Q_m3s / (0.2785 * C * (D_m**2.63)))**1.852
                    hf_tuberia = S * L_m

                    # 4. Cálculo de pérdidas menores (accesorios)
                    hf_accesorios = 0
                    K_total = 0
                    for cat_slug, categoria in ACCESORIOS.items():
                        for acc_slug, acc in categoria['items'].items():
                            cantidad = request.args.get(f'acc_{acc_slug}', 0, type=int)
                            if cantidad > 0:
                                K_total += acc['K'] * cantidad
                    
                    hf_accesorios = K_total * (velocidad**2) / (2 * g)

                    # 5. Resultados finales
                    resultados = {
                        'hf_tuberia': hf_tuberia,
                        'hf_accesorios': hf_accesorios,
                        'hf_total': hf_tuberia + hf_accesorios,
                        'velocidad': velocidad
                    }

                except (ValueError, TypeError, ZeroDivisionError):
                    flash('Por favor, ingrese valores numéricos válidos para el cálculo.', 'danger')
                    resultados = None

            return render_template(aplicativo.template_file, aplicativo=aplicativo, accesorios=ACCESORIOS, resultados=resultados)

        elif aplicativo.template_file == 'webapps/conversor_unidades.html':
            magnitud_activa = request.args.get('magnitud', 'caudal')
            if magnitud_activa not in UNIDADES_CONVERSION:
                magnitud_activa = 'caudal'

            valor_entrada = request.args.get('valor_entrada')
            unidad_origen = request.args.get('unidad_origen')
            
            resultados = None
            if valor_entrada and unidad_origen:
                try:
                    valor_decimal = Decimal(valor_entrada)
                    resultados = convertir_unidades(valor_decimal, unidad_origen, magnitud_activa)
                except Exception:
                    flash('Por favor, ingrese un valor numérico válido.', 'danger')

            return render_template(aplicativo.template_file, 
                                 aplicativo=aplicativo,
                                 unidades=UNIDADES_CONVERSION,
                                 magnitud_activa=magnitud_activa,
                                 valor_entrada=valor_entrada,
                                 unidad_origen=unidad_origen,
                                 resultados=resultados)

        return render_template(aplicativo.template_file, aplicativo=aplicativo)
    
    # Si no, mostramos la página de detalle genérica (comportamiento anterior).
    return render_template('webapps/aplicativo.html', aplicativo=aplicativo)


# --- NUEVAS RUTAS PARA LA CALCULADORA INTERACTIVA CON PLOTLY Y HTMX ---

def _crear_grafico_perdidas(Q_calculado_lps, hf_calculado_m, D_m, L_m, C, incluir_js=False):
    """Genera un gráfico de Plotly para la curva de pérdidas por fricción."""
    fig = go.Figure()

    # Generar puntos para la curva del sistema
    q_max_grafico = Q_calculado_lps * 1.5
    caudal_rango_lps = np.linspace(0, q_max_grafico, 50)
    caudal_rango_m3s = caudal_rango_lps / 1000

    # Evitar división por cero
    with np.errstate(divide='ignore', invalid='ignore'):
        S_rango = (caudal_rango_m3s / (0.2785 * C * (D_m**2.63)))**1.852
        hf_rango = S_rango * L_m

    # Añadir la curva de pérdidas
    fig.add_trace(go.Scatter(
        x=caudal_rango_lps,
        y=hf_rango,
        mode='lines',
        name='Curva de Pérdidas',
        line=dict(color='darkblue')
    ))

    # Marcar el punto de operación calculado
    fig.add_trace(go.Scatter(
        x=[Q_calculado_lps],
        y=[hf_calculado_m],
        mode='markers',
        name='Punto de Operación',
        marker=dict(color='crimson', size=12, symbol='x')
    ))

    fig.update_layout(
        title="Curva de Pérdidas por Fricción vs. Caudal",
        xaxis_title="Caudal (L/s)",
        yaxis_title="Pérdida de Carga (m)",
        template="plotly_white"
    )
    return pio.to_html(fig, full_html=False, include_plotlyjs=incluir_js)

def _crear_grafico_interactivo(eficiencia_pct=None, incluir_js=False, altura_estatica=None, q_operacion=None, h_operacion=None):
    # Volvemos a usar una curva de bomba fija para el ejemplo.
    caudal_puntos = [0, 10, 20, 30, 40, 50, 60]
    altura_puntos = [60, 58, 52, 45, 35, 23, 10]

    fig = go.Figure()

    # Añadir la curva principal de la bomba
    fig.add_trace(go.Scatter(
        x=caudal_puntos, 
        y=altura_puntos, 
        mode='lines+markers', 
        name='Curva H-Q',
        line=dict(shape='spline', smoothing=1.3) # Curva suave
    ))

    # Si se pasa una eficiencia, calcular y marcar el BEP
    if eficiencia_pct is not None and 0 < eficiencia_pct <= 100:
        try:
            # Lógica de ejemplo: BEP al X% del caudal máximo
            caudal_bep = (eficiencia_pct / 100) * max(caudal_puntos)
            # Interpolación lineal simple para encontrar la altura
            altura_bep = np.interp(caudal_bep, caudal_puntos, altura_puntos)
            
            fig.add_trace(go.Scatter(
                x=[caudal_bep], 
                y=[altura_bep], 
                mode='markers', 
                name=f'BEP ({eficiencia_pct}%)',
                marker=dict(color='red', size=12, symbol='star')
            ))
        except (ValueError, IndexError):
            pass # No se muestra el punto si hay error

    # Si se proporcionan los parámetros del sistema, calcular y dibujar la curva.
    if all(v is not None for v in [altura_estatica, q_operacion, h_operacion]):
        try:
            # Para la curva del sistema H_sys = H_estatica + K*Q^2
            # Usamos el punto de operación para calcular la constante de fricción K.
            if q_operacion > 0 and h_operacion > altura_estatica:
                K = (h_operacion - altura_estatica) / (q_operacion**2)
                
                q_sistema = np.linspace(0, max(caudal_puntos) * 1.1, 50) # Generar puntos para la curva
                h_sistema = altura_estatica + K * (q_sistema**2)
                
                fig.add_trace(go.Scatter(
                    x=q_sistema,
                    y=h_sistema,
                    mode='lines',
                    name=f'Curva Sistema (K={K:.4f})',
                    line=dict(color='green', dash='dash')
                ))
            else:
                flash('Los datos del punto de operación no son válidos para calcular la curva del sistema.', 'warning')

        except (np.linalg.LinAlgError, ValueError, IndexError):
            # Si hay un error en el cálculo, simplemente no se dibuja la curva del sistema.
            pass

    # Configurar el diseño del gráfico
    fig.update_layout(
        title="Calculadora Interactiva de Curva de Bomba",
        xaxis_title="Caudal (m³/h)",
        yaxis_title="Altura (m)",
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=20, r=20, t=40, b=20) # Ajustar márgenes
    )
    
    # Convertir a HTML. include_plotlyjs=False es importante para las actualizaciones de HTMX
    return pio.to_html(fig, full_html=False, include_plotlyjs=incluir_js)


# --- Rutas existentes (continuación) ---


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
