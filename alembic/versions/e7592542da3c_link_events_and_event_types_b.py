"""link events and event types b

Revision ID: e7592542da3c
Revises: 66032d415314
Create Date: 2025-01-19 17:58:28.983364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7592542da3c'
down_revision = '66032d415314'
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
    op.create_table('events_types_events',
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('event_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['extraevents.id'], name=op.f('fk_events_types_events_event_id_extraevents')),
    sa.ForeignKeyConstraint(['event_type_id'], ['events_types.id'], name=op.f('fk_events_types_events_event_type_id_events_types')),
    sa.PrimaryKeyConstraint('event_id', 'event_type_id', name=op.f('pk_events_types_events'))
    )

    with op.batch_alter_table('events_types', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_events_types_id'), ['id'])

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('events_types_events')
    # ### end Alembic commands ###
