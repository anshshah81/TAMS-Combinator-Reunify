# End-to-end fictional scenario

A complete synthetic walkthrough spanning intake, AI suggestions, a no-match case,
human investigation, and resolution. All names, records, and images are fictional.
Enable the development-only demo portal first (see the README): set `APP_ENV`,
`DEMO_AUTH_ENABLED`, run migrations, and seed the demo accounts.

## Cast (seeded synthetic data)

- Incident `INC-DEMO-001` — "Hill Country Flood — Training Exercise".
- Report `M-DEMO-101` — "Jordan Reed (synthetic)", filed by the family reporter.
- Report `M-DEMO-102` — "Taylor Quinn (synthetic)".
- Patients `H-DEMO-201` (Hospital A) and `H-DEMO-202` (Hospital B).

## 1. Family intake

Sign in as **Demo family reporter** → **Family report**. File a missing-person
report (name, approximate age, height, hair/eye color, distinguishing features,
last-seen place/time, clothing, optional synthetic photo, consent). You receive a
tracking ID. On **Report tracking**, the status reads a coarse, detail-free value
and never exposes hospital records or candidates.

## 2. Hospital intake

Sign in as **Demo hospital A staff** → **Hospital intake**. Record an unidentified
patient for your organization. Unknown attributes are left blank ("not recorded",
not "absent"). Hospital B staff cannot see Hospital A's records.

## 3. AI suggestions (reviewer)

Sign in as **Demo emergency reviewer** → **Match review**. Choose the incident and
click **Generate candidates**. The engine surfaces ranked suggestions with a
transparent evidence tally. `M-DEMO-101 ↔ H-DEMO-201` ranks highly (close age and
height, matching dark hair, overlapping "scar/forearm" and "blue jeans"), while
weakly-supported pairs rank lower and unsupported pairs do not appear at all.

## 4. No-match case

Some reports produce **no candidate** when nothing is supported — for example a
report whose only incident patients conflict on age and hair. The UI shows an
honest "no supported matches" state rather than forcing a match.

## 5. Investigation

Open a candidate → side-by-side investigation. Compare attributes and authorized
synthetic photos. Optionally run the (mock by default) **face comparison** and
**clothing detection**; both are labeled uncertain evidence, and a non-detection is
never treated as absence. Record **Investigate further** or **Request more info**;
the family's report status moves to a generic "under review".

## 6. Resolution

Only a human can **Record verification**, and only with notes plus a written
attestation of the independent evidence used (e.g. ID documents, next-of-kin). The
candidate becomes `verified`, the decision and an `identity.verified` entry are
written to the immutable audit log, and the family's report status becomes a coarse
"resolved". The system never contacts the family automatically.

## 7. Oversight

Sign in as **Demo administrator** → **Administration** to manage incident status,
review demo accounts, and read the append-only audit trail (actor, action, record
id only — never medical or biometric detail).

## What this demonstrates

AI narrows the search and explains its reasoning; humans decide. No automated
identity confirmation, no automated family contact, and strict role/organization
boundaries throughout.
