"""Reviewer investigation and human-decision workflow.

Reviewers and administrators investigate candidates side by side and record
decisions. Only a human can record an identity verification, and only with a
written attestation; the AI/matching pipeline never sets a verified status and
never contacts families. Every decision is written to the immutable audit log.
"""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from typing import Annotated, Literal
from ..core.audit import record as audit
from ..core.auth import get_db, require_csrf, roles
from ..core.ids import new_id
from ..models import MatchCandidate, MissingPersonReport, PatientRecord, ReviewDecision, User

router = APIRouter(prefix='/api/v1/match-candidates', tags=['review'])

# Reviewer action -> resulting candidate status.
ACTIONS = {
    'investigate': 'investigating',
    'request_info': 'info_requested',
    'reject': 'rejected',
    'verify': 'verified',
}
# Once a candidate is rejected or verified, its decision is final.
TERMINAL = {'rejected', 'verified'}


class DecisionIn(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    decision: Literal['investigate', 'request_info', 'reject', 'verify']
    notes: Annotated[str, Field(min_length=1, max_length=4000)] | None = None
    # Required only for `verify`: a human attestation of independent evidence.
    attestation: Annotated[str, Field(min_length=10, max_length=4000)] | None = None


class DecisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    candidate_id: str
    reviewer_id: str
    decision: str
    previous_status: str | None
    new_status: str | None
    notes: str | None
    attestation: str | None
    created_at: datetime


class InvestigationOut(BaseModel):
    candidate_id: str
    status: str
    ranking_score: float | None
    evidence: dict | None
    report: dict
    patient: dict


def _report_view(report: MissingPersonReport) -> dict:
    return {
        'id': report.id, 'name': report.name, 'nickname': report.nickname,
        'approximate_age': report.approximate_age, 'height_cm': report.height_cm,
        'hair_color': report.hair_color, 'eye_color': report.eye_color,
        'distinguishing_features': report.distinguishing_features,
        'last_seen_location': report.last_seen_location, 'last_seen_time': report.last_seen_time,
        'clothing_description': report.clothing_description, 'image_id': report.image_id,
    }


def _patient_view(patient: PatientRecord) -> dict:
    return {
        'id': patient.id, 'internal_id': patient.internal_id,
        'approximate_age': patient.approximate_age, 'height_cm': patient.height_cm,
        'hair_color': patient.hair_color, 'eye_color': patient.eye_color,
        'distinguishing_features': patient.distinguishing_features,
        'observed_clothing': patient.observed_clothing, 'intake_location': patient.intake_location,
        'admission_time': patient.admission_time, 'image_id': patient.image_id,
    }


def _load(db, candidate_id: str) -> MatchCandidate:
    candidate = db.get(MatchCandidate, candidate_id)
    if candidate is None:
        raise HTTPException(404, 'Candidate not found.')
    return candidate


@router.get('/{candidate_id}/investigation', response_model=InvestigationOut)
def investigation_view(candidate_id: str, _: User = Depends(roles('reviewer', 'admin')),
                       db=Depends(get_db)):
    candidate = _load(db, candidate_id)
    report = db.get(MissingPersonReport, candidate.missing_person_id)
    patient = db.get(PatientRecord, candidate.patient_id)
    try:
        evidence = json.loads(candidate.evidence_json) if candidate.evidence_json else None
    except json.JSONDecodeError:
        evidence = None
    return InvestigationOut(
        candidate_id=candidate.id, status=candidate.status, ranking_score=candidate.ranking_score,
        evidence=evidence, report=_report_view(report), patient=_patient_view(patient))


@router.get('/{candidate_id}/decisions', response_model=list[DecisionOut])
def list_decisions(candidate_id: str, _: User = Depends(roles('reviewer', 'admin')), db=Depends(get_db)):
    _load(db, candidate_id)
    return db.scalars(select(ReviewDecision).where(ReviewDecision.candidate_id == candidate_id)
                      .order_by(ReviewDecision.created_at.desc())).all()


@router.post('/{candidate_id}/decisions', response_model=DecisionOut, status_code=201,
             dependencies=[Depends(require_csrf)])
def record_decision(candidate_id: str, payload: DecisionIn, request: Request,
                    user: User = Depends(roles('reviewer', 'admin')), db=Depends(get_db)):
    candidate = _load(db, candidate_id)
    if candidate.status in TERMINAL:
        raise HTTPException(409, 'This candidate already has a final decision.')

    new_status = ACTIONS[payload.decision]
    if payload.decision == 'verify' and not (payload.attestation and payload.notes):
        # A verification must carry a human attestation and supporting notes.
        raise HTTPException(422, 'Recording a verification requires notes and a written attestation.')

    previous_status = candidate.status
    decision = ReviewDecision(
        id=new_id('REV'), candidate_id=candidate.id, reviewer_id=user.id,
        decision=payload.decision, previous_status=previous_status, new_status=new_status,
        notes=payload.notes, attestation=payload.attestation if payload.decision == 'verify' else None)
    db.add(decision)
    candidate.status = new_status

    # Project a coarse, detail-free status back to the family's report.
    report = db.get(MissingPersonReport, candidate.missing_person_id)
    if report is not None:
        if new_status == 'verified':
            report.status = 'resolved'
        elif new_status in {'investigating', 'info_requested'} and report.status == 'received':
            report.status = 'under_review'

    audit(db, user.id, f'candidate.{payload.decision}', candidate.id)
    if payload.decision == 'verify':
        audit(db, user.id, 'identity.verified', candidate.id)
    db.commit()
    db.refresh(decision)
    return decision
