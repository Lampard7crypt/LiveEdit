#!/usr/bin/env bash
# Creates/updates the labels used by the hackathon. Requires the GitHub CLI (gh) and `gh auth login`.
# Usage: bash .github/scripts/create-labels.sh clencyc/LiveEdit
set -euo pipefail
REPO="${1:?Usage: create-labels.sh owner/repo}"

mk() { gh label create "$1" --color "$2" --description "$3" --repo "$REPO" --force; }

# Badge labels (maintainers add one before merging; the workflow reads them)
mk "badge:test"   "10b981" "Awards the Test Hero badge on merge"
mk "badge:bug"    "ef4444" "Awards the Bug Squasher badge on merge"
mk "badge:docs"   "3b82f6" "Awards the Docs Champion badge on merge"
mk "badge:design" "ec4899" "Awards the Pixel Perfect badge on merge"
mk "badge:audio"  "f59e0b" "Awards the Audio Alchemist badge on merge"

# Hacktoberfest / triage helpers
mk "hacktoberfest-accepted" "8b5cf6" "Counts toward Hacktoberfest even if not merged"
mk "good first issue"       "7057ff" "Good for newcomers"
mk "needs-info"             "fbca04" "Waiting on details from the contributor"
mk "claimed"                "0e8a16" "Someone is working on this"
echo "Done."
