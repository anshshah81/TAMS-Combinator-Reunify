# Contributing to Reunify

Team workflow: `main` is the stable branch. Work in `feature/<topic>` or `fix/<topic>` branches, commit descriptive messages, push and open a pull request. Have a teammate review before merging. Prefer at least one approval and CI green.

**Three-team-member setup:** repository owner invites both teammates via **Settings → Collaborators and teams → Add people**. Each invitee accepts. Public access means anyone can read; only collaborators with write permission can push.

**Codex:** connect the repository and start each task in a branch. Instruct it to commit and push after tests, then open a PR, not push unreviewed changes to `main`.

**Sensitive data:** never commit real missing-person/patient records, photographs, biometric templates, authentication tokens or API credentials. Use synthetic demos only. Report accidentally exposed secrets immediately, rotate them, and purge the data from history as appropriate.
