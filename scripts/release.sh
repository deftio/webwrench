#!/usr/bin/env bash
set -euo pipefail

# release.sh — full release: prerelease checks + version bump + tag + push + GH release
#
# Two modes:
#   From main:             ./scripts/release.sh 0.2.0
#   From release branch:   ./scripts/release.sh
#
# Runs all prerelease checks first. If anything fails, nothing ships.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_helpers.sh"

# ── 1. Determine mode + version ──

step "Checking branch"
BRANCH=$(git branch --show-current)
MODE=""
VERSION=""

if [[ "$BRANCH" =~ ^release/v([0-9]+\.[0-9]+\.[0-9]+)$ ]]; then
    MODE="branch"
    VERSION="${BASH_REMATCH[1]}"
    ok "On release branch: $BRANCH (version $VERSION)"
elif [[ "$BRANCH" == "main" ]]; then
    MODE="main"
    VERSION="${1:-}"
    if [[ -z "$VERSION" ]]; then
        fail "On main — pass version as argument: ./scripts/release.sh 0.2.0"
    fi
    if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        fail "Version must be semver (e.g. 0.2.0)"
    fi
    ok "On main, releasing v$VERSION directly"
else
    fail "Must be on main or a release/v* branch (currently on '$BRANCH')"
fi

# ── 2. Check tag doesn't already exist ──

if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    fail "Tag v$VERSION already exists"
fi

# ── 3. Version bump (if needed) ──

step "Verifying version consistency"

TOML_VERSION=$(uv run python -c "
import re, pathlib
text = pathlib.Path('pyproject.toml').read_text()
m = re.search(r'^version\s*=\s*\"([^\"]+)\"', text, re.M)
print(m.group(1) if m else 'unknown')
")

INIT_VERSION=$(uv run python -c "
import re, pathlib
text = pathlib.Path('webwrench/__init__.py').read_text()
m = re.search(r'^__version__\s*=\s*\"([^\"]+)\"', text, re.M)
print(m.group(1) if m else 'unknown')
")

if [[ "$MODE" == "main" ]]; then
    if [[ "$TOML_VERSION" != "$VERSION" || "$INIT_VERSION" != "$VERSION" ]]; then
        warn "Version mismatch — bumping to $VERSION"
        sed -i.bak "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml && rm -f pyproject.toml.bak
        sed -i.bak "s/^__version__ = \".*\"/__version__ = \"$VERSION\"/" webwrench/__init__.py && rm -f webwrench/__init__.py.bak
        git add pyproject.toml webwrench/__init__.py
        git commit -m "chore: bump version to $VERSION"
        ok "Bumped to $VERSION"
    else
        ok "Already at $VERSION"
    fi
else
    if [[ "$TOML_VERSION" != "$VERSION" ]]; then
        fail "pyproject.toml version ($TOML_VERSION) != branch version ($VERSION)"
    fi
    if [[ "$INIT_VERSION" != "$VERSION" ]]; then
        fail "__init__.py version ($INIT_VERSION) != branch version ($VERSION)"
    fi
    ok "pyproject.toml: $TOML_VERSION"
    ok "__init__.py:    $INIT_VERSION"
fi

# ── 4. Clean working tree ──

step "Checking working tree"
if [[ -n "$(git status --porcelain)" ]]; then
    fail "Working tree is not clean. Commit or stash changes first."
fi
ok "Clean"

# ── 5. Run prerelease checks (lint, security, tests, build, install) ──

step "Running prerelease checks"
echo ""
"$SCRIPT_DIR/prerelease.sh"

# ── 6. Merge (if on release branch) ──

if [[ "$MODE" == "branch" ]]; then
    step "Squash-merging into main"
    COMMIT_COUNT=$(git rev-list --count main.."$BRANCH")
    ok "Merging $COMMIT_COUNT commit(s) from $BRANCH"

    git checkout main
    git merge --squash "$BRANCH"
    git commit -m "release: v$VERSION"

    ok "Squash-merged to main"
fi

# ── 7. Tag ──

step "Tagging v$VERSION"
git tag "v$VERSION"
ok "Tag created: v$VERSION"

# ── 8. Push ──

step "Pushing main + tags"
git push origin main --tags
ok "Pushed"

# ── 9. Create GitHub Release ──

step "Creating GitHub Release"
if gh release create "v$VERSION" --title "webwrench v$VERSION" --generate-notes; then
    ok "GitHub Release created — publish pipeline will run automatically"
else
    warn "Could not create GitHub Release (create manually if needed)"
fi

# ── 10. Cleanup ──

if [[ "$MODE" == "branch" ]]; then
    step "Cleaning up release branch"
    git branch -d "$BRANCH" 2>/dev/null || true
    git push origin --delete "$BRANCH" 2>/dev/null || true
    ok "Branch $BRANCH cleaned up"
fi

rm -rf dist/ build/

# ── Done ──

echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  webwrench v$VERSION released!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo "CI runs on push. Publish to PyPI triggers on the v$VERSION tag."
echo "GitHub Release: https://github.com/deftio/webwrench/releases/tag/v$VERSION"
