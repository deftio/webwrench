#!/usr/bin/env bash
set -euo pipefail

# release.sh — validate, test, build, tag, push, publish
#
# Two modes:
#   From main:             ./scripts/release.sh 0.2.0
#   From release branch:   ./scripts/release.sh
#
# Either way it will:
#   1. Run linting (ruff) and security scan (bandit)
#   2. Run full test suite with 100% coverage gate
#   3. Build the wheel/sdist and check bundle size
#   4. If on release branch: squash-merge into main
#   5. Tag and push (CI + publish.yml handle PyPI)

# ── Helpers ──

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

step() { echo -e "\n${CYAN}▸ $1${NC}"; }
ok()   { echo -e "  ${GREEN}✓ $1${NC}"; }
fail() { echo -e "  ${RED}✗ $1${NC}"; exit 1; }
warn() { echo -e "  ${YELLOW}⚠ $1${NC}"; }

# ── 1. Determine mode ──

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

# ── 2. Version consistency ──

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
    # On main: bump version if it doesn't match
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
    # On release branch: versions must already match
    if [[ "$TOML_VERSION" != "$VERSION" ]]; then
        fail "pyproject.toml version ($TOML_VERSION) != branch version ($VERSION)"
    fi
    if [[ "$INIT_VERSION" != "$VERSION" ]]; then
        fail "__init__.py version ($INIT_VERSION) != branch version ($VERSION)"
    fi
    ok "pyproject.toml: $TOML_VERSION"
    ok "__init__.py:    $INIT_VERSION"
fi

# ── 3. Clean working tree ──

step "Checking working tree"
if [[ -n "$(git status --porcelain)" ]]; then
    fail "Working tree is not clean. Commit or stash changes first."
fi
ok "Clean"

# ── 4. Lint ──

step "Running ruff lint"
if uv run ruff check webwrench/; then
    ok "Lint passed"
else
    fail "Lint failed"
fi

# ── 5. Security scan ──

step "Running bandit security scan"
if uv run bandit -r webwrench/ -c pyproject.toml -q; then
    ok "Security scan passed"
else
    fail "Security scan failed"
fi

# ── 6. Tests ──

step "Running test suite (100% coverage gate)"
if uv run pytest --cov=webwrench --cov-report=term-missing --cov-fail-under=100 -q; then
    ok "All tests passed with 100% coverage"
else
    fail "Tests failed or coverage below 100%"
fi

# ── 7. Build ──

step "Building package"
rm -rf dist/ build/
if uv build; then
    ok "Build succeeded"
else
    fail "Build failed"
fi

# Check wheel size (warn if > 2MB)
WHEEL=$(ls dist/*.whl 2>/dev/null | head -1)
if [[ -n "$WHEEL" ]]; then
    SIZE=$(wc -c < "$WHEEL" | tr -d ' ')
    SIZE_KB=$((SIZE / 1024))
    if [[ $SIZE -gt 2097152 ]]; then
        warn "Wheel is ${SIZE_KB}KB (> 2MB) — consider auditing bundled assets"
    else
        ok "Wheel size: ${SIZE_KB}KB"
    fi
fi

# ── 8. Verify installable ──

step "Verifying package installs"
if uv pip install --quiet dist/*.whl 2>/dev/null; then
    INSTALLED=$(uv run python -c "import webwrench; print(webwrench.__version__)")
    uv pip uninstall webwrench > /dev/null 2>&1
    if [[ "$INSTALLED" == "$VERSION" ]]; then
        ok "Installed and verified version $INSTALLED"
    else
        fail "Installed version ($INSTALLED) != expected ($VERSION)"
    fi
else
    warn "Could not verify install (non-fatal)"
fi

# ── 9. Merge (if on release branch) ──

if [[ "$MODE" == "branch" ]]; then
    step "Squash-merging into main"
    COMMIT_COUNT=$(git rev-list --count main.."$BRANCH")
    ok "Merging $COMMIT_COUNT commit(s) from $BRANCH"

    git checkout main
    git merge --squash "$BRANCH"
    git commit -m "release: v$VERSION"

    ok "Squash-merged to main"
fi

# ── 10. Tag ──

step "Tagging v$VERSION"
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    fail "Tag v$VERSION already exists"
fi
git tag "v$VERSION"
ok "Tag created: v$VERSION"

# ── 11. Push ──

step "Pushing main + tags"
git push origin main --tags
ok "Pushed"

# ── 12. Cleanup ──

if [[ "$MODE" == "branch" ]]; then
    step "Cleaning up release branch"
    git branch -d "$BRANCH" 2>/dev/null || true
    git push origin --delete "$BRANCH" 2>/dev/null || true
    ok "Branch $BRANCH cleaned up"
fi

# Clean build artifacts
rm -rf dist/ build/

# ── Done ──

echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  webwrench v$VERSION released!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo "CI will run automatically on the push to main."
echo ""
echo "To publish to PyPI:"
echo "  1. Go to https://github.com/deftio/webwrench/releases/new"
echo "  2. Select tag v$VERSION"
echo "  3. Title: webwrench v$VERSION"
echo "  4. Auto-generate or write release notes"
echo "  5. Publish — this triggers the PyPI publish workflow"
echo ""
echo "Or use gh CLI:"
echo "  gh release create v$VERSION --title \"webwrench v$VERSION\" --generate-notes"
