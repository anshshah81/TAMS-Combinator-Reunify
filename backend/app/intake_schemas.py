from datetime import datetime, timezone
from typing import Annotated, Literal
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

Short = Annotated[str, Field(min_length=1, max_length=50)]
Description = Annotated[str, Field(min_length=1, max_length=2000)]


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class LoginIn(Input):
    user_id: Annotated[str, Field(min_length=1, max_length=50)]


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    display_name: str
    role: Literal['family', 'hospital', 'reviewer', 'admin']
    organization_id: str | None


class PhysicalDetails(Input):
    incident_id: Annotated[str, Field(min_length=1, max_length=50)]
    approximate_age: Annotated[int, Field(ge=0, le=120)] | None = None
    height_cm: Annotated[int, Field(ge=30, le=250)] | None = None
    hair_color: Short | None = None
    eye_color: Short | None = None
    distinguishing_features: Description | None = None
    image_id: Annotated[str, Field(pattern=r'^[a-f0-9]{32}$')] | None = None


class ReportIn(PhysicalDetails):
    name: Annotated[str, Field(min_length=1, max_length=200)]
    nickname: Annotated[str, Field(min_length=1, max_length=120)] | None = None
    last_seen_location: Annotated[str, Field(min_length=1, max_length=200)]
    last_seen_time: AwareDatetime
    clothing_description: Description | None = None
    reporter_contact: Annotated[str, Field(min_length=3, max_length=200)]
    consent: Literal[True]

    @field_validator('last_seen_time')
    @classmethod
    def normalize_time(cls, value):
        if value > datetime.now(timezone.utc):
            raise ValueError('Time cannot be in the future.')
        return value.astimezone(timezone.utc)


class PatientIn(PhysicalDetails):
    internal_id: Annotated[str, Field(min_length=1, max_length=100)]
    observed_clothing: Description | None = None
    intake_location: Annotated[str, Field(min_length=1, max_length=200)] | None = None
    admission_time: AwareDatetime | None = None
    consent: Literal[True]

    @field_validator('admission_time')
    @classmethod
    def normalize_time(cls, value):
        if value is None:
            return value
        if value > datetime.now(timezone.utc):
            raise ValueError('Time cannot be in the future.')
        return value.astimezone(timezone.utc)


class DemoAccountOut(BaseModel):
    """Fictional sign-in choices surfaced only while demo auth is enabled."""
    model_config = ConfigDict(from_attributes=True)
    id: str
    display_name: str
    role: Literal['family', 'hospital', 'reviewer', 'admin']


class ImageUploadOut(BaseModel):
    image_id: str


class ReportCreatedOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: str
    created_at: datetime


class TrackingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: str
    created_at: datetime


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    incident_id: str
    organization_id: str | None
    internal_id: str | None
    approximate_age: int | None
    height_cm: int | None
    hair_color: str | None
    eye_color: str | None
    distinguishing_features: str | None
    observed_clothing: str | None
    intake_location: str | None
    admission_time: datetime | None
    image_id: str | None
