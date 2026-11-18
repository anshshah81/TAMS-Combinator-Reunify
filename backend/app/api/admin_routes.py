"""Administrator management: incident status, directory, and audit access.

Administrators oversee incidents and accounts and read the immutable audit log.
These endpoints never expose medical or biometric detail; the audit log carries
only actor, action, and record identifiers.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from typing import Annotated, Literal
from ..core.audit import record as audit
from ..core.auth import get_db, require_csrf, roles
from ..models import AuditLog, Incident, Organization, User

router = APIRouter(prefix='/api/v1/admin', tags=['admin'])


class IncidentStatusIn(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    status: Literal['active', 'monitoring', 'closed']


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    status: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    display_name: str
    role: str
    organization_id: str | None
    active: bool


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    kind: str


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    actor_id: str
    action: str
    record_id: str | None
    occurred_at: datetime


@router.get('/users', response_model=list[UserOut])
def list_users(_: User = Depends(roles('admin')), db=Depends(get_db)):
    return db.scalars(select(User).order_by(User.id)).all()


@router.get('/organizations', response_model=list[OrganizationOut])
def list_organizations(_: User = Depends(roles('admin')), db=Depends(get_db)):
    return db.scalars(select(Organization).order_by(Organization.id)).all()


@router.get('/audit-logs', response_model=list[AuditOut])
def list_audit_logs(_: User = Depends(roles('admin')), db=Depends(get_db)):
    return db.scalars(select(AuditLog).order_by(AuditLog.occurred_at.desc())).all()


@router.patch('/incidents/{incident_id}', response_model=IncidentOut,
              dependencies=[Depends(require_csrf)])
def set_incident_status(incident_id: str, payload: IncidentStatusIn, request: Request,
                        user: User = Depends(roles('admin')), db=Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(404, 'Incident not found.')
    incident.status = payload.status
    audit(db, user.id, 'incident.status_changed', incident.id)
    db.commit()
    db.refresh(incident)
    return incident
