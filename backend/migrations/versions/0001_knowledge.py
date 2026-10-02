"""Initial knowledge schema, deliberately independent of mutable ORM models."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import LONGTEXT

revision = "0001_knowledge"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("organization", sa.String(255), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_key", sa.String(64), nullable=False, unique=True),
        sa.Column("language", sa.String(35), nullable=False),
        sa.Column("published_at", sa.Date(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("status IN ('pending','published','expired','withdrawn')", name="ck_document_status"),
    )
    op.create_table(
        "document_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.Text().with_variant(LONGTEXT(), "mysql"), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("document_id", "content_hash", name="uq_version_hash"),
        sa.UniqueConstraint("document_id", "version_number", name="uq_version_number"),
        sa.CheckConstraint("version_number > 0", name="ck_version_number"),
    )
    op.create_table(
        "chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("version_id", sa.String(36), sa.ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("title_path", sa.Text(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("char_start", sa.Integer(), nullable=False),
        sa.Column("char_end", sa.Integer(), nullable=False),
        sa.UniqueConstraint("version_id", "sequence", name="uq_chunk_sequence"),
        sa.CheckConstraint("sequence >= 0 AND char_start >= 0 AND char_end > char_start", name="ck_chunk_position"),
    )
    op.create_table(
        "terms",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("definition", sa.Text()),
    )
    op.create_table(
        "term_aliases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("term_id", sa.String(36), sa.ForeignKey("terms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("language", sa.String(35), nullable=False),
        sa.Column("alias", sa.String(255), nullable=False),
        sa.UniqueConstraint("language", "alias", name="uq_term_alias"),
    )
    op.create_table(
        "index_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_id", sa.String(36), sa.ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("action IN ('upsert','delete')", name="ck_job_action"),
        sa.CheckConstraint("status IN ('pending','running','succeeded','failed')", name="ck_job_status"),
        sa.CheckConstraint("attempts >= 0", name="ck_job_attempts"),
    )
    for table, columns in {
        "documents": ["language", "status"],
        "document_versions": ["document_id"],
        "chunks": ["version_id"],
        "term_aliases": ["term_id"],
        "index_jobs": ["document_id", "status"],
    }.items():
        for column in columns:
            op.create_index(f"ix_{table}_{column}", table, [column])


def downgrade():
    for table in ["index_jobs", "term_aliases", "terms", "chunks", "document_versions", "documents"]:
        op.drop_table(table)
