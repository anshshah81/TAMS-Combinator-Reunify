"""Generate a fictional, labeled matching dataset.

Each synthetic person yields exactly one missing-person report and one
unidentified-patient record with noisily perturbed attributes, plus optional
unmatched distractor patients. Ground truth is the person id shared by the
matching report and patient. Data is split by both person and incident so that
no person or incident appears in more than one split -- this prevents leakage
when a learned linkage model (e.g. Splink) is evaluated later.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

HAIR = ['black', 'brown', 'blonde', 'gray', 'red', 'auburn']
EYES = ['brown', 'blue', 'green', 'hazel']
FEATURES = ['scar on left forearm', 'tattoo on right shoulder', 'burn mark on hand',
            'birthmark on neck', 'missing fingertip', 'surgical scar on knee']
CLOTHING = ['blue jeans', 'red hoodie', 'gray jacket', 'green dress', 'black boots',
            'white shirt', 'yellow raincoat']


@dataclass
class Record:
    id: str
    person_id: str
    incident_id: str
    approximate_age: int | None = None
    height_cm: int | None = None
    hair_color: str | None = None
    eye_color: str | None = None
    distinguishing_features: str | None = None
    clothing_description: str | None = None  # report side
    observed_clothing: str | None = None     # patient side
    last_seen_time=None
    admission_time=None


@dataclass
class Dataset:
    reports: list[Record]
    patients: list[Record]

    def patients_in(self, incident_id: str) -> list[Record]:
        return [patient for patient in self.patients if patient.incident_id == incident_id]


def _maybe(rng: random.Random, value, probability: float):
    """Drop a value sometimes to model missing information (not disagreement)."""
    return value if rng.random() < probability else None


def _generate_person(rng: random.Random, person_id: str, incident_id: str) -> tuple[Record, Record]:
    age = rng.randint(18, 80)
    height = rng.randint(150, 195)
    hair = rng.choice(HAIR)
    eye = rng.choice(EYES)
    feature = rng.choice(FEATURES)
    clothing = rng.choice(CLOTHING)

    report = Record(
        id=f'R-{person_id}', person_id=person_id, incident_id=incident_id,
        approximate_age=age, height_cm=height, hair_color=hair, eye_color=eye,
        distinguishing_features=feature, clothing_description=clothing)

    # The same person observed independently at a hospital: noisy but related.
    patient = Record(
        id=f'P-{person_id}', person_id=person_id, incident_id=incident_id,
        approximate_age=_maybe(rng, age + rng.randint(-3, 3), 0.9),
        height_cm=_maybe(rng, height + rng.randint(-4, 4), 0.9),
        hair_color=_maybe(rng, hair if rng.random() < 0.85 else rng.choice(HAIR), 0.85),
        eye_color=_maybe(rng, eye if rng.random() < 0.8 else rng.choice(EYES), 0.6),
        distinguishing_features=_maybe(rng, feature if rng.random() < 0.7 else rng.choice(FEATURES), 0.7),
        observed_clothing=_maybe(rng, clothing if rng.random() < 0.5 else rng.choice(CLOTHING), 0.7))
    return report, patient


def _distractor(rng: random.Random, index: int, incident_id: str) -> Record:
    return Record(
        id=f'D-{incident_id}-{index}', person_id=f'none-{incident_id}-{index}', incident_id=incident_id,
        approximate_age=_maybe(rng, rng.randint(18, 80), 0.9),
        height_cm=_maybe(rng, rng.randint(150, 195), 0.9),
        hair_color=_maybe(rng, rng.choice(HAIR), 0.85),
        eye_color=_maybe(rng, rng.choice(EYES), 0.6),
        distinguishing_features=_maybe(rng, rng.choice(FEATURES), 0.6),
        observed_clothing=_maybe(rng, rng.choice(CLOTHING), 0.7))


def generate_split(seed: int, persons: int, incidents: int, distractors_per_incident: int) -> Dataset:
    """Build one disjoint split: persons and incidents here appear nowhere else
    when called with different seeds for train vs test."""
    rng = random.Random(seed)
    reports: list[Record] = []
    patients: list[Record] = []
    for person in range(persons):
        incident_id = f'INC-{seed}-{person % incidents}'
        report, patient = _generate_person(rng, f'{seed}-{person}', incident_id)
        reports.append(report)
        patients.append(patient)
    for incident in range(incidents):
        incident_id = f'INC-{seed}-{incident}'
        for index in range(distractors_per_incident):
            patients.append(_distractor(rng, index, incident_id))
    return Dataset(reports=reports, patients=patients)
