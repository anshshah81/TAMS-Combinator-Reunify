# Synthetic data provenance and licensing

Reunify uses **synthetic and consented demonstration data only**. No real patient
records, photographs, facial embeddings, or personal contacts are stored or
committed. There are two sources of data in this repository.

## 1. Built-in demo seed

`backend/app/seed.py` and `backend/app/seed_accounts.py` insert a small, fixed set
of fictional incidents, reports, patient records, one placeholder candidate, and
demo sign-in identities. These are authored by hand for the demo, contain no real
people, and carry no external license obligations.

## 2. Evaluation harness data

`backend/app/eval/synthetic.py` generates fictional labeled report/patient pairs at
runtime from a seeded random generator. Nothing is persisted; it exists only to
measure the matching engine (see [evaluation](evaluation.md)).

## External datasets (reference, not yet integrated)

The project plan references these as intended sources for larger-scale synthetic
evaluation. They are **not bundled** in this repository; review each license before
downloading or redistributing any data or derived artifacts.

| Source | Purpose | License |
| --- | --- | --- |
| [Synthea](https://github.com/synthetichealth/synthea) | Synthetic patient/EHR records | Apache-2.0 (code); generated data free to use |
| [FEBRL](https://sourceforge.net/projects/febrl/) | Record-linkage test data generator | Open source (ANU); verify terms before redistribution |
| [Splink](https://github.com/moj-analytical-services/splink) | Probabilistic linkage baseline + sample data | MIT |

## Rules for any data added later

- Split training and test data by **person and incident** to prevent leakage.
- Never commit real photographs, biometric embeddings, medical records, private
  contacts, secrets, model weights, or database files.
- Keep generated public demo figures as **scenario counts only**, never real totals.
- Record the exact source, version, and license of any dataset added here.
