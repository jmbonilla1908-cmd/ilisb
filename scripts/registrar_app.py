import os
import sys
from slugify import slugify

# Añadir el directorio raíz del proyecto al path para poder importar la app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timezone

from app import create_app, db
from app.webapps.models import Aplicativo, TipoAplicativo

# Usamos la configuración de desarrollo para el script
app = create_app('config.DevelopmentConfig')

def registrar_calculadora():
    with app.app_context():
        nombre_antiguo = "Análisis de Curva de Bomba y Sistema"
        nombre_nuevo = "Cálculo de la curva de sistema"
        
        # Buscamos el aplicativo por su nombre ANTIGUO
        app_existente = Aplicativo.query.filter(Aplicativo.nombre == nombre_antiguo).first()
        
        nombre_tipo = "Cálculos Hidráulicos"
        tipo = TipoAplicativo.query.filter_by(nombre=nombre_tipo).first()
        if not tipo:
            tipo = TipoAplicativo(nombre=nombre_tipo, descripcion="Herramientas para cálculos hidráulicos en sistemas de bombeo.")
            db.session.add(tipo)
            db.session.flush()
            print(f"Nuevo tipo de aplicativo creado: '{nombre_tipo}'")

        # Si encontramos el aplicativo antiguo, lo actualizamos.
        if app_existente:
            print(f"Actualizando el aplicativo '{nombre_antiguo}' a '{nombre_nuevo}'...")
            app_existente.nombre = nombre_nuevo
            app_existente.descripcion_corta = "Grafica la curva de una bomba y la curva del sistema para encontrar el punto de operación."
            app_existente.descripcion = "Herramienta avanzada que permite definir la curva de una bomba (ingresando puntos Q-H), la curva del sistema (por punto de operación o por pérdidas) y visualizar la interacción entre ambas, incluyendo el ajuste por variación de frecuencia (RPM)."
            app_existente.fecha_actualizacion = datetime.now(timezone.utc)
            app_existente.template_file = 'webapps/calculadora_curva_sistema.html' # Nuevo nombre de plantilla
        else:
            # Si no existe, verificamos si ya existe con el nombre nuevo (por si el script se corre dos veces)
            app_ya_actualizado = Aplicativo.query.filter(Aplicativo.nombre == nombre_nuevo).first()
            if app_ya_actualizado:
                print(f"El aplicativo '{nombre_nuevo}' ya existe y está actualizado. No se hacen cambios.")
            else:
                # Este bloque 'else' ya no debería ser necesario si partimos del aplicativo antiguo,
                # pero lo dejamos como salvaguarda.
                print(f"No se encontró el aplicativo antiguo. Verifique el nombre.")
        
        db.session.commit()
        print(f"¡Operación de actualización completada!")

def registrar_calculadora_perdidas():
    with app.app_context():
        nombre_app = "Caída de Presión en la Tubería (Hazen Williams)"
        
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
        nombre_app = "Pérdidas de Carga en Tuberías y Accesorios"
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

def limpiar_duplicados():
    """
    Busca y elimina aplicativos duplicados que se hayan podido crear
    durante la refactorización.
    """
    with app.app_context():
        nombre_app = "Análisis de Curva de Bomba y Sistema"
        # Busca todos los aplicativos con ese nombre, ordenados por fecha de creación
        apps = Aplicativo.query.filter_by(nombre=nombre_app).order_by(Aplicativo.fecha_registro.asc()).all()

        if len(apps) > 1:
            print(f"Se encontraron {len(apps)} aplicativos duplicados para '{nombre_app}'. Limpiando...")
            # Mantenemos el primero (el más antiguo, que es el original) y eliminamos los demás.
            for app_a_borrar in apps[1:]:
                print(f"Eliminando aplicativo duplicado con ID: {app_a_borrar.id}")
                db.session.delete(app_a_borrar)
            db.session.commit()
            print("Limpieza completada.")

def registrar_seleccion_cable():
    with app.app_context():
        nombre_app = "Dimensionamiento del cable"
        app_existente = Aplicativo.query.filter(Aplicativo.nombre == nombre_app).first()

        nombre_tipo = "Cálculos Eléctricos"
        tipo = TipoAplicativo.query.filter_by(nombre=nombre_tipo).first()
        if not tipo:
            print(f"Creando nuevo tipo: '{nombre_tipo}'")
            tipo = TipoAplicativo(nombre=nombre_tipo, descripcion="Herramientas para cálculos eléctricos en sistemas de bombeo.")
            db.session.add(tipo)
            db.session.flush()

        if app_existente:
            print(f"El aplicativo '{nombre_app}' ya existe. No se hacen cambios.")
        else:
            print(f"Creando nuevo aplicativo: '{nombre_app}'...")
            nuevo_app = Aplicativo(
                nombre=nombre_app,
                descripcion_corta="Calcula la caída de voltaje para seleccionar el calibre de cable sumergible adecuado.",
                descripcion="Herramienta para el dimensionamiento correcto de cables para bombas sumergibles, calculando la caída de voltaje en porcentaje para diferentes calibres (AWG) según las condiciones del motor y la instalación.",
                requiere_membresia=True,
                template_file='webapps/seleccion_cable_sumergible.html',
                ruta_archivo='',
                url_help='',
                tipo_aplicativo_id=tipo.id
            )
            db.session.add(nuevo_app)
            db.session.commit()
            print(f"¡Aplicativo '{nombre_app}' creado exitosamente!")

def registrar_calculadora_sumergencia():
    with app.app_context():
        nombre_app = "Sumergencia mínima de tubería succión"
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
                descripcion_corta="Calcula la sumergencia mínima para evitar vórtices en la succión de bombas.",
                descripcion="Basado en los estándares del Hydraulic Institute, esta herramienta determina la sumergencia mínima (S) y otras dimensiones recomendadas para el diseño de pozos de succión, previniendo la formación de vórtices y la entrada de aire.",
                requiere_membresia=True,
                template_file='webapps/calculadora_sumergencia.html',
                ruta_archivo='',
                url_help='',
                tipo_aplicativo_id=tipo.id
            )
            db.session.add(nuevo_app)
            db.session.commit()
            print(f"¡Aplicativo '{nombre_app}' creado exitosamente!")

# Usamos una lista de tuplas para mantener el orden del Excel
ESTRUCTURA_APLICATIVOS = [
    ("General", [
        "Conversor de Unidades",
    ]),
    ("Tuberías", [
        "Caída de Presión en la Tubería (Hazen Williams)",
        "Pérdidas de Carga en Tuberías y Accesorios",
    ]),
    ("Bomba centrífuga", [
        "Sumergencia mínima de tubería succión",
    ]),
    ("Diseño e Ingeniería - Hidráulica general", [
        "Cálculo de la curva de sistema",
    ]),
    ("Operación", []),
    ("Dimensionamiento Eléctrico", [
        "Dimensionamiento del cable",
    ]),
    ("Electricidad Industrial", []),
    ("Tanque Hidroneumático", []),
    ("Simuladores para control de bombas", []),
    ("Para Mantenimiento de Bombas", []),
    ("Bomba Turbina Sumergible para pozo profundo", []),
    ("Costos de energía y eficiencia energética", []),
    ("Costos y presupuestos y tiempos de entrega", []),
    ("Matemáticas y estadística", []),
]

def sincronizar_estructura():
    """
    Crea las categorías (Tipos) y reasigna los aplicativos existentes
    según la estructura definida en ESTRUCTURA_APLICATIVOS.
    """
    with app.app_context():
        print("Iniciando sincronización de estructura de aplicativos...")
        
        # 1. Crear/Obtener todas las categorías necesarias
        tipos_db = {}
        for i, (nombre_tipo, _) in enumerate(ESTRUCTURA_APLICATIVOS):
            orden = i + 1
            tipo = TipoAplicativo.query.filter_by(nombre=nombre_tipo).first()
            if not tipo:
                print(f"Creando nueva categoría: '{nombre_tipo}'")
                tipo = TipoAplicativo(nombre=nombre_tipo, descripcion=f"Herramientas de {nombre_tipo.lower()}.", orden=orden)
                db.session.add(tipo)
                db.session.flush() # Para obtener el ID antes del commit
            elif tipo.orden != orden:
                print(f"Actualizando orden para '{nombre_tipo}' a {orden}")
                tipo.orden = orden
            tipos_db[nombre_tipo] = tipo

        # 2. Reasignar aplicativos existentes a su nueva categoría
        for nombre_tipo, lista_apps in ESTRUCTURA_APLICATIVOS:
            tipo_obj = tipos_db[nombre_tipo]
            for nombre_app in lista_apps:
                app_obj = Aplicativo.query.filter_by(nombre=nombre_app).first()
                if app_obj and app_obj.tipo_aplicativo_id != tipo_obj.id:
                    print(f"Reasignando '{nombre_app}' a la categoría '{nombre_tipo}'...")
                    app_obj.tipo_aplicativo_id = tipo_obj.id
        
        db.session.commit()
        print("Sincronización de estructura completada.")

def limpiar_categorias_vacias():
    """
    Busca y elimina las categorías (TipoAplicativo) que no tienen
    ningún aplicativo asociado.
    """
    with app.app_context():
        print("Buscando categorías vacías para limpiar...")
        
        # Query para encontrar tipos que no tienen aplicativos
        categorias_vacias = TipoAplicativo.query.outerjoin(Aplicativo).group_by(TipoAplicativo.id).having(db.func.count(Aplicativo.id) == 0).all()

        if categorias_vacias:
            for categoria in categorias_vacias:
                print(f"Eliminando categoría vacía: '{categoria.nombre}'")
                db.session.delete(categoria)
            db.session.commit()
            print("Limpieza de categorías vacías completada.")
        else:
            print("No se encontraron categorías vacías.")


if __name__ == '__main__':
    sincronizar_estructura()
    limpiar_categorias_vacias()
