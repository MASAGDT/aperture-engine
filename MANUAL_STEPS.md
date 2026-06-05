# Manual Steps

Codex can prepare the repository and workflows, but the package owner must finish the
Trusted Publishing setup in PyPI and GitHub.

## 1. Accounts

- Create or log into a PyPI account: <https://pypi.org/account/login/>

## 2. PyPI Trusted Publishers

Register a pending publisher from the PyPI publishing settings page:

- PyPI: <https://pypi.org/manage/account/publishing/>

Use these values:

- Owner: `MASAGDT`
- Repository name: `aperture-engine`
- Workflow filename: `release.yml`
- Environment name for PyPI: `pypi`

## 3. GitHub Environments

Create the matching environment in the GitHub repository settings:

- `pypi`

Repository environments page:
<https://github.com/MASAGDT/aperture-engine/settings/environments>

## 4. Release Ritual

For the first release, after the GitHub repository and PyPI Trusted Publisher are ready,
push the version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

For later releases, bump the version in both `pyproject.toml` and
`src/aperture_engine/__init__.py`, update `CHANGELOG.md`, commit the changes, then push a
matching version tag. The tag-triggered workflow builds, checks, and publishes the
package without storing any PyPI API token.
