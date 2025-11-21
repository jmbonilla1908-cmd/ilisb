from flask import Blueprint

bp = Blueprint(
    'marketing', __name__,
    template_folder='templates',
    static_folder='static'
)

from . import routes, models  # noqa: E402, F401
