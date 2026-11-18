from datetime import datetime
from pydantic import BaseModel, ConfigDict

class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    disaster_type: str
    affected_region: str
    status: str
    start_time: datetime

class DemoOverview(BaseModel):
    demo_only: bool = True
    incident_count: int
    missing_reports: int
    hospital_records: int
    suggested_matches: int
    candidates_needing_review: int
    verified_resolutions: int
