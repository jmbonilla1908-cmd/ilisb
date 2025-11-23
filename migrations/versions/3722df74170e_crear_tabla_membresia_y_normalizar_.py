"""Crear tabla Membresia y normalizar AlumnoMembresia

Revision ID: 3722df74170e
Revises: 61208478cd1d
Create Date: 2025-11-22 23:23:59.898199

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3722df74170e'
down_revision = '61208478cd1d'
branch_labels = None
depends_on = None


def upgrade():
    # ### Fase 1: Crear la nueva tabla de membresías ###
    membresia_table = op.create_table('membresia',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('precio_base', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('moneda', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('duracion_cantidad', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('duracion_unidad', sa.String(length=20), nullable=False, server_default='months'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre')
    )

    # ### Fase 2: Poblar la tabla de membresías con los datos que descubriste ###
    op.bulk_insert(membresia_table,
        [
            {'id': 1, 'nombre': 'Anual', 'precio_base': 200.00, 'moneda': 'USD', 'duracion_cantidad': 1, 'duracion_unidad': 'years'},
            {'id': 2, 'nombre': 'Mensual', 'precio_base': 50.00, 'moneda': 'USD', 'duracion_cantidad': 1, 'duracion_unidad': 'months'},
            {'id': 3, 'nombre': 'Manual Admin', 'precio_base': 0.00, 'moneda': 'USD', 'duracion_cantidad': 200, 'duracion_unidad': 'years'},
        ]
    )

    # ### Fase 3: Modificar la tabla alumno_membresia ###
    with op.batch_alter_table('alumno_membresia', schema=None) as batch_op:
        # Renombrar la columna vieja para no perder los datos
        batch_op.alter_column('tipo_membresia', new_column_name='tipo_membresia_legacy', existing_type=mysql.VARCHAR(length=50))
        # Añadir la nueva columna membresia_id
        batch_op.add_column(sa.Column('membresia_id', sa.Integer(), nullable=True)) # Temporalmente nullable
        # Crear la clave foránea
        batch_op.create_foreign_key('fk_alumno_membresia_membresia', 'membresia', ['membresia_id'], ['id'])

    # ### Fase 4: Migración de datos ###
    alumno_membresia = table('alumno_membresia',
        column('id', sa.Integer),
        column('tipo_membresia_legacy', sa.String(50)),
        column('membresia_id', sa.Integer)
    )
    # Actualizar registros donde tipo_membresia es '1'
    op.execute(
        alumno_membresia.update().
        where(alumno_membresia.c.tipo_membresia_legacy == '1').
        values(membresia_id=1)
    )
    # Actualizar registros donde tipo_membresia es '2'
    op.execute(
        alumno_membresia.update().
        where(alumno_membresia.c.tipo_membresia_legacy == '2').
        values(membresia_id=2)
    )

    # ### Fase 5: Limpieza ###
    with op.batch_alter_table('alumno_membresia', schema=None) as batch_op:
        # Ahora que los datos están migrados, hacemos la columna no-nullable
        batch_op.alter_column('membresia_id', existing_type=sa.Integer(), nullable=False)
        # Finalmente, eliminamos la columna antigua
        batch_op.drop_column('tipo_membresia_legacy')


def downgrade():
    # El proceso inverso es más complejo, aquí solo revertimos la estructura
    with op.batch_alter_table('alumno_membresia', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tipo_membresia', sa.String(50), nullable=False, server_default='anual'))
        batch_op.drop_constraint('fk_alumno_membresia_membresia', type_='foreignkey')
        batch_op.drop_column('membresia_id')

    op.drop_table('membresia')
