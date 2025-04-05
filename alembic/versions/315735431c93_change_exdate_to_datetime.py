"""Change exdate to datetime

Revision ID: 315735431c93
Revises: 7d3ece5c0869
Create Date: 2025-03-01 16:49:56.741639

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect, text
import logging

# Set up logging
logger = logging.getLogger('alembic.migration')

# revision identifiers, used by Alembic.
revision = '315735431c93'
down_revision = '7d3ece5c0869'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Upgrades the 'exdate' column in 'extraevents' table from ARRAY(DATE) to ARRAY(DateTime).
    
    This migration handles the following scenarios:
    1. Table or column doesn't exist - skips the migration
    2. Column is already ARRAY(DateTime) or similar timestamp type - skips the conversion
    3. Column is ARRAY(DATE) - performs the conversion
    4. Column is another array type - raises an error with guidance
    5. Column is a non-array type - raises an error with guidance
    
    PostgreSQL type representations in information_schema:
    - ARRAY(DATE): data_type='ARRAY', udt_name='_date'
    - ARRAY(TIMESTAMP): data_type='ARRAY', udt_name='_timestamp'
    - ARRAY(TIMESTAMPTZ): data_type='ARRAY', udt_name='_timestamptz'
    """
    conn = op.get_bind()
    
    # Vérifier si la table et la colonne existent
    inspector = inspect(conn)
    if 'extraevents' not in inspector.get_table_names():
        logger.info("Table 'extraevents' does not exist, skipping column type change")
        return
        
    columns = [col['name'] for col in inspector.get_columns('extraevents')]
    if 'exdate' not in columns:
        logger.info("Column 'exdate' does not exist in table 'extraevents', skipping column type change")
        return
        
    # Vérifier le type actuel de la colonne exdate avec une requête plus précise pour PostgreSQL
    logger.info("Checking data type of column 'exdate' in table 'extraevents'")
    result = conn.execute(text("""
        SELECT data_type, udt_name, character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = 'extraevents' AND column_name = 'exdate'
    """)).fetchone()
    
    if not result:
        logger.warning("Could not determine the type of column 'exdate', skipping conversion.")
        return
    
    data_type, udt_name, char_max_length = result
    
    # Define types that don't need conversion (already datetime-based)
    datetime_array_types = ['_timestamp', '_timestamptz', '_datetime']
    
    # Define types that need conversion from date to datetime
    date_array_types = ['_date']
    
    # Check if column is an array type
    if data_type == 'ARRAY':
        # Already a datetime-based array - no conversion needed
        if udt_name in datetime_array_types:
            logger.info(f"Column 'exdate' is already of type ARRAY({udt_name[1:].upper()}), no conversion needed")
            return
            
        # Date-based array - needs conversion
        elif udt_name in date_array_types:
            logger.info(f"Column 'exdate' is of type ARRAY({udt_name[1:].upper()}), converting to ARRAY(DateTime)")
            with op.batch_alter_table('extraevents', schema=None) as batch_op:
                batch_op.alter_column('exdate',
                        existing_type=postgresql.ARRAY(sa.DATE()),
                        type_=postgresql.ARRAY(sa.DateTime()),
                        existing_nullable=True)
            logger.info("Successfully converted column 'exdate' to ARRAY(DateTime)")
            
        # Other array type - needs manual intervention
        else:
            error_msg = (f"Unexpected array type for column 'exdate': ARRAY({udt_name[1:]}). "
                        f"Expected ARRAY(DATE). Migration halted to prevent data corruption. "
                        f"MANUAL ACTION REQUIRED: Please examine the 'exdate' column and convert "
                        f"it to ARRAY(TIMESTAMP) manually, then mark this migration as completed.")
            logger.error(error_msg)
            raise TypeError(error_msg)
    
    # Not an array type - needs manual intervention
    else:
        error_msg = (f"Column 'exdate' is not an array type. Found: {data_type}. "
                    f"Expected ARRAY(DATE). Migration halted to prevent data corruption. "
                    f"MANUAL ACTION REQUIRED: Please examine the 'exdate' column and convert "
                    f"it to ARRAY(TIMESTAMP) manually, then mark this migration as completed.")
        logger.error(error_msg)
        raise TypeError(error_msg)


def downgrade() -> None:
    """
    Downgrades the 'exdate' column in 'extraevents' table from ARRAY(DateTime) back to ARRAY(DATE).
    
    This operation assumes the column exists and is of type ARRAY(DateTime).
    If an error occurs during the conversion, it will be logged and re-raised to halt the downgrade.
    """
    logger.info("Converting column 'exdate' back to ARRAY(DATE)")
    try:
        with op.batch_alter_table('extraevents', schema=None) as batch_op:
            batch_op.alter_column('exdate',
                    existing_type=postgresql.ARRAY(sa.DateTime()),
                    type_=postgresql.ARRAY(sa.DATE()),
                    existing_nullable=True)
        logger.info("Successfully converted column 'exdate' back to ARRAY(DATE)")
    except Exception as e:
        logger.error(f"Error converting column 'exdate': {str(e)}")
        raise  # Re-raise the exception to halt the downgrade process