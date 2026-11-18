"""Restricted candidate-matching API for reviewers and administrators.

Generates and lists ranked candidates with transparent evidence. Generating
candidates never sets a verified status or contacts anyone; it only records
suggestions for human investigation. Family accounts have no access.
"""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from ..core.auth import get_db, require_csrf, roles
from ..core.ids import new_id
from ..models import Incident, MatchCandidate, MissingPersonReport, PatientRecord, User
from ..services.ai.match_engine import rank_candidates

router = APIRouter(prefix='/api/v1', tags=['matching'])


class MatchCandidateOut(BaseModel):
    id: str
    incident_id: str
    missing_person_id: str
    patient_id: str
    ranking_score: float | None
    status: str
    evidence: dict | None
    created_at: datetime


def _serialize(candidate: MatchCandidate) -> MatchCandidateOut:
    try:
        evidence = json.loads(candidate.evidence_json) if candidate.evidence_json else None
    except json.JSONDecodeError:
        evidence = None
    return MatchCandidateOut(
        id=candidate.id, incident_id=candidate.incident_id,
        missing_person_id=candidate.missing_person_id, patient_id=candidate.patient_id,
        ranking_score=candidate.ranking_score, status=candidate.status,
        evidence=evidence, created_at=candidate.created_at,
    )


@router.post('/incidents/{incident_id}/candidates', response_model=list[MatchCandidateOut],
             dependencies=[Depends(require_csrf)])
def generate_candidates(incident_id: str, request: Request,
                        _: User = Depends(roles('reviewer', 'admin')), db=Depends(get_db)):
    if db.get(Incident, incident_id) is None:
        raise HTTPException(404, 'Incident not found.')
    reports = db.scalars(select(MissingPersonReport).where(
        MissingPersonReport.incident_id == incident_id)).all()
    patients = db.scalars(select(PatientRecord).where(
        PatientRecord.incident_id == incident_id)).all()

    generated: list[MatchCandidate] = []
    for report in reports:
        for patient, evidence in rank_candidates(report, patients):
            existing = db.scalar(select(MatchCandidate).where(
                MatchCandidate.missing_person_id == report.id,
                MatchCandidate.patient_id == patient.id))
            payload = json.dumps(evidence.as_dict())
            if existing is not None:
                # Refresh evidence/score but never overwrite a reviewer's status.
                existing.evidence_json = payload
                existing.ranking_score = float(evidence.score)
                generated.append(existing)
            else:
                candidate = MatchCandidate(
                    id=new_id('CAND'), incident_id=incident_id, missing_person_id=report.id,
                    patient_id=patient.id, ranking_score=float(evidence.score),
                    evidence_json=payload, status='needs_review')
                db.add(candidate)
                generated.append(candidate)
    db.commit()
    generated.sort(key=lambda candidate: candidate.ranking_score or 0, reverse=True)
    return [_serialize(candidate) for candidate in generated]


@router.get('/match-candidates', response_model=list[MatchCandidateOut])
def list_candidates(incident_id: str | None = None,
                    _: User = Depends(roles('reviewer', 'admin')), db=Depends(get_db)):
    statement = select(MatchCandidate).order_by(MatchCandidate.ranking_score.desc().nullslast(),
                                                MatchCandidate.id)
    if incident_id:
        statement = statement.where(MatchCandidate.incident_id == incident_id)
    return [_serialize(candidate) for candidate in db.scalars(statement).all()]


@router.get('/match-candidates/{candidate_id}', response_model=MatchCandidateOut)
def get_candidate(candidate_id: str, _: User = Depends(roles('reviewer', 'admin')), db=Depends(get_db)):
    candidate = db.get(MatchCandidate, candidate_id)
    if candidate is None:
        raise HTTPException(404, 'Candidate not found.')
    return _serialize(candidate)
