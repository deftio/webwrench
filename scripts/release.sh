#!/usr/bin/env bash
set -euo pipefail

# Release helper for webwrench
# Usage: ./scripts/release.sh 0.2.0

VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
    echo "Usage: ./scripts/release.sh <version>"
    echo "Example: ./scripts/release.sh 0.2.0"
    exit 1
fi

# Validate semver format
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in semver format (e.g. 0.2.0)"
    exit 1
fi

# Ensure we're on main branch
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" != "main" ]]; then
    echo "Error: Must be on main branch (currently on '$BRANCH')"
    exit 1
fi

# Ensure working tree is clean
if [[ -n "$(git status --porcelain)" ]]; then
    echo "Error: Working tree is not clean. Commit or stash changes first."
    exit 1
fi

echo "Releasing webwrench v$VERSION"

# Update version in pyproject.toml
sed -i.bak "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml && rm pyproject.toml.bak

# Update version in __init__.py
sed -i.bak "s/^__version__ = \".*\"/__version__ = \"$VERSION\"/" webwrench/__init__.py && rm webwrench/__init__.py.bak

# Run tests as sanity check
echo "Running tests..."
pytest --cov=webwrench --cov-report=term-missing -q

echo "Tests passed."

# Commit, tag, push
git add pyproject.toml webwrench/__init__.py
git commit -m "release: v$VERSION"
git tag "v$VERSION"
git push origin main --tags

echo ""
echo "Done! v$VERSION has been pushed."
echo ""
echo "Next steps:"
echo "  1. Go to https://github.com/deftio/webwrench/releases/new"
echo "  2. Select tag v$VERSION"
echo "  3. Set title: webwrench v$VERSION"
echo "  4. Add release notes"
echo "  5. Publish release (this triggers PyPI publish)"
