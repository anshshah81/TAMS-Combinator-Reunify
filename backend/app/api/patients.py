"""Hospital unidentified-patient intake.

Organization and creator are derived from the authenticated session, never from
the request body. Hospital staff see only their own organization's records;
reviewers and administrators may read records to support investigation. Family
accounts have no access to this router.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from ..core.auth import current_user, get_db, get_storage, require_csrf, roles
from ..core.ids import new_id
from ..intake_schemas import PatientIn, PatientOut
from ..models import Incident, PatientRecord, User
from .images import claim_image

router = APIRouter(prefix='/api/v1/patients', tags=['patients'])


@router.post('', response_model=PatientOut, status_code=201,
             dependencies=[Depends(require_csrf)])
def create_patient(payload: PatientIn, request: Request,
                   user: User = Depends(roles('hospital')), db=Depends(get_db)):
    if user.organization_id is None:
        raise HTTPException(403, 'This account is not linked to a hospital organization.')
    incident = db.get(Incident, payload.incident_id)
    if incident is None:
        raise HTTPException(400, 'Unknown incident.')
    duplicate = db.scalar(select(PatientRecord.id).where(
        PatientRecord.organization_id == user.organization_id,
        PatientRecord.internal_id == payload.internal_id,
    ))
    if duplicate is not None:
        raise HTTPException(409, 'A patient with this internal identifier already exists.')
    image_id = claim_image(db, get_storage(request), payload.image_id, user, 'patient')
    patient = PatientRecord(
        id=new_id('PAT'),
        organization_id=user.organization_id,
        created_by=user.id,
        hospital_id=user.organization_id,
        internal_id=payload.internal_id,
        incident_id=payload.incident_id,
        approximate_age=payload.approximate_age,
        height_cm=payload.height_cm,
        hair_color=payload.hair_color,
        eye_color=payload.eye_color,
        distinguishing_features=payload.distinguishing_features,
        observed_clothing=payload.observed_clothing,
        intake_location=payload.intake_location,
        admission_time=payload.admission_time,
        image_id=image_id,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get('', response_model=list[PatientOut])
def list_patients(user: User = Depends(roles('hospital', 'reviewer', 'admin')), db=Depends(get_db)):
    statement = select(PatientRecord).order_by(PatientRecord.created_at.desc())
    if user.role == 'hospital':
        statement = statement.where(PatientRecord.organization_id == user.organization_id)
    return db.scalars(statement).all()


@router.get('/{patient_id}', response_model=PatientOut)
def get_patient(patient_id: str, user: User = Depends(roles('hospital', 'reviewer', 'admin')),
                db=Depends(get_db)):
    patient = db.get(PatientRecord, patient_id)
    if patient is None:
        raise HTTPException(404, 'Patient record not found.')
    if user.role == 'hospital' and patient.organization_id != user.organization_id:
        # Do not disclose existence of another organization's record.
        raise HTTPException(404, 'Patient record not found.')
    return patient
