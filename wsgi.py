import os
from app import create_app, db

# Lee la variable de entorno FLASK_CONFIG. Si no existe, usa 'development' por defecto.
config_name = os.getenv('FLASK_CONFIG', 'development')

# Mapea el nombre del entorno al string de configuración.
config_map = {
    'development': 'config.DevelopmentConfig',
    'production': 'config.ProductionConfig'
}
config_string = config_map.get(config_name, 'config.DevelopmentConfig')

app = create_app(config_string)