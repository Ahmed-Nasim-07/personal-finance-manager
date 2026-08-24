"""Add category to income

Revision ID: 66d19c62bae8
Revises: 210c0e105d2c
Create Date: 2026-08-24 23:15:30.445655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66d19c62bae8'
down_revision = '210c0e105d2c'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("incomes", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("category_id", sa.Integer(), nullable=False)
        )

        batch_op.create_foreign_key(
            "fk_incomes_category_id",
            "categories",
            ["category_id"],
            ["id"]
        )


def downgrade():
    with op.batch_alter_table("incomes", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_incomes_category_id",
            type_="foreignkey"
        )

        batch_op.drop_column("category_id")

    # ### end Alembic commands ###
