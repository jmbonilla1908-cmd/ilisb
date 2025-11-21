from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_wtf.csrf import CSRFProtect
from flask_htmx import HTMX
import json
from werkzeug.utils import import_string

# Inicialización de extensiones
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # El login de alumnos es el predeterminado
login_manager.login_message = 'Por favor, inicie sesión para acceder a esta página.'
login_manager.login_message_category = 'info'
bootstrap = Bootstrap5()
csrf = CSRFProtect()
htmx = HTMX()

def create_app(config_name='config.DevelopmentConfig'):
    app = Flask(__name__)
    cfg = import_string(config_name)
    app.config.from_object(cfg)

    # Configurar Bootstrap-Flask para usar el tema 'Cosmo' de Bootswatch
    app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'cosmo'

    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)
    htmx.init_app(app)

    # Registrar Blueprints
    from app.core import bp as core_bp
    app.register_blueprint(core_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Restauramos el blueprint de webapps que ya tenías
    from app.webapps import bp as webapps_bp
    app.register_blueprint(webapps_bp, url_prefix='/webapps')

    # Registrar el nuevo blueprint de cursos
    from app.cursos import bp as cursos_bp
    app.register_blueprint(cursos_bp)

    # Registrar el nuevo blueprint de admin
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Registrar el nuevo blueprint de matriculas
    from app.matriculas import bp as matriculas_bp
    app.register_blueprint(matriculas_bp, url_prefix='/matriculas') # Corregido

    # Registrar el nuevo blueprint de marketing
    from app.marketing import bp as marketing_bp
    app.register_blueprint(marketing_bp, url_prefix='/marketing')

    # Registrar el nuevo blueprint de intranet
    from app.intranet import intranetModule as intranet_bp
    app.register_blueprint(intranet_bp, url_prefix='/intranet')

    # Registrar el nuevo blueprint de calendario
    from app.calendario import bp as calendario_bp
    app.register_blueprint(calendario_bp, url_prefix='/calendario')

    # Importar modelos para Flask-Migrate
    with app.app_context():
        from app.auth import models as auth_models  # noqa: F401
        from app.cursos import models as cursos_models  # noqa: F401
        from app.admin import models as admin_models  # noqa: F401
        from app.matriculas import models as matriculas_models  # noqa: F401
        from app.marketing import models as marketing_models  # noqa: F401
        from app.webapps import models as webapps_models  # noqa: F401
        from app.intranet import models as intranet_models  # noqa: F401
        from app.calendario import models as calendario_models  # noqa: F401
        from app.core import models as core_models  # noqa: F401

    # Context processor para aliados estratégicos
    @app.context_processor
    def inject_aliados():
        from app.marketing.models import AliadoEstrategico
        aliados = AliadoEstrategico.obtener_destacados(limite=12)
        return dict(aliados_estrategicos=aliados)

    # Custom Jinja filters
    app.jinja_env.filters['from_json'] = json.loads

    return app
