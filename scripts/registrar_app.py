import os
import sys
from slugify import slugify

# Añadir el directorio raíz del proyecto al path para poder importar la app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.webapps.models import Aplicativo, TipoAplicativo

# Usamos la configuración de desarrollo para el script
app = create_app('config.DevelopmentConfig')

def registrar_calculadora():
    with app.app_context():
        nombre_app = "Calculadora de Curva Interactiva"
        
        app_existente = Aplicativo.query.filter(Aplicativo.nombre == nombre_app).first()
        
        nombre_tipo = "Cálculos Hidráulicos"
        tipo = TipoAplicativo.query.filter_by(nombre=nombre_tipo).first()
        if not tipo:
            print(f"Creando nuevo tipo: '{nombre_tipo}'")
            tipo = TipoAplicativo(nombre=nombre_tipo, descripcion="Herramientas para cálculos hidráulicos en sistemas de bombeo.")
            db.session.add(tipo)
            db.session.flush()

        if app_existente:
            print(f"El aplicativo '{nombre_app}' ya existe. No se hacen cambios.")
        else:
            print(f"Creando nuevo aplicativo: '{nombre_app}'...")
            
            # --- SOLUCIÓN DEFINITIVA ---
            # Creamos el objeto y asignamos los valores explícitamente
            # para evitar cualquier ambigüedad con el constructor.
            nuevo_app = Aplicativo()
            nuevo_app.nombre = nombre_app # Esto se mapeará a 'nombreaplicativo'
            nuevo_app.descripcion_corta = "Visualiza la curva de una bomba y su punto de eficiencia (BEP)."
            nuevo_app.descripcion = "Usa el deslizador para cambiar el porcentaje de eficiencia y ver cómo se actualiza el Punto de Mejor Eficiencia (BEP) en el gráfico en tiempo real."
            nuevo_app.requiere_membresia = True
            nuevo_app.es_premium = False
            nuevo_app.template_file = 'webapps/calculadora_curva.html'
            nuevo_app.ruta_archivo = '' # Campo obligatorio
            nuevo_app.url_help = '' # Campo obligatorio
            nuevo_app.tipo_aplicativo_id = tipo.id # Campo obligatorio
            
            db.session.add(nuevo_app)
        
        db.session.commit()
        print("¡Operación completada exitosamente!")

def registrar_calculadora_perdidas():
    with app.app_context():
        nombre_app = "Calculadora de Pérdidas por Fricción"
        
        app_existente = Aplicativo.query.filter(Aplicativo.nombre == nombre_app).first()
        
        nombre_tipo = "Cálculos Hidráulicos"
        tipo = TipoAplicativo.query.filter_by(nombre=nombre_tipo).first()
        if not tipo:
            # Esto no debería pasar si ya ejecutaste el script antes, pero es una buena práctica.
            print(f"Creando nuevo tipo: '{nombre_tipo}'")
            tipo = TipoAplicativo(nombre=nombre_tipo, descripcion="Herramientas para cálculos hidráulicos en sistemas de bombeo.")
            db.session.add(tipo)
            db.session.flush()

        if app_existente:
            print(f"El aplicativo '{nombre_app}' ya existe. No se hacen cambios.")
        else:
            print(f"Creando nuevo aplicativo: '{nombre_app}'...")
            nuevo_app = Aplicativo(
                nombre=nombre_app,
                descripcion_corta="Estima la pérdida de carga en tuberías usando la ecuación de Hazen-Williams.",
                descripcion="Una herramienta esencial para el diseño de sistemas de tuberías. Ingrese los parámetros de la tubería y el caudal para calcular la pérdida de carga por fricción (hf) y el gradiente hidráulico (S).",
                requiere_membresia=True,
                template_file='webapps/calculadora_perdidas.html',
                ruta_archivo='',
                url_help='',
                tipo_aplicativo_id=tipo.id
            )
            db.session.add(nuevo_app)
            db.session.commit()
            print(f"¡Aplicativo '{nombre_app}' creado exitosamente!")

def registrar_conversor_unidades():
    with app.app_context():
        nombre_app = "Conversor de Unidades"
        app_existente = Aplicativo.query.filter(Aplicativo.nombre == nombre_app).first()

        nombre_tipo = "Conversores y Utilidades"
        tipo = TipoAplicativo.query.filter_by(nombre=nombre_tipo).first()
        if not tipo:
            print(f"Creando nuevo tipo: '{nombre_tipo}'")
            tipo = TipoAplicativo(nombre=nombre_tipo, descripcion="Herramientas de conversión y utilidades generales de ingeniería.")
            db.session.add(tipo)
            db.session.flush()

        if app_existente:
            print(f"El aplicativo '{nombre_app}' ya existe. No se hacen cambios.")
        else:
            print(f"Creando nuevo aplicativo: '{nombre_app}'...")
            nuevo_app = Aplicativo(
                nombre=nombre_app,
                descripcion_corta="Conversor de unidades técnicas para ingeniería.",
                descripcion="Una herramienta completa para convertir unidades de Caudal, Presión, Potencia, Longitud, y muchas otras magnitudes físicas.",
                requiere_membresia=True,
                template_file='webapps/conversor_unidades.html',
                ruta_archivo='',
                url_help='',
                tipo_aplicativo_id=tipo.id
            )
            db.session.add(nuevo_app)
            db.session.commit()
            print(f"¡Aplicativo '{nombre_app}' creado exitosamente!")

def registrar_calculadora_perdida_accesorios():
    with app.app_context():
        nombre_app = "Cálculo de Pérdidas por Accesorios"
        app_existente = Aplicativo.query.filter(Aplicativo.nombre == nombre_app).first()

        nombre_tipo = "Cálculos Hidráulicos"
        tipo = TipoAplicativo.query.filter_by(nombre=nombre_tipo).first()
        if not tipo:
            print(f"Creando nuevo tipo: '{nombre_tipo}'")
            tipo = TipoAplicativo(nombre=nombre_tipo, descripcion="Herramientas para cálculos hidráulicos en sistemas de bombeo.")
            db.session.add(tipo)
            db.session.flush()

        if app_existente:
            print(f"El aplicativo '{nombre_app}' ya existe. No se hacen cambios.")
        else:
            print(f"Creando nuevo aplicativo: '{nombre_app}'...")
            nuevo_app = Aplicativo(
                nombre=nombre_app,
                descripcion_corta="Calcula las pérdidas de carga totales en un sistema, incluyendo tuberías y accesorios.",
                descripcion="Herramienta avanzada para determinar la pérdida de carga total en un sistema de tuberías, sumando la fricción principal y las pérdidas menores generadas por válvulas, codos y otros accesorios.",
                requiere_membresia=True,
                template_file='webapps/calculadora_perdida_accesorios.html',
                ruta_archivo='',
                url_help='',
                tipo_aplicativo_id=tipo.id
            )
            db.session.add(nuevo_app)
            db.session.commit()
            print(f"¡Aplicativo '{nombre_app}' creado exitosamente!")

if __name__ == '__main__':
    # registrar_conversor_unidades()
    registrar_calculadora_perdida_accesorios()
