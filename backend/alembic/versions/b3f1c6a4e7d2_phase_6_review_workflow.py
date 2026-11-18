"""phase 6 review workflow

Extends review_decisions with the status transition (previous/new) and the
human attestation required to record an independent identity verification.
Review decisions and audit logs are append-only; nothing here deletes history.

Revision ID: b3f1c6a4e7d2
Revises: d9b4ba78b25b
"""
from alembic import op
import sqlalchemy as sa

revision = 'b3f1c6a4e7d2'
down_revision = 'd9b4ba78b25b'
branch_labels = None
depends_on = None

# See the Phase 2 migration: SQLite batch mode copies existing unnamed
# constraints and needs deterministic names to do so.
NAMING_CONVENTION = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}


def upgrade():
    with op.batch_alter_table('review_decisions', naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.add_column(sa.Column('previous_status', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('new_status', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('attestation', sa.Text(), nullable=True))
        batch_op.create_index(batch_op.f('ix_review_decisions_candidate_id'), ['candidate_id'], unique=False)


def downgrade():
    with op.batch_alter_table('review_decisions', naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.drop_index(batch_op.f('ix_review_decisions_candidate_id'))
        batch_op.drop_column('attestation')
        batch_op.drop_column('new_status')
        batch_op.drop_column('previous_status')
