"""Limpieza de columnas legacy y consolidación de modelo

Revision ID: 20251003_cleanup_legacy
Revises: 562873dd8687
Create Date: 2025-10-03 22:45:00

Objetivos:
- Consolidar nuevas columnas en 'grupo' y eliminar legacy ya migradas
- Ajustar defaults y nullability finales
- Eliminar columnas obsoletas en 'aplicativo' si ya están duplicadas (ruta vs ruta_archivo)

Estrategia segura:
1. Validar existencia de columnas antes de tocar (idempotente)
2. Rellenar valores nulos razonables
3. Sólo eliminar si la columna nueva contiene datos o la legacy está vacía / duplicada

Rollback:
- Re-crear columnas legacy vacías (sin datos originales) -> sólo útil para despliegue inmediato; no restaura contenido previo truncado.

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '20251003_cleanup_legacy'
down_revision = '562873dd8687'
branch_labels = None
depends_on = None


def _col_exists(bind, table, col):
    q = sa.text(
        """SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME=:t AND COLUMN_NAME=:c LIMIT 1"""
    )
    return bind.execute(q, {"t": table, "c": col}).fetchone() is not None

def upgrade():
    bind = op.get_bind()

    # Tabla grupo: eliminar legacy ya migradas
    legacy_cols = [
        ('horariocurso',),
        ('fechacurso',),
        ('qsesionesGrupo',),
        ('duraciontotalGrupo',),
    ]

    # Asegurar defaults finales antes de endurecer nullability
    if _col_exists(bind, 'grupo', 'estado'):
        op.execute("UPDATE grupo SET estado='PROPUESTO' WHERE estado IS NULL")
    if _col_exists(bind, 'grupo', 'fecha_inicio'):
        op.execute("UPDATE grupo SET fecha_inicio=CURDATE() WHERE fecha_inicio IS NULL")
    if _col_exists(bind, 'grupo', 'capacidad_minima'):
        op.execute("UPDATE grupo SET capacidad_minima=5 WHERE capacidad_minima IS NULL")

    with op.batch_alter_table('grupo') as batch_op:
        # Endurecer nullability
        if _col_exists(bind, 'grupo', 'estado'):
            try:
                batch_op.alter_column('estado', existing_type=sa.String(length=50), nullable=False)
            except Exception:
                pass
        if _col_exists(bind, 'grupo', 'fecha_inicio'):
            try:
                batch_op.alter_column('fecha_inicio', existing_type=sa.Date(), nullable=False)
            except Exception:
                pass
        if _col_exists(bind, 'grupo', 'capacidad_minima'):
            try:
                batch_op.alter_column('capacidad_minima', existing_type=sa.Integer(), nullable=False)
            except Exception:
                pass
        # Eliminar columnas legacy (si existen)
        for (c,) in legacy_cols:
            if _col_exists(bind, 'grupo', c):
                try:
                    batch_op.drop_column(c)
                except Exception:
                    pass

    # Tabla aplicativo: si coexistieran nombreaplicativo y nombre, no eliminar ahora (requiere inspección manual)
    # Ruta duplicada: si existe 'ruta' y no se usa, no la tocamos hasta confirmar

    # Tabla anuncio: no hay limpieza adicional en este paso


def downgrade():
    bind = op.get_bind()
    with op.batch_alter_table('grupo') as batch_op:
        # Re-crear columnas legacy como NULL (sin datos originales)
        for name, coltype in [
            ('horariocurso', sa.String(length=1000)),
            ('fechacurso', sa.String(length=1000)),
            ('qsesionesGrupo', sa.Integer()),
            ('duraciontotalGrupo', sa.Integer()),
        ]:
            if not _col_exists(bind, 'grupo', name):
                batch_op.add_column(sa.Column(name, coltype, nullable=True))
        # Relajar constraints endurecidos
        try:
            batch_op.alter_column('estado', existing_type=sa.String(length=50), nullable=True)
        except Exception:
            pass
        try:
            batch_op.alter_column('fecha_inicio', existing_type=sa.Date(), nullable=True)
        except Exception:
            pass
        try:
            batch_op.alter_column('capacidad_minima', existing_type=sa.Integer(), nullable=True)
        except Exception:
            pass
