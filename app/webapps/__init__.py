from flask import Blueprint

bp = Blueprint(
    'webapps', __name__,
    template_folder='templates',
    static_folder='static'
)

from app.webapps import routes  # noqa: E402
from . import models  # noqa: E402, F401
