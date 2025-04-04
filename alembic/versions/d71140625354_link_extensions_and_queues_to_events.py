"""link extensions and queues to events

Revision ID: d71140625354
Revises: ab98db2ffe5b
Create Date: 2024-12-31 14:37:17.193187

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'd71140625354'
down_revision = 'ab98db2ffe5b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Cette migration est intentionnellement vide.
    
    Elle sert de point de liaison dans l'historique des migrations entre
    'ab98db2ffe5b' et les migrations qui en dépendent. Les changements de schéma
    initialement prévus ont été implémentés dans d'autres migrations.
    
    Ne pas supprimer cette migration car d'autres migrations en dépendent.
    """
    pass


def downgrade() -> None:
    """
    Cette migration est intentionnellement vide.
    
    Aucune action n'est nécessaire pour annuler cette migration car
    elle ne contient aucun changement de schéma.
    """
    pass