"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
import logging
from sqlalchemy.exc import OperationalError, ProgrammingError, IntegrityError, DBAPIError
${imports if imports else ""}

# Set up logger
logger = logging.getLogger('alembic.migration')

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
    conn = op.get_bind()
    try:
        ${upgrades if upgrades else "pass"}
    except DBAPIError as e:
        # Check if it's a connection error
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            logger.error(f"Database connection error during upgrade: {str(e)}")
            logger.error("Please check your database connection settings and ensure the database is running.")
            raise
        else:
            logger.error(f"Database API error during upgrade: {str(e)}")
            raise
    except OperationalError as e:
        # Log the error
        logger.warning(f"Operation error during upgrade: {str(e)}")

        # Attempt to rollback the transaction
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after OperationalError")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after OperationalError: {str(rollback_error)}")

        # Continue with migration despite the error
        logger.warning("Continuing with migration despite OperationalError")
    except IntegrityError as e:
        logger.error(f"Integrity error during upgrade: {str(e)}")
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after IntegrityError")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after IntegrityError: {str(rollback_error)}")
        raise
    except ProgrammingError as e:
        logger.error(f"SQL Programming error during upgrade: {str(e)}")
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after ProgrammingError")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after ProgrammingError: {str(rollback_error)}")
        raise
    except Exception as e:
        # For other exceptions, log and re-raise to stop the migration
        logger.error(f"Unexpected error during upgrade: {str(e)}")
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after unexpected error")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after unexpected error: {str(rollback_error)}")
        raise


def downgrade() -> None:
    conn = op.get_bind()
    try:
        ${downgrades if downgrades else "pass"}
    except DBAPIError as e:
        # Check if it's a connection error
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            logger.error(f"Database connection error during downgrade: {str(e)}")
            logger.error("Please check your database connection settings and ensure the database is running.")
            raise
        else:
            logger.error(f"Database API error during downgrade: {str(e)}")
            raise
    except OperationalError as e:
        # Log the error
        logger.warning(f"Operation error during downgrade: {str(e)}")
        
        # Attempt to rollback the transaction
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after OperationalError")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after OperationalError: {str(rollback_error)}")
        
        # Continue with migration despite the error
        logger.warning("Continuing with migration despite OperationalError")
    except IntegrityError as e:
        logger.error(f"Integrity error during downgrade: {str(e)}")
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after IntegrityError")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after IntegrityError: {str(rollback_error)}")
        raise
    except ProgrammingError as e:
        logger.error(f"SQL Programming error during downgrade: {str(e)}")
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after ProgrammingError")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after ProgrammingError: {str(rollback_error)}")
        raise
    except Exception as e:
        # For other exceptions, log and re-raise to stop the migration
        logger.error(f"Unexpected error during downgrade: {str(e)}")
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after unexpected error")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after unexpected error: {str(rollback_error)}")
        raise