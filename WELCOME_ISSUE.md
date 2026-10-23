<!-- Create a new issue with this content, then pin it (… menu > Pin issue). -->

**Title:** Welcome, Hacktoberfest contributors! Start here

---

Welcome to LiveEdit, an AI video editor built with Flask, Celery, React and Gemini. We're glad you're here.

## Your first 15 minutes

- [ ] Read [HOW_IT_WORKS.md](https://github.com/clencyc/LiveEdit/blob/master/HOW_IT_WORKS.md) (5 minutes: how the app fits together)
- [ ] Pick an issue labelled [`good first issue`](https://github.com/clencyc/LiveEdit/issues?q=is%3Aopen+label%3A%22good+first+issue%22)
- [ ] Comment "I'd like to work on this" and wait for a maintainer to assign you
- [ ] Fork the repo and create a branch (`fix/short-description`)
- [ ] Make your change and run the tests
- [ ] Open a PR that says `Closes #<issue number>`

## You don't need API keys

Most contributions (tests, docs, UI polish, small fixes) need **no** Gemini, Google Cloud, Logto or Paystack account. The backend tests mock all of that. Please do **not** point a dev build at the production backend.

```bash
# Backend tests
cd LiveEditBackend && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt pytest pytest-cov && pytest -v

# Frontend tests
cd LiveEditFronten && npm install && npm test
```

(The frontend folder really is spelled `LiveEditFronten`.)

## Earn badges

Every merged PR earns a badge, posted automatically in a comment on your PR:

| Badge | For |
| --- | --- |
| First PR Merged | Your first merged PR |
| Test Hero | Tests |
| Bug Squasher | Bug fixes |
| Docs Champion | Documentation |
| Pixel Perfect | UI, design, accessibility |
| Audio Alchemist | Audio effects |

See [CONTRIBUTORS.md](https://github.com/clencyc/LiveEdit/blob/master/CONTRIBUTORS.md) for the Hall of Fame, and your name goes in the README contributors table too.

## Ground rules

- One issue at a time, one PR per issue. Keep PRs small.
- Ask questions in the issue thread. There are no silly ones, and if an issue points at a file that doesn't exist, that's our mistake: tell us.
- No low-effort or bulk "typo" PRs and no unreviewed AI-generated changes. They don't count and they slow everyone down.
- Be kind and assume good intent.
- Found a security problem? **Don't open a public issue.** Report it privately via the [Security tab](https://github.com/clencyc/LiveEdit/security/advisories/new).

Happy hacking!
