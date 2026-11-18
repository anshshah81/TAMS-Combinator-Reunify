"""Family missing-person intake and limited self-service tracking.

A family reporter may create reports and see only their own. Tracking exposes a
narrow status projection and never reveals patient records or match candidates.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from ..core.auth import get_db, get_storage, require_csrf, roles
from ..core.ids import new_id
from ..intake_schemas import ReportCreatedOut, ReportIn, TrackingOut
from ..models import Incident, MissingPersonReport, User
from .images import claim_image

router = APIRouter(prefix='/api/v1/reports', tags=['reports'])


@router.post('', response_model=ReportCreatedOut, status_code=201,
             dependencies=[Depends(require_csrf)])
def create_report(payload: ReportIn, request: Request,
                  user: User = Depends(roles('family')), db=Depends(get_db)):
    incident = db.get(Incident, payload.incident_id)
    if incident is None:
        raise HTTPException(400, 'Unknown incident.')
    image_id = claim_image(db, get_storage(request), payload.image_id, user, 'report')
    report = MissingPersonReport(
        id=new_id('MPR'),
        owner_id=user.id,
        incident_id=payload.incident_id,
        name=payload.name,
        nickname=payload.nickname,
        approximate_age=payload.approximate_age,
        height_cm=payload.height_cm,
        hair_color=payload.hair_color,
        eye_color=payload.eye_color,
        distinguishing_features=payload.distinguishing_features,
        last_seen_location=payload.last_seen_location,
        last_seen_time=payload.last_seen_time,
        clothing_description=payload.clothing_description,
        reporter_contact=payload.reporter_contact,
        consent=payload.consent,
        image_id=image_id,
        status='received',
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get('', response_model=list[ReportCreatedOut])
def list_own_reports(user: User = Depends(roles('family')), db=Depends(get_db)):
    reports = db.scalars(
        select(MissingPersonReport).where(MissingPersonReport.owner_id == user.id)
        .order_by(MissingPersonReport.created_at.desc())
    ).all()
    return reports


@router.get('/{report_id}/tracking', response_model=TrackingOut)
def track_report(report_id: str, user: User = Depends(roles('family')), db=Depends(get_db)):
    report = db.get(MissingPersonReport, report_id)
    if report is None or report.owner_id != user.id:
        raise HTTPException(404, 'Report not found.')
    return report
