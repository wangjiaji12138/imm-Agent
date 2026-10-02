"""Credential protected conversations and compact turns."""

from alembic import op
import sqlalchemy as sa

revision = "0002_conversations"
down_revision = "0001_knowledge"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("conversations",
                    sa.Column("id", sa.String(36), primary_key=True),
                    sa.Column("credential_hash", sa.String(64), nullable=False),
                    sa.Column("created_at", sa.DateTime(), nullable=False),
                    sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_table("messages",
                    sa.Column("id", sa.String(36), primary_key=True),
                    sa.Column("conversation_id", sa.String(36), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
                    sa.Column("sequence", sa.Integer(), nullable=False),
                    sa.Column("question", sa.String(500), nullable=False),
                    sa.Column("answer", sa.Text(), nullable=False),
                    sa.Column("result_type", sa.String(20), nullable=False),
                    sa.Column("request_id", sa.String(36), nullable=False, unique=True),
                    sa.Column("created_at", sa.DateTime(), nullable=False),
                    sa.UniqueConstraint("conversation_id", "sequence", name="uq_message_sequence"))
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])


def downgrade():
    op.drop_table("messages")
    op.drop_table("conversations")
