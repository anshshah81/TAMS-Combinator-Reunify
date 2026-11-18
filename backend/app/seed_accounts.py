"""Fictional demo identities only; not an account-registration system."""
from .models import Organization, User
from .db import SessionLocal

ACCOUNTS = (
    ('family-demo', 'Demo family reporter', 'family', None),
    ('family-other', 'Second demo reporter', 'family', None),
    ('hospital-demo', 'Demo hospital A staff', 'hospital', 'SYNTH-HOSPITAL-1'),
    ('hospital-other', 'Demo hospital B staff', 'hospital', 'SYNTH-HOSPITAL-2'),
    ('reviewer-demo', 'Demo emergency reviewer', 'reviewer', 'SYNTH-RESPONSE'),
    ('admin-demo', 'Demo administrator', 'admin', 'SYNTH-RESPONSE'),
)


def seed_demo_accounts(db):
    for key, name, kind in [('SYNTH-HOSPITAL-1', 'Synthetic Hospital A', 'hospital'),
                            ('SYNTH-HOSPITAL-2', 'Synthetic Hospital B', 'hospital'),
                            ('SYNTH-RESPONSE', 'Synthetic Response Team', 'response')]:
        if db.get(Organization, key) is None:
            db.add(Organization(id=key, name=name, kind=kind))
    db.flush()
    for key, name, role, organization in ACCOUNTS:
        if db.get(User, key) is None:
            db.add(User(id=key, display_name=name, role=role, organization_id=organization))
    db.commit()


if __name__ == '__main__':
    from .core.settings import Settings
    if not Settings.from_env().demo_auth:
        raise SystemExit('Enable development-only demo authentication before seeding accounts.')
    with SessionLocal() as db:
        seed_demo_accounts(db)
    print('Fictional demo accounts ready.')
