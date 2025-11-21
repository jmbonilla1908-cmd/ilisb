from flask import Blueprint

bp = Blueprint(
    'webapps', __name__,
    template_folder='templates',
    static_folder='static'
)

@bp.context_processor
def inject_tipos_aplicativos():
    """Inyecta la lista de tipos de aplicativos en todas las plantillas del blueprint."""
    from .models import TipoAplicativo
    # Modificación: Solo mostrar tipos que tengan al menos un aplicativo activo.
    tipos = (TipoAplicativo.query
             .join(TipoAplicativo.aplicativos)
             .filter_by(activo=True)
             .distinct()
             .order_by(TipoAplicativo.nombre)
             .all())
    return dict(tipos=tipos)

from app.webapps import routes  # noqa: E402
from . import models  # noqa: E402, F401
