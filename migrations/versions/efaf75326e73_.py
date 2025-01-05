"""Change table column names to fix errors

Revision ID: efaf75326e73
Revises: b43ed054e5d2
Create Date: 2025-01-03 15:07:03.832615

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "efaf75326e73"
down_revision = "b43ed054e5d2"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("event", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("repeat_often", sa.Integer(), nullable=False))
        batch_op.drop_column("repeat_every")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("event", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("repeat_every", sa.INTEGER(), nullable=False))
        batch_op.drop_column("repeat_often")

    # ### end Alembic commands ###
