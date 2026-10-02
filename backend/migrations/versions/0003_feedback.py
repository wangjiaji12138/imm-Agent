"""Minimal answer feedback."""

from alembic import op
import sqlalchemy as sa

revision = "0003_feedback"
down_revision = "0002_conversations"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("feedback",
                    sa.Column("id", sa.String(36), primary_key=True),
                    sa.Column("conversation_id", sa.String(36), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
                    sa.Column("request_id", sa.String(36), nullable=False),
                    sa.Column("rating", sa.String(12), nullable=False),
                    sa.Column("note", sa.Text(), nullable=True),
                    sa.Column("updated_at", sa.DateTime(), nullable=False),
                    sa.UniqueConstraint("conversation_id", "request_id", name="uq_feedback_answer"),
                    sa.CheckConstraint("rating IN ('helpful','not_helpful')", name="ck_feedback_rating"))
    op.create_index("ix_feedback_conversation_id", "feedback", ["conversation_id"])


def downgrade():
    op.drop_table("feedback")
