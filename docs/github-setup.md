# GitHub setup and publishing

The requested owner is `anshshah81`, repository `TAMS-Combinator-Reunify`, public,
with default branch `main`. Do not create this under a different account.

At implementation time the connected GitHub account was confirmed as `anshshah81`.
The target repository returned 404 (not found or inaccessible), GitHub CLI was not
installed, and the connector did not offer repository creation. No remote creation,
push, PR, or ruleset success should be inferred from the presence of this file.

## Publish once GitHub CLI is installed and connected

Authenticate using the browser/device flow; never paste tokens into chat or files:

```powershell
gh auth login --hostname github.com --web
gh auth status
gh api user --jq .login
gh repo view anshshah81/TAMS-Combinator-Reunify
```

Confirm the login is `anshshah81`. If the repository now exists, inspect its contents,
branches, and open PRs first. Fetch its history and integrate the local foundation on
a feature branch without replacing existing work. Do not force-push.

Only if the repository does not exist, publish the reviewed local baseline from
this starter folder (the branch is `feature/backend-foundation`):

```powershell
git status
git branch main
gh repo create anshshah81/TAMS-Combinator-Reunify --public --source=. --remote=origin
git push origin main
gh repo edit anshshah81/TAMS-Combinator-Reunify --default-branch main
git push -u origin feature/backend-foundation
```

The initial foundation is the baseline for a new repository; both branches point
to the same commit, so there is no meaningful PR between them. Subsequent changes
must branch from synchronized main and open reviewable feature PRs. If a baseline
already exists remotely, integrate via PR instead of this initial-publish recipe.

## Branch protection

After CI has run once, open repository Settings → Rules → Rulesets → New branch
ruleset. Name it `Protect main`, set enforcement to Active, and target the default
branch (`main`). Require a pull request before merging with one approval, dismiss
stale approvals after new commits, require conversation resolution, require status
checks and branches to be up to date, block force pushes, and restrict deletions.
Select the actual CI checks `backend (3.11)`, `backend (3.12)`, and `frontend` after
they appear. Keep bypass permissions empty unless the team explicitly agrees.
If rulesets are unavailable, use Settings → Branches → Add branch protection rule,
pattern `main`, with the same requirements. Never disable protections to push.

Invite the other two developers through Settings → Collaborators → Add people;
the owner needs their GitHub usernames and they must accept the invitations.
