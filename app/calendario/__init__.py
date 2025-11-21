from flask import Blueprint

bp = Blueprint('calendario', __name__, template_folder='templates')

from app.calendario import routes