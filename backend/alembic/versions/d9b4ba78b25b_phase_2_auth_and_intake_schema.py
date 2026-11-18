"""phase 2 auth and intake schema

Adds synthetic-demo authentication (organizations, users, sessions) and intake
ownership: image assets plus report/patient owner, organization, internal id,
eye color, consent, and image references.

Revision ID: d9b4ba78b25b
Revises: 059fe07f326f
"""
from alembic import op
import sqlalchemy as sa

revision = 'd9b4ba78b25b'
down_revision = '059fe07f326f'
branch_labels = None
depends_on = None

# SQLite batch mode recreates tables; it needs deterministic names for the
# existing unnamed constraints it copies. Supplying a naming convention keeps
# this migration self-contained without changing the application metadata.
NAMING_CONVENTION = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}


def upgrade():
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('kind', sa.String(length=30), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=30), nullable=False),
        sa.Column('organization_id', sa.String(length=50), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)
    op.create_table(
        'auth_sessions',
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('token_hash'),
    )
    op.create_index(op.f('ix_auth_sessions_expires_at'), 'auth_sessions', ['expires_at'], unique=False)
    op.create_index(op.f('ix_auth_sessions_user_id'), 'auth_sessions', ['user_id'], unique=False)
    op.create_table(
        'images',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('owner_id', sa.String(length=50), nullable=False),
        sa.Column('purpose', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_images_owner_id'), 'images', ['owner_id'], unique=False)

    with op.batch_alter_table('missing_person_reports', naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.add_column(sa.Column('owner_id', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('eye_color', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('reporter_contact', sa.String(length=200), nullable=True))
        # Existing Phase 1 rows predate consent; backfill them as not-consented.
        batch_op.add_column(sa.Column('consent', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column('image_id', sa.String(length=50), nullable=True))
        batch_op.create_index(batch_op.f('ix_missing_person_reports_owner_id'), ['owner_id'], unique=False)
        batch_op.create_unique_constraint('uq_missing_person_reports_image_id', ['image_id'])
        batch_op.create_foreign_key('fk_missing_person_reports_image_id_images', 'images', ['image_id'], ['id'])
        batch_op.create_foreign_key('fk_missing_person_reports_owner_id_users', 'users', ['owner_id'], ['id'])

    with op.batch_alter_table('patient_records', naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.add_column(sa.Column('organization_id', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('internal_id', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('eye_color', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('image_id', sa.String(length=50), nullable=True))
        batch_op.create_index(batch_op.f('ix_patient_records_organization_id'), ['organization_id'], unique=False)
        batch_op.create_unique_constraint('uq_patient_records_image_id', ['image_id'])
        batch_op.create_unique_constraint('uq_patient_records_organization_id', ['organization_id', 'internal_id'])
        batch_op.create_foreign_key('fk_patient_records_created_by_users', 'users', ['created_by'], ['id'])
        batch_op.create_foreign_key('fk_patient_records_image_id_images', 'images', ['image_id'], ['id'])
        batch_op.create_foreign_key('fk_patient_records_organization_id_organizations', 'organizations', ['organization_id'], ['id'])


def downgrade():
    # Dropping the columns in batch mode recreates each table without the
    # column-bound unique and foreign-key constraints, so they need no explicit drop.
    with op.batch_alter_table('patient_records', naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.drop_index(batch_op.f('ix_patient_records_organization_id'))
        batch_op.drop_column('image_id')
        batch_op.drop_column('eye_color')
        batch_op.drop_column('internal_id')
        batch_op.drop_column('created_by')
        batch_op.drop_column('organization_id')

    with op.batch_alter_table('missing_person_reports', naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.drop_index(batch_op.f('ix_missing_person_reports_owner_id'))
        batch_op.drop_column('image_id')
        batch_op.drop_column('consent')
        batch_op.drop_column('reporter_contact')
        batch_op.drop_column('eye_color')
        batch_op.drop_column('owner_id')

    op.drop_index(op.f('ix_images_owner_id'), table_name='images')
    op.drop_table('images')
    op.drop_index(op.f('ix_auth_sessions_user_id'), table_name='auth_sessions')
    op.drop_index(op.f('ix_auth_sessions_expires_at'), table_name='auth_sessions')
    op.drop_table('auth_sessions')
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_table('users')
    op.drop_table('organizations')
