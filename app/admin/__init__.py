from flask import Blueprint

bp = Blueprint('admin', __name__, template_folder='templates')
bp.login_view = 'admin.login'  # Vista de login específica para este blueprint
bp.login_message = 'Por favor, inicie sesión como administrador para acceder.'
bp.login_message_category = 'warning'


from app.admin import routes, commands  # noqa: F401