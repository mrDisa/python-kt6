"""Create users, projects, todos

Revision ID: 20261114_001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "20261114_001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(16), nullable=False))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False))
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])
    op.create_table("todos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("creator_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False))
    op.create_index("ix_todos_project_id", "todos", ["project_id"])

def downgrade():
    op.drop_index("ix_todos_project_id", "todos")
    op.drop_table("todos")
    op.drop_index("ix_projects_owner_id", "projects")
    op.drop_table("projects")
    op.drop_index("ix_users_email", "users")
    op.drop_table("users")
