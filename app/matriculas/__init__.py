from flask import Blueprint

bp = Blueprint(
    'matriculas', __name__,
    template_folder='templates',
)

from . import routes, models  # noqa: E402, F401  # noqa: E402, F401
