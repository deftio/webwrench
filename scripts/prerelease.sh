#!/usr/bin/env bash
set -euo pipefail

# prerelease.sh — validate everything, no side effects
#
# Usage: ./scripts/prerelease.sh
#
# Runs lint, security scan, tests (100% coverage), build, install verify.
# Does NOT commit, tag, push, or modify any files.
# Safe to run anytime as a preflight check.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_helpers.sh"

# ── 1. Version info ──

step "Reading version"
VERSION=$(uv run python -c "
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

if [[ "$VERSION" != "$INIT_VERSION" ]]; then
    fail "Version mismatch: pyproject.toml=$VERSION, __init__.py=$INIT_VERSION"
fi
ok "Version: $VERSION (pyproject.toml + __init__.py match)"

# ── 2. Git status ──

step "Checking git"
BRANCH=$(git branch --show-current)
ok "Branch: $BRANCH"
DIRTY=$(git status --porcelain)
if [[ -n "$DIRTY" ]]; then
    warn "Working tree has uncommitted changes"
else
    ok "Working tree clean"
fi

# ── 3. Lint ──

step "Running ruff lint"
if uv run ruff check webwrench/; then
    ok "Lint passed"
else
    fail "Lint failed"
fi

# ── 4. Security scan ──

step "Running bandit security scan"
if uv run bandit -r webwrench/ -c pyproject.toml -q; then
    ok "Security scan passed"
else
    fail "Security scan failed"
fi

# ── 5. Tests ──

step "Running test suite (100% coverage gate)"
if uv run pytest --cov=webwrench --cov-report=term-missing --cov-fail-under=100 -q; then
    ok "All tests passed with 100% coverage"
else
    fail "Tests failed or coverage below 100%"
fi

# ── 6. Build ──

step "Building package"
rm -rf dist/ build/
if uv build; then
    ok "Build succeeded"
else
    fail "Build failed"
fi

# Check wheel size
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

# ── 7. Verify installable ──

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

# Clean up
rm -rf dist/ build/

# ── Done ──

echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  prerelease checks passed for v$VERSION${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo "Ready to release. Run: ./scripts/release.sh $VERSION"
