# Manual Steps

Codex can prepare the repository and workflows, but the package owner must finish the
Trusted Publishing setup in PyPI and GitHub.

## 1. Accounts

- Create or log into a PyPI account: <https://pypi.org/account/login/>
- Create or log into a TestPyPI account for the dry run: <https://test.pypi.org/account/login/>

## 2. PyPI Trusted Publishers

Register pending publishers from the publishing settings pages:

- PyPI: <https://pypi.org/manage/account/publishing/>
- TestPyPI: <https://test.pypi.org/manage/account/publishing/>

Use these values:

- Owner: `MASAGDT`
- Repository name: `aperture-engine`
- Workflow filename: `release.yml`
- Environment name for PyPI: `pypi`
- Environment name for TestPyPI: `testpypi`

## 3. GitHub Environments

Create matching environments in the GitHub repository settings:

- `pypi`
- `testpypi`

Repository environments page:
<https://github.com/MASAGDT/aperture-engine/settings/environments>

## 4. Optional TestPyPI Dry Run

After the `testpypi` publisher and environment exist, run the release workflow manually
from GitHub Actions, or with:

```bash
gh workflow run release.yml --ref main
```

## 5. Release Ritual

For the first release, after the GitHub repository and PyPI Trusted Publisher are ready:

```bash
git tag v0.1.0
git push origin v0.1.0
```

For later releases, bump the version in both `pyproject.toml` and
`src/aperture_engine/__init__.py`, update `CHANGELOG.md`, commit the changes, then push a
matching version tag. The tag-triggered workflow builds, checks, and publishes the
package without storing any PyPI API token.
