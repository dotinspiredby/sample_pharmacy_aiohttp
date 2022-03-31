"""m

Revision ID: 4232c657b1bc
Revises: 
Create Date: 2022-03-20 23:14:59.318716

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4232c657b1bc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('login', sa.Unicode(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admins')
    # ### end Alembic commands ###