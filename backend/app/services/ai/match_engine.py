"""Transparent candidate-matching engine.

Compares a missing-person report against unidentified-patient records and produces
ranked candidates with explicit supporting, conflicting, and missing evidence. The
ranking score is a transparent heuristic tally of evidence; it is deliberately NOT
a calibrated probability that two records are the same person, and it never decides
identity. Missing information is recorded as missing, not treated as disagreement.

Candidate retrieval is constrained to the same incident. Optional facial distance
(from the face-matching service) can be supplied per pair; it is uncertain evidence
and is only ever a weak signal, never verification.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

ENGINE_VERSION = 'transparent-heuristic-v1'

# Thresholds are heuristic defaults for ranking only, not validated identity
# criteria. They must be calibrated on licensed, consented data before any real use.
AGE_SUPPORT_YEARS = 5
AGE_CONFLICT_YEARS = 15
HEIGHT_SUPPORT_CM = 7
HEIGHT_CONFLICT_CM = 20
FACE_SUPPORT_DISTANCE = 0.30
FACE_CONFLICT_DISTANCE = 1.00


@dataclass(frozen=True)
class Evidence:
    supporting: list[str] = field(default_factory=list)
    conflicting: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    score: int = 0
    engine_version: str = ENGINE_VERSION
    method: str = 'transparent-heuristic'

    def as_dict(self) -> dict:
        return asdict(self)


def _tokens(text) -> set[str]:
    if not text:
        return set()
    return {word for word in ''.join(c.lower() if c.isalnum() else ' ' for c in text).split() if len(word) > 2}


def evaluate_pair(report, patient, face_distance: float | None = None) -> Evidence:
    """Compare one report/patient pair and return explicit, transparent evidence."""
    supporting: list[str] = []
    conflicting: list[str] = []
    missing: list[str] = []

    def numeric(label, a, b, support, conflict, unit=''):
        if a is None or b is None:
            missing.append(f'{label} missing on one record')
            return
        diff = abs(a - b)
        if diff <= support:
            supporting.append(f'{label} close ({a}{unit} vs {b}{unit})')
        elif diff >= conflict:
            conflicting.append(f'{label} differs ({a}{unit} vs {b}{unit})')

    def categorical(label, a, b):
        if not a or not b:
            missing.append(f'{label} missing on one record')
            return
        if a.strip().lower() == b.strip().lower():
            supporting.append(f'{label} matches ({a})')
        else:
            conflicting.append(f'{label} differs ({a} vs {b})')

    numeric('age', getattr(report, 'approximate_age', None), getattr(patient, 'approximate_age', None),
            AGE_SUPPORT_YEARS, AGE_CONFLICT_YEARS)
    numeric('height', getattr(report, 'height_cm', None), getattr(patient, 'height_cm', None),
            HEIGHT_SUPPORT_CM, HEIGHT_CONFLICT_CM, unit='cm')
    categorical('hair color', getattr(report, 'hair_color', None), getattr(patient, 'hair_color', None))
    categorical('eye color', getattr(report, 'eye_color', None), getattr(patient, 'eye_color', None))

    # Free-text similarity: overlap is supporting; absence is missing. We never
    # treat a text mismatch as a conflict because wording varies.
    feature_overlap = _tokens(getattr(report, 'distinguishing_features', None)) & \
        _tokens(getattr(patient, 'distinguishing_features', None))
    if not getattr(report, 'distinguishing_features', None) or not getattr(patient, 'distinguishing_features', None):
        missing.append('distinguishing features missing on one record')
    elif feature_overlap:
        supporting.append(f'distinguishing features overlap ({", ".join(sorted(feature_overlap))})')

    clothing_overlap = _tokens(getattr(report, 'clothing_description', None)) & \
        _tokens(getattr(patient, 'observed_clothing', None))
    if not getattr(report, 'clothing_description', None) or not getattr(patient, 'observed_clothing', None):
        missing.append('clothing description missing on one record')
    elif clothing_overlap:
        supporting.append(f'clothing overlaps ({", ".join(sorted(clothing_overlap))}); clothing can change')

    # Patients are unidentified, so name/nickname usually cannot be compared.
    if not getattr(patient, 'internal_id', None) or getattr(patient, 'organization_id', None) is None:
        pass
    missing.append('name/nickname not comparable (patient is unidentified)')

    # Timeline: a plausible ordering is weak support; an implausible one conflicts.
    last_seen = getattr(report, 'last_seen_time', None)
    admitted = getattr(patient, 'admission_time', None)
    if last_seen is None or admitted is None:
        missing.append('timeline missing on one record')
    else:
        delta_days = (admitted - last_seen).total_seconds() / 86400
        if delta_days >= -0.01:
            supporting.append('admission is after the last-seen time')
        elif delta_days < -1:
            conflicting.append('admission precedes the last-seen time by over a day')

    if face_distance is None:
        missing.append('face comparison not run')
    elif face_distance <= FACE_SUPPORT_DISTANCE:
        supporting.append(f'low face distance ({face_distance:.2f}); uncertain evidence')
    elif face_distance >= FACE_CONFLICT_DISTANCE:
        conflicting.append(f'high face distance ({face_distance:.2f}); uncertain evidence')

    score = len(supporting) - len(conflicting)
    return Evidence(supporting=supporting, conflicting=conflicting, missing=missing, score=score)


def rank_candidates(report, patients, face_distances: dict | None = None) -> list[tuple[object, Evidence]]:
    """Return patients that have at least one supporting signal for this report,
    highest-ranked first. Returns an empty list when nothing is supported, so a
    "no confident match" outcome is represented honestly rather than forced."""
    face_distances = face_distances or {}
    scored: list[tuple[object, Evidence]] = []
    for patient in patients:
        evidence = evaluate_pair(report, patient, face_distances.get(getattr(patient, 'id', None)))
        if evidence.supporting:
            scored.append((patient, evidence))
    scored.sort(key=lambda pair: (pair[1].score, len(pair[1].supporting)), reverse=True)
    return scored
