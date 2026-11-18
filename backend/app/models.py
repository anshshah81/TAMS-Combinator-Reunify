from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
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
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
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
    candidate_id: Mapped[str] = mapped_column(ForeignKey('match_candidates.id'))
    reviewer_id: Mapped[str] = mapped_column(String(50))
    decision: Mapped[str] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(100))
    record_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
