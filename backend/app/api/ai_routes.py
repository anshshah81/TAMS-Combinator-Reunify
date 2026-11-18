"""Restricted AI evidence endpoints for reviewers and administrators.

These return uncertain evidence (face distance, clothing detections) to support
human investigation. They never verify identity or change case status.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from ..core.auth import get_db, get_settings, get_storage, require_csrf, roles
from ..models import ImageAsset, User
from ..services.ai.face_matching import FaceMatchingUnavailable, compare_faces, get_matcher

router = APIRouter(prefix='/api/v1', tags=['ai'])

ImageId = Annotated[str, Field(pattern=r'^[a-f0-9]{32}$')]


class FaceCompareIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    reference_image_id: ImageId
    candidate_image_id: ImageId


class FaceComparisonOut(BaseModel):
    status: str
    distance: float | None
    model: str
    detector: str
    warning: str | None
    mock: bool


def _resolve_path(storage, db, image_id: str):
    if db.get(ImageAsset, image_id) is None:
        raise HTTPException(404, 'Image not found.')
    try:
        return storage.path(image_id)
    except (AttributeError, ValueError):
        raise HTTPException(400, 'Image is not available for comparison.')


@router.post('/face-comparisons', response_model=FaceComparisonOut,
             dependencies=[Depends(require_csrf)])
def create_face_comparison(payload: FaceCompareIn, request: Request,
                           _: User = Depends(roles('reviewer', 'admin')), db=Depends(get_db)):
    storage = get_storage(request)
    reference = _resolve_path(storage, db, payload.reference_image_id)
    candidate = _resolve_path(storage, db, payload.candidate_image_id)
    try:
        matcher = get_matcher(get_settings(request).face_match_mode)
    except FaceMatchingUnavailable as error:
        # Do not substitute a mock result for a missing real backend.
        raise HTTPException(503, str(error))
    result = compare_faces(reference, candidate, matcher=matcher)
    return FaceComparisonOut(**result.as_dict())
