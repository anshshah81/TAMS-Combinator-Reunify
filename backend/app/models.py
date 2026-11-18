from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

def now():
    return datetime.now(timezone.utc)

class Incident(Base):
    __tablename__ = 'incidents'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    disaster_type: Mapped[str] = mapped_column(String(70))
    affected_region: Mapped[str] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(30), default='active')
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class MissingPersonReport(Base):
    __tablename__ = 'missing_person_reports'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    owner_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), index=True)
    owner: Mapped['User | None'] = relationship()
    eye_color: Mapped[str | None] = mapped_column(String(50))
    reporter_contact: Mapped[str | None] = mapped_column(String(200))
    consent: Mapped[bool] = mapped_column(Boolean, default=False)
    image_id: Mapped[str | None] = mapped_column(ForeignKey('images.id'), unique=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey('incidents.id'), index=True)
    name: Mapped[str] = mapped_column(String(200))
    nickname: Mapped[str | None] = mapped_column(String(120), nullable=True)
    approximate_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hair_color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    distinguishing_features: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_seen_location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    last_seen_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    clothing_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_image_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default='received')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class PatientRecord(Base):
    __tablename__ = 'patient_records'
    __table_args__ = (UniqueConstraint('organization_id', 'internal_id'),)
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey('organizations.id'), index=True)
    organization: Mapped['Organization | None'] = relationship()
    created_by: Mapped[str | None] = mapped_column(ForeignKey('users.id'))
    internal_id: Mapped[str | None] = mapped_column(String(100))
    eye_color: Mapped[str | None] = mapped_column(String(50))
    image_id: Mapped[str | None] = mapped_column(ForeignKey('images.id'), unique=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey('incidents.id'), index=True)
    hospital_id: Mapped[str] = mapped_column(String(70))
    approximate_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hair_color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    distinguishing_features: Mapped[str | None] = mapped_column(Text, nullable=True)
    observed_clothing: Mapped[str | None] = mapped_column(Text, nullable=True)
    intake_location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    admission_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    patient_image_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class MatchCandidate(Base):
    __tablename__ = 'match_candidates'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey('incidents.id'), index=True)
    missing_person_id: Mapped[str] = mapped_column(ForeignKey('missing_person_reports.id'))
    patient_id: Mapped[str] = mapped_column(ForeignKey('patient_records.id'))
    ranking_score: Mapped[float | None] = mapped_column(nullable=True)
    evidence_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default='needs_review')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ReviewDecision(Base):
    __tablename__ = 'review_decisions'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(ForeignKey('match_candidates.id'), index=True)
    reviewer_id: Mapped[str] = mapped_column(String(50))
    decision: Mapped[str] = mapped_column(String(50))
    previous_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    new_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Human-written attestation required to record an independent identity
    # verification; the AI/matching pipeline never populates this.
    attestation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(100))
    record_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Organization(Base):
    __tablename__ = 'organizations'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    kind: Mapped[str] = mapped_column(String(30))
    users: Mapped[list['User']] = relationship(back_populates='organization')


class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(30))
    organization_id: Mapped[str | None] = mapped_column(ForeignKey('organizations.id'), index=True)
    organization: Mapped[Organization | None] = relationship(back_populates='users')
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class AuthSession(Base):
    __tablename__ = 'auth_sessions'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class ImageAsset(Base):
    __tablename__ = 'images'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    purpose: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
