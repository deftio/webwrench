#!/usr/bin/env bash
set -euo pipefail

# start-release.sh — Phase 1 of 2: bump version + create release branch
# Usage: ./scripts/start-release.sh 0.2.0
#
# This creates a release/v0.2.0 branch with the version bumped in
# pyproject.toml and __init__.py. Develop on this branch, then run
# ./scripts/release.sh to finalize.

VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
    echo "Usage: ./scripts/start-release.sh <version>"
    echo "Example: ./scripts/start-release.sh 0.2.0"
    exit 1
fi

# Validate semver format
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in semver format (e.g. 0.2.0)"
    exit 1
fi

# Read current version from pyproject.toml
CURRENT=$(uv run python -c "
import re, pathlib
text = pathlib.Path('pyproject.toml').read_text()
m = re.search(r'^version\s*=\s*\"([^\"]+)\"', text, re.M)
print(m.group(1) if m else 'unknown')
")

echo "Current version: $CURRENT"
echo "New version:     $VERSION"

if [[ "$CURRENT" == "$VERSION" ]]; then
    echo "Error: New version is the same as current ($CURRENT)"
    exit 1
fi

# Ensure working tree is clean
if [[ -n "$(git status --porcelain)" ]]; then
    echo "Error: Working tree is not clean. Commit or stash changes first."
    exit 1
fi

# Create release branch
BRANCH="release/v${VERSION}"
echo ""
echo "Creating branch: $BRANCH"
git checkout -b "$BRANCH"

# Bump version in pyproject.toml
sed -i.bak "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml && rm -f pyproject.toml.bak

# Bump version in __init__.py
sed -i.bak "s/^__version__ = \".*\"/__version__ = \"$VERSION\"/" webwrench/__init__.py && rm -f webwrench/__init__.py.bak

# Commit the version bump
git add pyproject.toml webwrench/__init__.py
git commit -m "chore: bump version to $VERSION"

echo ""
echo "=== Phase 1 complete ==="
echo ""
echo "Branch '$BRANCH' created with version $VERSION."
echo ""
echo "Next steps:"
echo "  1. Make any final changes on this branch"
echo "  2. Run: ./scripts/release.sh"
echo "     This will validate, test, build, and merge to main."
