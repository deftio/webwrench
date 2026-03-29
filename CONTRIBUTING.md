# Contributing to webwrench

All contributions come through pull requests — no direct commits to `main`.

## Setup

Requires Python 3.10+.

```bash
git clone https://github.com/deftio/webwrench.git
cd webwrench
pip install -e ".[dev]"
```

## Development Workflow

1. Create a feature branch from `main`
2. Make changes with corresponding tests
3. Verify locally: lint, test, coverage
4. Push and open a PR against `main`

```bash
git checkout main
git pull origin main
git checkout -b feature/my-feature

# ... make changes ...

ruff check webwrench/
pytest --cov=webwrench --cov-report=term-missing
git add <files>
git commit -m "add: description of the change"
git push -u origin feature/my-feature
```

Then open a PR on GitHub.

## Branch Rules

- **Never commit directly to `main`.** Always use a feature branch.
- Branch naming: `feature/<name>`, `fix/<name>`, or `docs/<name>`.
- Keep branches focused — one feature or fix per branch.
- Squash commits before merging. The PR title becomes the commit message on `main`.

## Pull Request Requirements

- Clear description of what changed and why
- New or updated tests for any code changes
- All CI checks passing (lint, tests, coverage)
- 100% test coverage maintained

## Directory Layout

| Directory | Purpose | Shipped to PyPI? |
|-----------|---------|------------------|
| `webwrench/` | Package source | Yes |
| `webwrench/_assets/` | Bundled bitwrench.js + Chart.js | Yes |
| `tests/` | pytest test suite | No |
| `examples/` | Runnable example scripts | No |
| `docs/` | Documentation site (GitHub Pages) | No |
| `dev/` | Design documents and specs | No |
| `scripts/` | Release automation | No |

## Testing

```bash
# Run all tests with coverage
pytest --cov=webwrench --cov-report=term-missing

# Run a specific test file
pytest tests/test_display.py

# Run with verbose output
pytest -v
```

Coverage must stay at 100%. The CI pipeline enforces this.

## Linting

```bash
ruff check webwrench/
```

## Code Rules

- Zero runtime dependencies — do not add any entries to `dependencies` in `pyproject.toml`
- bitwrench IS the frontend — no custom JavaScript or CSS in webwrench
- TACO format: `{"t": tag, "a": attributes, "c": content, "o": options}`
- Use `contextvars` for per-session dispatch, never global state
- Python 3.10+ — use `X | Y` union syntax, not `Union[X, Y]`

## Version Guarantee

`pyproject.toml` is the single source of truth for the version number. The version must also be set in `webwrench/__init__.py` (`__version__`). The release script (`scripts/release.sh`) updates both files automatically.

Do not bump the version number manually — use the release script.

## Release Process (Maintainers Only)

Releases follow this flow:

```
feature branch → PR → squash merge to main → release script → GitHub Release → PyPI
```

### Steps

1. Ensure `main` is up to date and CI is green
2. Run the release script:

```bash
./scripts/release.sh 0.2.0
```

This will:
- Validate semver format
- Update version in `pyproject.toml` and `webwrench/__init__.py`
- Run the full test suite as a sanity check
- Commit: `release: v0.2.0`
- Tag: `v0.2.0`
- Push commit and tag to `main`

3. Create a GitHub Release from the tag at https://github.com/deftio/webwrench/releases/new
4. CI automatically publishes to PyPI when the GitHub Release is created

**Do NOT run `python -m build && twine upload` manually.** CI handles PyPI publishing automatically when a GitHub Release is published.

## Commit Message Style

Use a lowercase prefix describing the type of change:

| Prefix | Use |
|--------|-----|
| `add:` | New feature |
| `fix:` | Bug fix |
| `update:` | Enhancement to existing feature |
| `refactor:` | Code restructure with no behavior change |
| `docs:` | Documentation only |
| `test:` | Test additions or fixes |
| `release:` | Version bump (release script only) |

Examples:
```
add: sidebar layout component
fix: chart update not propagating to browser
docs: add theming guide
test: cover accordion open state
```

## CI Pipeline

CI runs automatically on pushes to `main` and on all PRs:

- **Lint**: `ruff check webwrench/`
- **Security**: `bandit -r webwrench/ -c pyproject.toml`
- **Tests**: `pytest --cov=webwrench` across Python 3.10, 3.11, 3.12, 3.13
- **Coverage**: Must remain at 100%

## Questions?

Open an issue at https://github.com/deftio/webwrench/issues.
