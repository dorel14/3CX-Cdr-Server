"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

# Surcharge de la méthode create_table pour ajouter if_not_exists=True
#_original_create_table = op.create_table
#def create_table_with_if_not_exists(*args, **kwargs):
#    kwargs['if_not_exists'] = True
#    return _original_create_table(*args, **kwargs)
#op.create_table = create_table_with_if_not_exists

def upgrade() -> None:
    try:
        ${upgrades if upgrades else "pass"}
    except sa.exc.OperationalError as e:
        # Log the error but allow migration to continue
        logger.warning(f"Operation error during upgrade: {str(e)}")
    except Exception as e:
        # For other exceptions, log and re-raise to stop the migration
        logger.error(f"Unexpected error during upgrade: {str(e)}")
        raise


def downgrade() -> None:
    try:
        ${downgrades if downgrades else "pass"}
    except sa.exc.OperationalError as e:
        # Log the error but allow migration to continue
        logger.warning(f"Operation error during downgrade: {str(e)}")
    except Exception as e:
        # For other exceptions, log and re-raise to stop the migration
        logger.error(f"Unexpected error during downgrade: {str(e)}")
        raise

