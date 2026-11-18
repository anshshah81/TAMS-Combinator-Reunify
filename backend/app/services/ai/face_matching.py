"""Facial similarity service.

Returns a structured comparison of two face images as *uncertain evidence*. A
small cosine/other distance is a signal for a human reviewer to investigate; it is
never an identity verification. There is no validated verification threshold for
disaster photographs, so this module deliberately does not classify "same person".

Adapters:
- MockFaceMatcher: default, deterministic, clearly labeled. Performs no real face
  detection or recognition.
- ArcFaceMatcher: opt-in real inference via DeepFace + ArcFace. Importing it
  requires the optional AI dependencies (see backend/requirements-ai.txt) and
  license review of the code and pretrained weights. It is never silently used in
  place of the mock, and a failure to load raises rather than faking a result.
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

from ..image_storage import InvalidImage, sanitize_image

# Possible outcomes. 'compared' carries a distance; the others explain why no
# distance is available and are distinct from each other and from an error.
STATUS_COMPARED = 'compared'
STATUS_NO_FACE = 'no_face'
STATUS_AMBIGUOUS = 'ambiguous_faces'
STATUS_ERROR = 'error'


class FaceMatchingUnavailable(RuntimeError):
    """Raised when a requested real adapter cannot be loaded. Never fall back to
    the mock silently; surface this so callers do not mistake mock output for
    real inference."""


@dataclass(frozen=True)
class FaceComparison:
    status: str
    distance: float | None
    model: str
    detector: str
    warning: str | None = None
    mock: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


class FaceMatcher(Protocol):
    model: str
    detector: str
    mock: bool

    def compare(self, reference: bytes, candidate: bytes) -> FaceComparison: ...


def _load_valid_image(path: str | Path) -> bytes:
    """Read and validate an image, raising InvalidImage/FileNotFoundError."""
    data = Path(path).read_bytes()
    if not data:
        raise InvalidImage('Image file is empty.')
    # sanitize_image enforces format, frame count, and pixel bounds.
    sanitize_image(data)
    return data


class MockFaceMatcher:
    """Deterministic, clearly labeled stand-in. Identical images yield distance
    0.0; different images yield a stable pseudo-distance in [0, 1). It does not
    detect faces and must never be presented as real evidence."""

    model = 'ArcFace (mock)'
    detector = 'mock'
    mock = True

    def compare(self, reference: bytes, candidate: bytes) -> FaceComparison:
        if reference == candidate:
            distance = 0.0
        else:
            digest = hashlib.sha256(reference + b'|' + candidate).digest()
            distance = round(int.from_bytes(digest[:4], 'big') / 2 ** 32, 4)
        return FaceComparison(
            status=STATUS_COMPARED, distance=distance, model=self.model, detector=self.detector,
            warning='Mock similarity only: no real face detection or recognition was performed, '
                    'and this is not identity verification.',
            mock=True,
        )


class ArcFaceMatcher:
    """Opt-in real adapter. Not exercised in ordinary CI (requires heavy deps and
    model weights). Importing DeepFace lazily keeps the standard install light."""

    model = 'ArcFace'
    detector = 'retinaface'
    mock = False

    def __init__(self) -> None:
        try:
            from deepface import DeepFace  # type: ignore  # noqa: F401
        except Exception as error:  # pragma: no cover - requires optional deps
            raise FaceMatchingUnavailable(
                'Real ArcFace inference requires the optional AI dependencies. '
                'Install backend/requirements-ai.txt and review model/weight licenses first.'
            ) from error
        self._deepface = DeepFace

    def compare(self, reference: bytes, candidate: bytes) -> FaceComparison:  # pragma: no cover
        import tempfile

        def represent(data: bytes):
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as handle:
                handle.write(data)
                path = handle.name
            try:
                return self._deepface.represent(
                    img_path=path, model_name='ArcFace', detector_backend='retinaface',
                    enforce_detection=True, align=True,
                )
            finally:
                Path(path).unlink(missing_ok=True)

        try:
            ref_faces = represent(reference)
            cand_faces = represent(candidate)
        except ValueError as error:
            return FaceComparison(STATUS_NO_FACE, None, self.model, self.detector, warning=str(error))
        # Refuse to guess which person to compare when multiple faces are present.
        if len(ref_faces) != 1 or len(cand_faces) != 1:
            return FaceComparison(
                STATUS_AMBIGUOUS, None, self.model, self.detector,
                warning='Multiple faces detected; select a single face before comparing.')
        distance = _cosine_distance(ref_faces[0]['embedding'], cand_faces[0]['embedding'])
        return FaceComparison(
            STATUS_COMPARED, round(float(distance), 4), self.model, self.detector,
            warning='Distance is uncertain evidence, not identity verification.')


def _cosine_distance(a, b) -> float:  # pragma: no cover - used only by real adapter
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 1.0
    return 1.0 - dot / (norm_a * norm_b)


def get_matcher(mode: str = 'mock') -> FaceMatcher:
    if mode == 'mock':
        return MockFaceMatcher()
    if mode == 'arcface':
        return ArcFaceMatcher()
    raise ValueError(f'Unknown face matching mode: {mode!r}')


def compare_faces(reference_image_path, candidate_image_path, matcher: FaceMatcher | None = None) -> FaceComparison:
    """Compare two face images and return structured evidence with model metadata.

    Validates both images first and reports a distinct 'error' status (never a
    fabricated distance) when an image is missing or unusable.
    """
    matcher = matcher or MockFaceMatcher()
    try:
        reference = _load_valid_image(reference_image_path)
        candidate = _load_valid_image(candidate_image_path)
    except FileNotFoundError:
        return FaceComparison(STATUS_ERROR, None, matcher.model, matcher.detector,
                              warning='One or both images could not be found.', mock=matcher.mock)
    except InvalidImage as error:
        return FaceComparison(STATUS_ERROR, None, matcher.model, matcher.detector,
                              warning=str(error), mock=matcher.mock)
    return matcher.compare(reference, candidate)
