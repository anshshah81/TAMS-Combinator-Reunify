# GitHub collaboration setup

Repository: https://github.com/anshshah81/TAMS-Combinator-Reunify

The public repository now contains the Phase 1 foundation on `main`. Initial commit:
`dd34c2a934ae7ab9f167e1f32715d75ff40e5e84`. The same baseline is retained on
`feature/backend-foundation`. Both branches were published using the owner's
GitHub account after browser authorization through Git Credential Manager.

## Local authentication and commit identity

Git Credential Manager stores authentication outside the repository. To sign in on
a new workstation, use the browser flow and verify the account:

```powershell
git credential-manager github login --username anshshah81 --browser
git credential-manager github list
```

Each teammate must use their own GitHub account and commit identity. Never share
passwords or tokens, paste credentials into chat, or commit them to the repository.
The initial commit uses `anshshah81` and the account's GitHub no-reply email.

## Feature workflow

```powershell
git switch main
git pull --ff-only origin main
git switch -c feature/frontend-example
# Implement and run the checks in README.md.
git add <specific-files>
git diff --cached --check
git commit -m "feat: describe the implemented change"
git push -u origin feature/frontend-example
```

Open a pull request targeting `main`, include actual test results, and ask a teammate
to review. The initial baseline has identical main/feature contents, so there is no
meaningful PR between those two baseline branches. Subsequent changes use PRs.
Do not force-push main or automatically merge major features.

## Branch protection and collaborators

Protect `main` with one approving review, dismissal of stale approvals, conversation
resolution, required checks `backend (3.11)`, `backend (3.12)`, and `frontend`, and
up-to-date branches before merge. Block force pushes and deletion. If configuring
manually, use Settings → Branches → Add branch protection rule, pattern `main`,
with these settings. Verify the actual settings on GitHub; this document alone is
not evidence that protection is active.

Invite the other two developers through Settings → Collaborators → Add people.
Use their GitHub usernames; they must accept the invitations before contributing.
