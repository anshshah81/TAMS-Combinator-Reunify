"""Clothing detection service.

Given a photo and a list of garment phrases, returns which phrases have possible
visual support, with bounding boxes and scores. This is *uncertain evidence* for a
human reviewer. Important semantics:

- 'detected' vs 'none_detected' vs 'error' are distinct. Non-detection is NOT
  evidence that a garment is absent (it may be obscured, cropped, or the person
  may have changed clothes).
- A detected garment category does not confirm its color.
- When multiple people appear in one image, clothing must be associated with the
  target person before it counts as evidence. The result flags this requirement.

Adapters:
- MockClothingDetector: default, deterministic, clearly labeled; no real detection.
- GroundingDinoDetector: opt-in real inference; requires optional AI dependencies
  and license review. Never silently substituted by the mock.

Bounding boxes are normalized floats [x0, y0, x1, y1] in the range [0, 1], relative
to the image's top-left origin.
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Protocol

from ..image_storage import InvalidImage, sanitize_image

STATUS_DETECTED = 'detected'
STATUS_NONE_DETECTED = 'none_detected'
STATUS_ERROR = 'error'

MAX_QUERIES = 20
PERSON_ASSOCIATION_NOTE = (
    'If more than one person appears in the image, associate clothing with the '
    'target person before treating it as evidence.')


class ClothingDetectionUnavailable(RuntimeError):
    """Raised when a requested real adapter cannot be loaded; never fall back to
    the mock silently."""


@dataclass(frozen=True)
class Detection:
    box: list[float]
    score: float


@dataclass(frozen=True)
class QueryResult:
    query: str
    supported: bool
    detections: list[Detection] = field(default_factory=list)
    note: str | None = None


@dataclass(frozen=True)
class ClothingDetection:
    status: str
    model: str
    detector: str
    queries: list[QueryResult]
    warning: str | None = None
    mock: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


class ClothingDetector(Protocol):
    model: str
    detector: str
    mock: bool

    def detect(self, image: bytes, descriptions: list[str]) -> list[QueryResult]: ...


def _clean_descriptions(descriptions: list[str]) -> list[str]:
    cleaned: list[str] = []
    for item in descriptions:
        text = (item or '').strip()
        if text and text.lower() not in {c.lower() for c in cleaned}:
            cleaned.append(text[:100])
    return cleaned[:MAX_QUERIES]


def _load_valid_image(path: str | Path) -> bytes:
    data = Path(path).read_bytes()
    if not data:
        raise InvalidImage('Image file is empty.')
    sanitize_image(data)
    return data


class MockClothingDetector:
    """Deterministic, clearly labeled stand-in. Decides per-query "support" from a
    hash so output is stable; it performs no real detection and is not evidence."""

    model = 'GroundingDINO (mock)'
    detector = 'mock'
    mock = True

    def detect(self, image: bytes, descriptions: list[str]) -> list[QueryResult]:
        results: list[QueryResult] = []
        for query in descriptions:
            digest = hashlib.sha256(image + b'|' + query.lower().encode()).digest()
            supported = digest[0] % 3 != 0  # ~2/3 supported, deterministic
            if supported:
                # Derive a stable pseudo-box and score from the hash.
                x0 = digest[1] / 255 * 0.5
                y0 = digest[2] / 255 * 0.5
                box = [round(x0, 3), round(y0, 3), round(min(x0 + 0.4, 1.0), 3), round(min(y0 + 0.5, 1.0), 3)]
                score = round(0.3 + (digest[3] / 255) * 0.6, 3)
                results.append(QueryResult(
                    query=query, supported=True, detections=[Detection(box=box, score=score)],
                    note='Mock detection. A detected garment category does not confirm its color.'))
            else:
                results.append(QueryResult(
                    query=query, supported=False, detections=[],
                    note='No visual support in this mock. This is not evidence the garment is absent.'))
        return results


class GroundingDinoDetector:
    """Opt-in real adapter. Not exercised in ordinary CI (heavy deps + weights)."""

    model = 'GroundingDINO'
    detector = 'groundingdino'
    mock = False

    def __init__(self) -> None:
        try:
            import groundingdino  # type: ignore  # noqa: F401
        except Exception as error:  # pragma: no cover - requires optional deps
            raise ClothingDetectionUnavailable(
                'Real Grounding DINO inference requires the optional AI dependencies. '
                'Install backend/requirements-ai.txt and review model/weight licenses first.'
            ) from error

    def detect(self, image: bytes, descriptions: list[str]) -> list[QueryResult]:  # pragma: no cover
        raise ClothingDetectionUnavailable(
            'Grounding DINO inference wiring is not enabled in this build. '
            'Provide a configured model and weights before running real detection.')


def get_detector(mode: str = 'mock') -> ClothingDetector:
    if mode == 'mock':
        return MockClothingDetector()
    if mode == 'grounding_dino':
        return GroundingDinoDetector()
    raise ValueError(f'Unknown clothing detection mode: {mode!r}')


def detect_clothing(image_path, clothing_descriptions, detector: ClothingDetector | None = None) -> ClothingDetection:
    """Detect garment phrases in an image and return structured, uncertain evidence."""
    detector = detector or MockClothingDetector()
    descriptions = _clean_descriptions(list(clothing_descriptions or []))
    if not descriptions:
        return ClothingDetection(STATUS_ERROR, detector.model, detector.detector, [],
                                 warning='Provide at least one clothing description.', mock=detector.mock)
    try:
        image = _load_valid_image(image_path)
    except FileNotFoundError:
        return ClothingDetection(STATUS_ERROR, detector.model, detector.detector, [],
                                 warning='The image could not be found.', mock=detector.mock)
    except InvalidImage as error:
        return ClothingDetection(STATUS_ERROR, detector.model, detector.detector, [],
                                 warning=str(error), mock=detector.mock)
    queries = detector.detect(image, descriptions)
    status = STATUS_DETECTED if any(q.supported for q in queries) else STATUS_NONE_DETECTED
    return ClothingDetection(status, detector.model, detector.detector, queries,
                             warning=PERSON_ASSOCIATION_NOTE, mock=detector.mock)
