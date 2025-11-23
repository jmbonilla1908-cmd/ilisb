from flask import (render_template, redirect, url_for, flash, request, 
                   jsonify, current_app)
from flask_login import login_required, current_user
from decimal import Decimal, getcontext
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import base64
from app.auth.decorators import admin_required
from . import bp
from .models import Aplicativo, TipoAplicativo
from app import db

# --- LÓGICA PARA EL CONVERSOR DE UNIDADES ---

# Precisión para los cálculos
getcontext().prec = 50

# --- DATOS PARA SELECCIÓN DE CABLE ---

# Tabla de cables de cobre (AWG, mm², Resistencia Ohm/km @ 20°C, Ampacidad @ 30°C)
TABLA_CABLES = [
    {'awg': '14', 'mm2': 2.08, 'resistencia': 8.45, 'ampacidad': 25},
    {'awg': '12', 'mm2': 3.31, 'resistencia': 5.31, 'ampacidad': 30},
    {'awg': '10', 'mm2': 5.26, 'resistencia': 3.34, 'ampacidad': 40},
    {'awg': '8', 'mm2': 8.37, 'resistencia': 2.1, 'ampacidad': 55},
    {'awg': '6', 'mm2': 13.3, 'resistencia': 1.32, 'ampacidad': 75},
    {'awg': '4', 'mm2': 21.15, 'resistencia': 0.83, 'ampacidad': 95},
    {'awg': '2', 'mm2': 33.62, 'resistencia': 0.52, 'ampacidad': 130},
    {'awg': '1', 'mm2': 42.41, 'resistencia': 0.41, 'ampacidad': 150},
    {'awg': '1/0', 'mm2': 53.49, 'resistencia': 0.33, 'ampacidad': 170},
    {'awg': '2/0', 'mm2': 67.43, 'resistencia': 0.26, 'ampacidad': 195},
    {'awg': '3/0', 'mm2': 85.01, 'resistencia': 0.21, 'ampacidad': 225},
    {'awg': '4/0', 'mm2': 107.2, 'resistencia': 0.16, 'ampacidad': 260},
    {'awg': '250', 'mm2': 127, 'resistencia': 0.14, 'ampacidad': 290},
    {'awg': '300', 'mm2': 152, 'resistencia': 0.12, 'ampacidad': 320},
    {'awg': '350', 'mm2': 177, 'resistencia': 0.1, 'ampacidad': 350},
    {'awg': '400', 'mm2': 203, 'resistencia': 0.09, 'ampacidad': 380},
    {'awg': '500', 'mm2': 253, 'resistencia': 0.07, 'ampacidad': 430},
]

# Factores de corrección de temperatura para ampacidad
FACTORES_TEMP = {
    30: 1.0, 35: 0.94, 40: 0.88, 45: 0.82, 50: 0.75,
    55: 0.67, 60: 0.58, 65: 0.47, 70: 0.35, 75: 0.0
}

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
            'entrada_normal': {'nombre': 'Entrada Normal a Tubería', 'K': 0.5, 'imagen': 'img/accesorios/placeholder.svg'},
            'salida_tuberia': {'nombre': 'Salida de Tubería', 'K': 1.0, 'imagen': 'img/accesorios/placeholder.svg'},
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
    tipos_menu = TipoAplicativo.query.order_by(TipoAplicativo.orden).all()
    return render_template('webapps/index.html', populares=populares, recientes=recientes, tipos=tipos_menu)


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
    # Obtenemos todos los tipos para el menú lateral, ordenados por el nuevo campo 'orden'
    tipos_menu = TipoAplicativo.query.order_by(TipoAplicativo.orden).all()

    aplicativo = Aplicativo.query.join(TipoAplicativo).filter(
        db.func.lower(db.func.replace(
            db.func.replace(Aplicativo.nombre, ' ', '-'), 
            '_', '-'
        )) == slug.lower()
    ).first_or_404()
    
    # Verificar acceso
    if aplicativo.requiere_membresia and not (current_user.is_authenticated and hasattr(current_user, 'es_miembro_activo') and current_user.es_miembro_activo):
        flash('Necesitas una membresía activa para acceder a esta herramienta.')
        return redirect(url_for('core.membresia'))
    
    if aplicativo.es_premium and not (current_user.is_authenticated and hasattr(current_user, 'es_premium') and current_user.es_premium):
        flash('Esta herramienta requiere membresía premium.')
        return redirect(url_for('core.premium'))
    
    # Incrementar vistas
    aplicativo.incrementar_vistas()
    
    # --- LÓGICA MEJORADA ---
    # Si el aplicativo tiene un archivo de plantilla específico, lo usamos.
    if aplicativo.template_file:
        # Para la calculadora, también pasamos el gráfico inicial.
        if aplicativo.template_file == 'webapps/calculadora_curva_sistema.html':
            args = request.args.copy()
            
            # --- Lógica para añadir/quitar puntos de la curva de bomba ---
            q_bomba = args.getlist('q_bomba')
            h_bomba = args.getlist('h_bomba')

            if 'add_point' in args:
                q_bomba.append('')
                h_bomba.append('')
            elif 'remove_point' in args:
                if len(q_bomba) > 3: # Mantenemos un mínimo de 3 puntos
                    q_bomba.pop()
                    h_bomba.pop()
            
            # Si no hay puntos, inicializamos con 3 vacíos
            if not q_bomba:
                q_bomba = ['0', '150', '100']
                h_bomba = ['48', '30', '43']

            # Actualizamos los args para que la plantilla los repinte
            args.setlist('q_bomba', q_bomba)
            args.setlist('h_bomba', h_bomba)

            graph_html = "<div><p class='text-center p-5'>Ingrese los datos y haga clic en 'Graficar' para generar la curva.</p></div>"

            if 'calcular' in request.args:
                try:
                    # 1. Recopilar y limpiar puntos de la curva de la bomba
                    puntos_q = [float(q) for q in args.getlist('q_bomba') if q]
                    puntos_h = [float(h) for h in args.getlist('h_bomba') if h]

                    if len(puntos_q) < 3 or len(puntos_q) != len(puntos_h):
                        flash('Debe ingresar al menos 3 puntos (Q, H) válidos para la curva de la bomba.', 'warning')
                        return render_template(aplicativo.template_file, aplicativo=aplicativo, graph_html=graph_html, request=request, tipos=tipos_menu)

                    # 2. Recopilar datos del sistema
                    cota = float(args.get('cota', 28.1))
                    variacion_max = float(args.get('variacion_max', 6.0))
                    metodo_sistema = args.get('metodo_sistema', 'po')

                    # 3. Calcular K (coeficiente de resistencia del sistema)
                    K = 0
                    if metodo_sistema == 'po':
                        q_op = float(args.get('q_operacion', 120))
                        h_op = float(args.get('h_operacion', 38))
                        if q_op > 0 and h_op > cota:
                            K = (h_op - cota) / (q_op**2)
                        else:
                            flash('El punto de operación debe tener un caudal > 0 y una altura > altura estática.', 'warning')
                    else: # metodo_hf
                        q_hf = float(args.get('q_hf', 120))
                        h_hf = float(args.get('h_hf', 10))
                        if q_hf > 0:
                            K = h_hf / (q_hf**2)
                        else:
                            flash('El caudal para el cálculo de pérdidas debe ser > 0.', 'warning')

                    # 4. Recopilar datos interactivos
                    frecuencia_hz = float(args.get('frecuencia_hz', 60))
                    nivel_succion = float(args.get('nivel_succion', cota))

                    # 5. Generar el gráfico
                    graph_html = _crear_grafico_curva_sistema(
                        puntos_q=puntos_q,
                        puntos_h=puntos_h,
                        cota=cota,
                        variacion_max=variacion_max,
                        K=K,
                        frecuencia_actual=frecuencia_hz,
                        nivel_actual=nivel_succion,
                        incluir_js=True
                    )
                except (ValueError, TypeError, ZeroDivisionError) as e:
                    flash(f'Error en los datos de entrada: {e}. Por favor, verifique los valores.', 'danger')

            # Usamos los 'args' modificados para repintar el formulario
            return render_template(aplicativo.template_file, aplicativo=aplicativo, graph_html=graph_html, request=args, tipos=tipos_menu)

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
            
            return render_template(aplicativo.template_file, aplicativo=aplicativo, resultados=resultados, graph_html=graph_html, tipos=tipos_menu)

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

            graph_html = None
            if resultados:
                graph_html = _crear_grafico_perdidas_accesorios(resultados['hf_tuberia'], resultados['hf_accesorios'], incluir_js=True)

            return render_template(aplicativo.template_file, aplicativo=aplicativo, accesorios=ACCESORIOS, resultados=resultados, graph_html=graph_html, tipos=tipos_menu)


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
                                 resultados=resultados,
                                 tipos=tipos_menu)

        elif aplicativo.template_file == 'webapps/seleccion_cable_sumergible.html':
            resultados = None
            if 'calcular' in request.args:
                try:
                    # 1. Recopilar datos
                    alim = float(request.args.get('alim'))
                    volt = float(request.args.get('volt'))
                    amper = float(request.args.get('amper'))
                    f_potencia = float(request.args.get('f_potencia'))
                    temp = int(request.args.get('temperatura'))
                    t_arranque = float(request.args.get('t_arranque'))
                    long_cable = float(request.args.get('long_cable'))

                    # 2. Calcular amperaje corregido por temperatura
                    factor_temp = FACTORES_TEMP.get(temp - (temp % 5), 1.0) # Redondea hacia abajo al múltiplo de 5 más cercano
                    amperaje_corregido = amper / factor_temp if factor_temp > 0 else float('inf')

                    # 3. Calcular caída de voltaje para cada cable
                    tabla_resultados = []
                    for cable in TABLA_CABLES:
                        # Resistencia corregida por temperatura (cobre)
                        resistencia_corregida = cable['resistencia'] * (1 + 0.00393 * (temp - 20))
                        
                        # Caída de voltaje
                        caida_v = (alim * amper * long_cable * resistencia_corregida) / 1000
                        caida_porc = (caida_v / volt) * 100

                        # Determinar clase CSS para resaltar
                        clase = ''
                        if amperaje_corregido > cable['ampacidad']:
                            clase = 'table-danger'
                        elif caida_porc > 5.0:
                            clase = 'table-danger'
                        elif caida_porc > 3.0:
                            clase = 'table-warning'
                        else:
                            clase = 'table-success'

                        tabla_resultados.append({**cable, 'caida_voltaje': caida_porc, 'clase_css': clase})
                    
                    resultados = {
                        'amperaje_corregido': amperaje_corregido,
                        'tabla': tabla_resultados
                    }
                except (ValueError, TypeError, ZeroDivisionError) as e:
                    flash(f'Error en los datos de entrada: {e}. Por favor, verifique los valores.', 'danger')

            return render_template(aplicativo.template_file, aplicativo=aplicativo, resultados=resultados, tipos=tipos_menu)

        elif aplicativo.template_file == 'webapps/calculadora_sumergencia.html':
            resultados = None
            if 'calcular' in request.args:
                try:
                    # 1. Recopilar y estandarizar unidades
                    caudal_valor = float(request.args.get('caudal_valor'))
                    caudal_unidad = request.args.get('caudal_unidad')
                    diametro_valor = float(request.args.get('diametro_valor'))
                    diametro_unidad = request.args.get('diametro_unidad')

                    # Convertir todo a pies y ft³/s
                    if caudal_unidad == 'gpm':
                        Q_cfs = caudal_valor / 448.831
                    elif caudal_unidad == 'l/s':
                        Q_cfs = caudal_valor / 28.317
                    else: # m3/h
                        Q_cfs = caudal_valor / 101.94

                    if diametro_unidad == 'in':
                        D_ft = diametro_valor / 12
                    else: # mm
                        D_ft = diametro_valor / 304.8

                    # 2. Realizar cálculos
                    g = 32.2  # Aceleración de la gravedad en ft/s²
                    area = np.pi * (D_ft**2) / 4
                    V_fps = Q_cfs / area
                    Fr = V_fps / np.sqrt(g * D_ft) # Número de Froude

                    # Sumergencia mínima S = D * (1 + 2.3 * Fr)
                    S_ft = D_ft * (1 + 2.3 * Fr)

                    resultados = {
                        'S': S_ft * 12,      # Convertir a pulgadas para mostrar
                        'D': D_ft * 12,      # Convertir a pulgadas para mostrar
                        'C': (D_ft / 2) * 12, # C = D/2
                        'B': (D_ft * 1.5) * 12, # B = 1.5D
                        'V': V_fps,
                        'Fr': Fr
                    }
                except (ValueError, TypeError, ZeroDivisionError) as e:
                    flash(f'Error en los datos de entrada: {e}. Por favor, verifique los valores.', 'danger')
            
            return render_template(aplicativo.template_file, aplicativo=aplicativo, resultados=resultados, tipos=tipos_menu)

        return render_template(aplicativo.template_file, aplicativo=aplicativo, tipos=tipos_menu)
    
    # Si no, mostramos la página de detalle genérica (comportamiento anterior).
    return render_template('webapps/aplicativo.html', aplicativo=aplicativo, tipos=tipos_menu)


def _crear_grafico_curva_sistema(puntos_q, puntos_h, cota, variacion_max, K, frecuencia_actual, nivel_actual, incluir_js=False):
    fig = go.Figure()

    # 1. Ajustar curva de la bomba a un polinomio de 2do grado
    # H = A*Q^2 + B*Q + C
    coeffs = np.polyfit(puntos_q, puntos_h, 2)
    poly_bomba = np.poly1d(coeffs)

    # Generar puntos suaves para la curva de la bomba
    q_max_bomba = max(puntos_q)
    q_bomba_range = np.linspace(0, q_max_bomba, 100)
    h_bomba_range = poly_bomba(q_bomba_range)

    # Curva de la bomba a 60Hz (nominal)
    fig.add_trace(go.Scatter(x=q_bomba_range, y=h_bomba_range, mode='lines', name='Bomba @ 60Hz', line=dict(color='blue')))

    # 2. Curva de la bomba ajustada a la frecuencia actual
    ratio_frec = frecuencia_actual / 60.0
    q_bomba_adj = q_bomba_range * ratio_frec
    h_bomba_adj = h_bomba_range * (ratio_frec**2)
    fig.add_trace(go.Scatter(x=q_bomba_adj, y=h_bomba_adj, mode='lines', name=f'Bomba @ {frecuencia_actual}Hz', line=dict(color='red', dash='dash')))

    # 3. Curvas del sistema
    # H_sys = H_estatica + K*Q^2
    q_sistema_range = np.linspace(0, max(q_bomba_adj) * 1.1, 100)
    
    # Nivel máximo (altura estática mínima)
    h_sys_max = (cota - variacion_max) + K * (q_sistema_range**2)
    fig.add_trace(go.Scatter(x=q_sistema_range, y=h_sys_max, mode='lines', name='Sistema (Nivel Máx)', line=dict(color='orange', dash='dot')))

    # Nivel mínimo (altura estática máxima)
    h_sys_min = cota + K * (q_sistema_range**2)
    fig.add_trace(go.Scatter(x=q_sistema_range, y=h_sys_min, mode='lines', name='Sistema (Nivel Mín)', line=dict(color='brown', dash='dot')))

    # Nivel actual
    h_sys_actual = (cota - (cota - nivel_actual)) + K * (q_sistema_range**2)
    fig.add_trace(go.Scatter(x=q_sistema_range, y=h_sys_actual, mode='lines', name='Sistema (Nivel Actual)', line=dict(color='green', width=3)))

    # 4. Encontrar y marcar el punto de operación (intersección)
    # H_bomba_adj(Q) = H_sys_actual(Q) -> (A*r^2 - K)*Q^2 + (B*r)*Q + (C*r^2 - H_est_actual) = 0
    h_est_actual = (cota - (cota - nivel_actual))
    poly_interseccion = np.poly1d([coeffs[0]*(ratio_frec**2) - K, coeffs[1]*ratio_frec, coeffs[2]*(ratio_frec**2) - h_est_actual])
    raices = poly_interseccion.roots
    q_operacion_real = max(r.real for r in raices if r.imag == 0 and r.real > 0)
    if q_operacion_real:
        h_operacion_real = h_est_actual + K * (q_operacion_real**2)
        fig.add_trace(go.Scatter(x=[q_operacion_real], y=[h_operacion_real], mode='markers', name='Punto de Operación',
                                 marker=dict(color='purple', size=15, symbol='star')))

    # Puntos originales ingresados
    fig.add_trace(go.Scatter(x=puntos_q, y=puntos_h, mode='markers', name='Puntos Ingresados', marker=dict(color='grey')))

    fig.update_layout(
        title="Análisis de Curva de Bomba vs. Curva de Sistema",
        xaxis_title="Caudal (Q)",
        yaxis_title="Altura (H)",
        template="plotly_white"
    )
    return pio.to_html(fig, full_html=False, include_plotlyjs=incluir_js)

def _crear_grafico_perdidas_accesorios(hf_tuberia, hf_accesorios, incluir_js=False):
    """Genera un gráfico de pastel para la distribución de pérdidas."""
    labels = ['Pérdida por Fricción (Tubería)', 'Pérdidas Menores (Accesorios)']
    values = [hf_tuberia, hf_accesorios]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3,
                                 textinfo='label+percent',
                                 hovertemplate='<b>%{label}</b><br>Pérdida: %{value:.2f} m<br>Contribución: %{percent}<extra></extra>')])

    fig.update_layout(
        title_text="Distribución de Pérdidas de Carga",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )

    return pio.to_html(fig, full_html=False, include_plotlyjs=incluir_js)


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
