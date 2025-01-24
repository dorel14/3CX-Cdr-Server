"""link events and event types

Revision ID: 66032d415314
Revises: 25c2c8d021a3
Create Date: 2025-01-19 17:41:52.894540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66032d415314'
down_revision = '25c2c8d021a3'
branch_labels = None
depends_on = None

# Surcharge de la méthode create_table pour ajouter if_not_exists=True
_original_create_table = op.create_table
def create_table_with_if_not_exists(*args, **kwargs):
    kwargs['if_not_exists'] = True
    return _original_create_table(*args, **kwargs)
op.create_table = create_table_with_if_not_exists

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_events_types')),
    sa.UniqueConstraint('id', name=op.f('uq_events_types_id'))
    )
    with op.batch_alter_table('extensiontoqueuelink', schema=None) as batch_op:
        batch_op.alter_column('extension_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('queue_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('extensiontoqueuelink', schema=None) as batch_op:
        batch_op.alter_column('queue_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('extension_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    op.drop_table('events_types')
    # ### end Alembic commands ###
