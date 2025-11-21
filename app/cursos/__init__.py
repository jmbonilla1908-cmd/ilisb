from flask import Blueprint

bp = Blueprint('cursos', __name__, template_folder='templates')

from app.cursos import routes, models