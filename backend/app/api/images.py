"""Authenticated image intake and authorized retrieval.

Images are validated, re-encoded, and stripped of metadata before storage, kept
in private per-key files (never a public static directory), and returned only to
the uploader or an authorized reviewer/administrator.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile
from ..core.auth import current_user, get_db, get_storage, require_csrf
from sqlalchemy import select
from ..core.ids import new_image_key
from ..intake_schemas import ImageUploadOut
from ..models import ImageAsset, MissingPersonReport, PatientRecord, User
from ..services.image_storage import InvalidImage, sanitize_image

router = APIRouter(prefix='/api/v1/images', tags=['images'])

# role -> the single image purpose that role may create.
PURPOSE_BY_ROLE = {'family': 'report', 'hospital': 'patient'}


def _read_bounded(upload: UploadFile, limit: int) -> bytes:
    data = bytearray()
    while True:
        chunk = upload.file.read(64 * 1024)
        if not chunk:
            break
        data.extend(chunk)
        if len(data) > limit:
            raise HTTPException(413, 'Image exceeds the allowed size.')
    return bytes(data)


@router.post('', response_model=ImageUploadOut, dependencies=[Depends(require_csrf)])
async def upload_image(request: Request, file: UploadFile, user: User = Depends(current_user),
                       db=Depends(get_db)):
    purpose = PURPOSE_BY_ROLE.get(user.role)
    if purpose is None:
        raise HTTPException(403, 'This account cannot upload intake images.')
    raw = _read_bounded(file, request.app.state.settings.max_image_bytes)
    if not raw:
        raise HTTPException(400, 'Empty upload.')
    try:
        cleaned = sanitize_image(raw)
    except InvalidImage as error:
        raise HTTPException(400, str(error))
    key = new_image_key()
    storage = get_storage(request)
    storage.put(key, cleaned)
    try:
        db.add(ImageAsset(id=key, owner_id=user.id, purpose=purpose))
        db.commit()
    except Exception:
        db.rollback()
        storage.delete(key)  # avoid orphaning a stored file on a failed insert
        raise
    return ImageUploadOut(image_id=key)


def claim_image(db, storage, image_id: str | None, user: User, purpose: str) -> str | None:
    """Validate that an uploaded image belongs to the user and matches the
    intended purpose, and is not already attached elsewhere. Returns the id or
    raises. Callers set the returned id on the owning record."""
    if image_id is None:
        return None
    asset = db.get(ImageAsset, image_id)
    if asset is None or asset.owner_id != user.id or asset.purpose != purpose:
        raise HTTPException(400, 'Referenced image is not available.')
    already_used = db.scalar(
        select(MissingPersonReport.id).where(MissingPersonReport.image_id == image_id)
    ) or db.scalar(select(PatientRecord.id).where(PatientRecord.image_id == image_id))
    if already_used is not None:
        raise HTTPException(400, 'Image is already attached to a record.')
    return image_id


@router.get('/{image_id}')
def get_image(image_id: str, request: Request, user: User = Depends(current_user), db=Depends(get_db)):
    asset = db.get(ImageAsset, image_id)
    authorized = asset is not None and (asset.owner_id == user.id or user.role in ('reviewer', 'admin'))
    if not authorized:
        raise HTTPException(404, 'Image not found.')
    try:
        content = get_storage(request).read(image_id)
    except (FileNotFoundError, ValueError):
        raise HTTPException(404, 'Image not found.')
    return Response(content=content, media_type='image/png',
                    headers={'Cache-Control': 'no-store'})
