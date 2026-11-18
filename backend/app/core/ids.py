import uuid


def new_id(prefix: str) -> str:
    """Opaque, non-sequential record id. Intake ids deliberately avoid the
    seeded scenario prefixes so live submissions never alter public totals."""
    return f'{prefix}-{uuid.uuid4().hex[:16].upper()}'


def new_image_key() -> str:
    """32-char lowercase hex key matching the storage and schema contract."""
    return uuid.uuid4().hex
