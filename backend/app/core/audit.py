"""Append-only audit trail.

Records are only ever inserted, never updated or deleted, so the history of who
did what to which record stays immutable. Audit entries intentionally store only
an actor id, an action name, and a record id -- never medical or biometric detail.
"""
from ..core.ids import new_id
from ..models import AuditLog


def record(db, actor_id: str, action: str, record_id: str | None = None) -> AuditLog:
    entry = AuditLog(id=new_id('AUD'), actor_id=actor_id, action=action, record_id=record_id)
    db.add(entry)
    return entry
