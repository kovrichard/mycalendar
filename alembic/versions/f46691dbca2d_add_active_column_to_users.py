"""Add active column to users

Revision ID: f46691dbca2d
Revises: e9f9d9c1dbe6
Create Date: 2020-10-14 14:38:29.165496

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f46691dbca2d"
down_revision = "e9f9d9c1dbe6"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
    )
    op.alter_column(
        "users", "password", existing_type=sa.VARCHAR(length=255), nullable=False
    )
    op.alter_column(
        "users", "username", existing_type=sa.VARCHAR(length=255), nullable=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users", "username", existing_type=sa.VARCHAR(length=255), nullable=True
    )
    op.alter_column(
        "users", "password", existing_type=sa.VARCHAR(length=255), nullable=True
    )
    op.drop_column("users", "is_active")
    # ### end Alembic commands ###
