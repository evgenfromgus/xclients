"""Creating base tables

Revision ID: 40d59a763b46
Revises: 
Create Date: 2024-10-12 11:58:43.121751

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "40d59a763b46"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # op.execute("DROP TYPE IF EXISTS roleenum;")
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "app_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "create_timestamp", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column(
            "change_timestamp", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("login", sa.String(length=20), nullable=False),
        sa.Column("password", sa.String(length=100), nullable=False),
        sa.Column("display_name", sa.String(length=40), nullable=False),
        sa.Column(
            "role", sa.Enum("admin", "client", name="roleenum", create_type=False), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "company",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "create_timestamp", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column(
            "change_timestamp", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "employee",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "create_timestamp", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column(
            "change_timestamp", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("first_name", sa.String(length=20), nullable=False),
        sa.Column("last_name", sa.String(length=20), nullable=False),
        sa.Column("middle_name", sa.String(length=20), nullable=True),
        sa.Column("phone", sa.String(length=15), nullable=False),
        sa.Column("email", sa.String(length=256), nullable=True),
        sa.Column("birthdate", sa.DATE(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("employee")
    op.drop_table("company")
    op.drop_table("app_users")
    # Удаление типа ENUM
    op.execute("DROP TYPE IF EXISTS roleenum;")
    # ### end Alembic commands ###
