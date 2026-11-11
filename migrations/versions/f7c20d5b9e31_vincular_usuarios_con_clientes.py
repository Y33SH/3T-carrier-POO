"""Vincular usuarios Consultor con clientes

Revision ID: f7c20d5b9e31
Revises: 36e0d46670bf
Create Date: 2026-11-11

"""
from alembic import op
import sqlalchemy as sa


revision = "f7c20d5b9e31"
down_revision = "36e0d46670bf"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("usuarios", sa.Column("id_cliente", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_usuarios_id_cliente_clientes",
        "usuarios",
        "clientes",
        ["id_cliente"],
        ["id_cliente"],
    )


def downgrade():
    op.drop_constraint("fk_usuarios_id_cliente_clientes", "usuarios", type_="foreignkey")
    op.drop_column("usuarios", "id_cliente")
