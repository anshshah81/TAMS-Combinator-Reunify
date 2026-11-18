from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Incident, MissingPersonReport, PatientRecord, MatchCandidate

def seed_synthetic_demo(db: Session) -> None:
    if db.scalar(select(Incident.id).limit(1)) is not None:
        return
    # SYNTHETIC CASES ONLY. No real identities or images.
    db.add(Incident(id='INC-DEMO-001', name='Hill Country Flood — Training Exercise', disaster_type='flood', affected_region='Central Texas (synthetic)', status='active', start_time=datetime(2026, 6, 1, tzinfo=timezone.utc)))
    db.add(Incident(id='INC-DEMO-002', name='Coastal Storm — Training Exercise', disaster_type='storm', affected_region='Gulf Coast (synthetic)', status='closed', start_time=datetime(2026, 5, 1, tzinfo=timezone.utc)))
    db.flush()
    db.add_all([
        MissingPersonReport(id='M-DEMO-101', incident_id='INC-DEMO-001', name='Jordan Reed (synthetic)', approximate_age=26, height_cm=165, hair_color='dark', distinguishing_features='small scar on left forearm', last_seen_location='Synthetic Town A', clothing_description='red hoodie and blue jeans'),
        MissingPersonReport(id='M-DEMO-102', incident_id='INC-DEMO-001', name='Taylor Quinn (synthetic)', approximate_age=44, height_cm=172, hair_color='brown', clothing_description='gray jacket', status='received'),
        PatientRecord(id='H-DEMO-201', incident_id='INC-DEMO-001', hospital_id='SYNTH-HOSPITAL-1', approximate_age=28, height_cm=166, hair_color='dark', distinguishing_features='scar on left forearm', observed_clothing='blue jeans', intake_location='Synthetic Hospital A'),
        PatientRecord(id='H-DEMO-202', incident_id='INC-DEMO-001', hospital_id='SYNTH-HOSPITAL-2', approximate_age=61, height_cm=180, hair_color='gray', intake_location='Synthetic Hospital B'),
    ])
    db.flush()
    db.add(MatchCandidate(id='C-DEMO-301', incident_id='INC-DEMO-001', missing_person_id='M-DEMO-101', patient_id='H-DEMO-201', evidence_json='{"demo":true,"note":"Placeholder candidate, not from inference"}', status='needs_review'))
    db.commit()


if __name__ == '__main__':
    from .db import SessionLocal
    with SessionLocal() as session:
        seed_synthetic_demo(session)
    print('Synthetic exercise seed ready; existing data preserved.')
