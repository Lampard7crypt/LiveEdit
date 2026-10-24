# Hackathon kit: setup guide (about 20 minutes)

You can delete this file after setup. Do the steps in order.

## What's in the kit

| File | Purpose |
| --- | --- |
| `.github/badges/*.svg` | 7 contributor badges |
| `.github/scripts/generate_badges.py` | Regenerates the badges (change names, colours, icons) |
| `.github/workflows/contributor-badges.yml` | Posts badges in a comment when a PR is merged |
| `.github/scripts/create-labels.sh` | Creates the labels the workflow uses |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR checklist for contributors |
| `.github/ISSUE_TEMPLATE/` | Template for writing good first issues, and a private security link |
| `.all-contributorsrc` | Config for the All Contributors bot |
| `CONTRIBUTORS.md` | Badge guide and Hall of Fame |
| `WELCOME_ISSUE.md` | Text for a pinned "Start here" issue |

## 1. Add the files to `master`

Copy everything into the repo root and commit **directly to `master`**. The workflow only runs if it exists on the default branch.

```bash
git add .github CONTRIBUTORS.md .all-contributorsrc
git commit -m "Add Hacktoberfest contributor badges and templates"
git push origin master
```

Also commit `HOW_IT_WORKS.md` and the new `README.md` if you haven't yet.

## 2. Make CI run on your PRs (important)

`.github/workflows/tests.yml` currently triggers only for `main` and `develop`, but your default branch is `master`, so contributors get no test results. Change both triggers:

```yaml
on:
  push:
    branches: [master, main, develop]
  pull_request:
    branches: [master, main, develop]
```

## 3. Create the labels

```bash
gh auth login
bash .github/scripts/create-labels.sh clencyc/LiveEdit
```

(Or create `badge:test`, `badge:bug`, `badge:docs`, `badge:design`, `badge:audio` by hand under Issues > Labels. The names must match exactly.)

## 4. Repository settings

- Add the topic **`hacktoberfest`** (repo main page > gear next to About > Topics).
- Settings > Actions > General: make sure Actions are enabled.
- Keep "Require approval for first-time contributors" on, so CI from strangers needs your OK.
- Check hacktoberfest.com for this year's current rules.

## 5. All Contributors (README wall of fame)

1. Install the app: https://github.com/apps/allcontributors and give it access to the `LiveEdit` repo.
2. Add this block to `README.md` where you want the table:

```markdown
## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->
```

3. To add someone, comment on any issue or PR:

```
@all-contributors please add @username for code, test, doc
```

Useful types: `code`, `test`, `doc`, `design`, `bug`, `ideas`, `audio`, `review`, `question`.

## 6. Test the badge bot before the event

The workflow skips PRs by the repo owner. To test with your own account:

1. In `contributor-badges.yml`, temporarily delete the `if (pr.author_association === 'OWNER') { ... }` block and push to `master`.
2. Open a throwaway PR (for example a one-line change to `CONTRIBUTORS.md`), add the label `badge:docs`, and merge it.
3. Check the PR for the badge comment.
4. Restore the block and revert the throwaway change.

If nothing appears, open the Actions tab and read the "Contributor badges" run.

## 7. Pin the welcome issue

Create a new issue from `WELCOME_ISSUE.md`, then use the `...` menu > Pin issue.

## Your routine while the event runs

1. Review the PR. Ask for changes if needed.
2. Add **one** badge label (`badge:test`, `badge:bug`, `badge:docs`, `badge:design` or `badge:audio`). Everyone also gets First PR and Hacktoberfest badges automatically.
3. Merge. The bot posts the badges.
4. Add a row to the Hall of Fame in `CONTRIBUTORS.md`.
5. Comment `@all-contributors please add @username for ...`.

## Notes

- **Security:** the workflow uses `pull_request_target`. It is safe because it never checks out or runs PR code. Never add a step that does.
- **Spam:** badges are awarded on merge only, so low-effort PRs earn nothing.
- **Changing badges:** edit `BADGES` in `generate_badges.py`, run `python .github/scripts/generate_badges.py`, commit the SVGs. For a new badge also add a label entry in the workflow's `LABEL_BADGES`.
