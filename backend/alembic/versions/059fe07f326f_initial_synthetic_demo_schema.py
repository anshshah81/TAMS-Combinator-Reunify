"""Initial synthetic demo schema

Revision ID: 059fe07f326f
Revises: none
"""
from alembic import op
import sqlalchemy as sa

revision = '059fe07f326f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('audit_logs',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('actor_id', sa.String(length=50), nullable=False),
    sa.Column('action', sa.String(length=100), nullable=False),
    sa.Column('record_id', sa.String(length=50), nullable=True),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('incidents',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('disaster_type', sa.String(length=70), nullable=False),
    sa.Column('affected_region', sa.String(length=150), nullable=False),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('missing_person_reports',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('incident_id', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('nickname', sa.String(length=120), nullable=True),
    sa.Column('approximate_age', sa.Integer(), nullable=True),
    sa.Column('height_cm', sa.Integer(), nullable=True),
    sa.Column('hair_color', sa.String(length=50), nullable=True),
    sa.Column('distinguishing_features', sa.Text(), nullable=True),
    sa.Column('last_seen_location', sa.String(length=200), nullable=True),
    sa.Column('last_seen_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('clothing_description', sa.Text(), nullable=True),
    sa.Column('reference_image_path', sa.String(length=300), nullable=True),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_missing_person_reports_incident_id'), 'missing_person_reports', ['incident_id'], unique=False)
    op.create_table('patient_records',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('incident_id', sa.String(length=50), nullable=False),
    sa.Column('hospital_id', sa.String(length=70), nullable=False),
    sa.Column('approximate_age', sa.Integer(), nullable=True),
    sa.Column('height_cm', sa.Integer(), nullable=True),
    sa.Column('hair_color', sa.String(length=50), nullable=True),
    sa.Column('distinguishing_features', sa.Text(), nullable=True),
    sa.Column('observed_clothing', sa.Text(), nullable=True),
    sa.Column('intake_location', sa.String(length=200), nullable=True),
    sa.Column('admission_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('patient_image_path', sa.String(length=300), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patient_records_incident_id'), 'patient_records', ['incident_id'], unique=False)
    op.create_table('match_candidates',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('incident_id', sa.String(length=50), nullable=False),
    sa.Column('missing_person_id', sa.String(length=50), nullable=False),
    sa.Column('patient_id', sa.String(length=50), nullable=False),
    sa.Column('ranking_score', sa.Float(), nullable=True),
    sa.Column('evidence_json', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
    sa.ForeignKeyConstraint(['missing_person_id'], ['missing_person_reports.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient_records.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_match_candidates_incident_id'), 'match_candidates', ['incident_id'], unique=False)
    op.create_table('review_decisions',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('candidate_id', sa.String(length=50), nullable=False),
    sa.Column('reviewer_id', sa.String(length=50), nullable=False),
    sa.Column('decision', sa.String(length=50), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['candidate_id'], ['match_candidates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('review_decisions')
    op.drop_index(op.f('ix_match_candidates_incident_id'), table_name='match_candidates')
    op.drop_table('match_candidates')
    op.drop_index(op.f('ix_patient_records_incident_id'), table_name='patient_records')
    op.drop_table('patient_records')
    op.drop_index(op.f('ix_missing_person_reports_incident_id'), table_name='missing_person_reports')
    op.drop_table('missing_person_reports')
    op.drop_table('incidents')
    op.drop_table('audit_logs')
