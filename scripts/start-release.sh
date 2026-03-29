#!/usr/bin/env bash
set -euo pipefail

# start-release.sh — Phase 1 of 2: bump version + create release branch
# Usage: ./scripts/start-release.sh 0.2.0
#
# This creates a release/v0.2.0 branch with the version bumped in
# pyproject.toml and __init__.py. Develop on this branch, then run
# ./scripts/release.sh to finalize.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_helpers.sh"

VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
    echo "Usage: ./scripts/start-release.sh <version>"
    echo "Example: ./scripts/start-release.sh 0.2.0"
    exit 1
fi

if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    fail "Version must be in semver format (e.g. 0.2.0)"
fi

CURRENT=$(uv run python -c "
import re, pathlib
text = pathlib.Path('pyproject.toml').read_text()
m = re.search(r'^version\s*=\s*\"([^\"]+)\"', text, re.M)
print(m.group(1) if m else 'unknown')
")

step "Version"
ok "Current: $CURRENT"
ok "New:     $VERSION"

if [[ "$CURRENT" == "$VERSION" ]]; then
    fail "New version is the same as current ($CURRENT)"
fi

if [[ -n "$(git status --porcelain)" ]]; then
    fail "Working tree is not clean. Commit or stash changes first."
fi

BRANCH="release/v${VERSION}"
step "Creating branch: $BRANCH"
git checkout -b "$BRANCH"

sed -i.bak "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml && rm -f pyproject.toml.bak
sed -i.bak "s/^__version__ = \".*\"/__version__ = \"$VERSION\"/" webwrench/__init__.py && rm -f webwrench/__init__.py.bak

git add pyproject.toml webwrench/__init__.py
git commit -m "chore: bump version to $VERSION"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Branch '$BRANCH' ready${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "  1. Make any final changes on this branch"
echo "  2. ./scripts/prerelease.sh    — validate everything"
echo "  3. ./scripts/release.sh       — ship it"
