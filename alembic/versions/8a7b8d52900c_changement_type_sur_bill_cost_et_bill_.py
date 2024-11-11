"""Changement type sur bill_cost et bill-rate

Revision ID: 8a7b8d52900c
Revises: ef1bbaa2f981
Create Date: 2024-06-16 15:46:23.846436

"""
from alembic import op
import sqlalchemy as sa
from sqlmodel import SQLModel
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '8a7b8d52900c'
down_revision = 'ef1bbaa2f981'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('call_data_records') as batch_op:
        batch_op.add_column(sa.Column('bill_rate_temp', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('bill_cost_temp', sa.Float(), nullable=True))
        
    with op.batch_alter_table('call_data_records') as batch_op:
        batch_op.execute("""
            UPDATE call_data_records
            SET bill_rate_temp = CAST(bill_rate AS FLOAT),
                bill_cost_temp = CAST(bill_cost AS FLOAT)
            WHERE bill_rate IS NOT NULL AND bill_cost IS NOT NULL;
        """)

        batch_op.drop_column('bill_rate')
        batch_op.drop_column('bill_cost')

        batch_op.alter_column('bill_rate_temp', new_column_name='bill_rate')
        batch_op.alter_column('bill_cost_temp', new_column_name='bill_cost')

def downgrade() -> None:
    with op.batch_alter_table('call_data_records') as batch_op:
        batch_op.add_column(sa.Column('bill_rate_temp', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('bill_cost_temp', sa.VARCHAR(), nullable=True))

        batch_op.execute("""
            UPDATE call_data_records
            SET bill_rate_temp = bill_rate,
                bill_cost_temp = bill_cost;
        """)

        batch_op.drop_column('bill_rate')
        batch_op.drop_column('bill_cost')

        batch_op.alter_column('bill_rate_temp', new_column_name='bill_rate')
        batch_op.alter_column('bill_cost_temp', new_column_name='bill_cost')
    # ### end Alembic commands ###
