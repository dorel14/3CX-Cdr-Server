"""merge_multiple_heads

Revision ID: 38d244b2fbc2
Revises: bfe2413e87ef, c23c03b391d0
Create Date: 2024-11-15 18:56:39.775345

"""
from alembic import op
import sqlalchemy as sa
from sqlmodel import SQLModel
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '38d244b2fbc2'
down_revision = ('bfe2413e87ef', 'c23c03b391d0')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
