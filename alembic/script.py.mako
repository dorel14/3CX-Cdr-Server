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

# Set up logger for migration-specific logging
logger = logging.getLogger('alembic.migration')

# Alembic revision identifiers - used to track migration history and dependencies
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

# NOTE: Commented code below shows how to override create_table to always use if_not_exists
# This can be uncommented if you want tables to be created only if they don't already exist
#_original_create_table = op.create_table
#def create_table_with_if_not_exists(*args, **kwargs):
#    kwargs['if_not_exists'] = True
#    return _original_create_table(*args, **kwargs)
#op.create_table = create_table_with_if_not_exists

def upgrade() -> None:
    """
    Performs the upgrade migration steps.

    This function includes comprehensive error handling to manage different types of database errors:
    - Connection errors: Immediately fail the migration
    - Operational errors: Log, rollback if possible, and continue (useful for non-critical errors)
    - Integrity/Programming errors: Log, rollback if possible, and fail the migration
    - Other exceptions: Log, rollback if possible, and fail the migration
    """
    conn = op.get_bind()
    try:
        # Execute the actual migration upgrade steps
        ${upgrades if upgrades else "pass"}
    except DBAPIError as e:
        # Handle database connection issues separately from other API errors
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            logger.error(f"Database connection error during upgrade: {str(e)}")
            logger.error("Please check your database connection settings and ensure the database is running.")
            raise  # Connection errors are critical - always fail the migration
        else:
            logger.error(f"Database API error during upgrade: {str(e)}")
            raise
    except OperationalError as e:
        # OperationalError typically represents database operation failures that might be transient
        # or non-critical (like timeouts, lock waits, etc.)
        logger.warning(f"Operation error during upgrade: {str(e)}")

        # Attempt to rollback the transaction to maintain database consistency
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after OperationalError")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after OperationalError: {str(rollback_error)}")

        # We continue despite OperationalError because these are often non-critical
        # and might be related to specific statements rather than the whole migration
        logger.warning("Continuing with migration despite OperationalError - this may leave the database in a partially migrated state")
    except IntegrityError as e:
        # IntegrityError indicates constraint violations (unique, foreign key, etc.)
        # These are critical errors that should fail the migration
        logger.error(f"Integrity error during upgrade: {str(e)}")
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after IntegrityError")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after IntegrityError: {str(rollback_error)}")
        raise  # Always fail the migration on integrity errors
    except ProgrammingError as e:
        # ProgrammingError typically indicates SQL syntax errors or invalid database objects
        logger.error(f"SQL Programming error during upgrade: {str(e)}")
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after ProgrammingError")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after ProgrammingError: {str(rollback_error)}")
        raise  # Always fail the migration on programming errors
    except Exception as e:
        # Catch-all for any other unexpected exceptions
        logger.error(f"Unexpected error during upgrade: {str(e)}")
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after unexpected error")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after unexpected error: {str(rollback_error)}")
        raise  # Always fail the migration on unexpected errors


def downgrade() -> None:
    """
    Performs the downgrade migration steps.

    This function mirrors the upgrade function's error handling approach:
    - Connection errors: Immediately fail the migration
    - Operational errors: Log, rollback if possible, and continue (useful for non-critical errors)
    - Integrity/Programming errors: Log, rollback if possible, and fail the migration
    - Other exceptions: Log, rollback if possible, and fail the migration
    """
    conn = op.get_bind()
    try:
        # Execute the actual migration downgrade steps
        ${downgrades if downgrades else "pass"}
    except DBAPIError as e:
        # Handle database connection issues separately from other API errors
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            logger.error(f"Database connection error during downgrade: {str(e)}")
            logger.error("Please check your database connection settings and ensure the database is running.")
            raise  # Connection errors are critical - always fail the migration
        else:
            logger.error(f"Database API error during downgrade: {str(e)}")
            raise
    except OperationalError as e:
        # OperationalError typically represents database operation failures that might be transient
        logger.warning(f"Operation error during downgrade: {str(e)}")

        # Attempt to rollback the transaction to maintain database consistency
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after OperationalError")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after OperationalError: {str(rollback_error)}")

        # We continue despite OperationalError because these are often non-critical
        logger.warning("Continuing with migration despite OperationalError - this may leave the database in a partially migrated state")
    except IntegrityError as e:
        # IntegrityError indicates constraint violations (unique, foreign key, etc.)
        logger.error(f"Integrity error during downgrade: {str(e)}")
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after IntegrityError")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after IntegrityError: {str(rollback_error)}")
        raise  # Always fail the migration on integrity errors
    except ProgrammingError as e:
        # ProgrammingError typically indicates SQL syntax errors or invalid database objects
        logger.error(f"SQL Programming error during downgrade: {str(e)}")
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after ProgrammingError")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after ProgrammingError: {str(rollback_error)}")
        raise  # Always fail the migration on programming errors
    except Exception as e:
        # Catch-all for any other unexpected exceptions
        logger.error(f"Unexpected error during downgrade: {str(e)}")
        try:
            conn.rollback()
            logger.info("Successfully rolled back transaction after unexpected error")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback after unexpected error: {str(rollback_error)}")
        raise  # Always fail the migration on unexpected errors