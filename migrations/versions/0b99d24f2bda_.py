"""empty message

Revision ID: 0b99d24f2bda
Revises: 
Create Date: 2021-01-23 18:33:46.538870

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b99d24f2bda'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Currency',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ccy', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ccy')
    )
    op.create_table('Date',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('date')
    )
    op.create_table('Tenor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tenor', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tenor')
    )
    op.create_table('Curve',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_id', sa.Integer(), nullable=False),
    sa.Column('ccy_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['ccy_id'], ['Currency.id'], ),
    sa.ForeignKeyConstraint(['date_id'], ['Date.id'], ),
    sa.PrimaryKeyConstraint('id', name='_pk_id'),
    sa.UniqueConstraint('date_id', 'ccy_id', name='_curve_uc')
    )
    op.create_table('Spread',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tenor_id', sa.Integer(), nullable=False),
    sa.Column('curve_id', sa.Integer(), nullable=False),
    sa.Column('spread', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['curve_id'], ['Curve.id'], ),
    sa.ForeignKeyConstraint(['tenor_id'], ['Tenor.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Spread')
    op.drop_table('Curve')
    op.drop_table('Tenor')
    op.drop_table('Date')
    op.drop_table('Currency')
    # ### end Alembic commands ###
