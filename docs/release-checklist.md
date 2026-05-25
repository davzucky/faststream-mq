# Release checklist

Use this checklist before publishing `faststream-mq`.

## 1. Confirm release scope

- Review merged PRs since the previous release.
- Update `CHANGELOG.md`.
- Confirm documentation reflects the current setup and migration path.
- Confirm the version in `pyproject.toml` is correct.

## 2. Validate locally

Install the IBM MQ Client SDK if needed:

```bash
MQ_FILE_PATH="$HOME/.local/opt/mqm" ./scripts/install-mq-client.sh
export MQ_FILE_PATH="$HOME/.local/opt/mqm"
export LD_LIBRARY_PATH="$MQ_FILE_PATH/lib64:$LD_LIBRARY_PATH"
```

Run fast checks:

```bash
uv sync --all-extras --group dev
uv run ruff format --check
uv run ruff check
./scripts/ty-check.sh
uv run pytest -m 'not connected and not slow'
uv run --only-group docs mkdocs build --strict
uv build
```

Run connected checks:

```bash
docker compose up -d ibmmq ibmmq_ha2
uv run python scripts/wait-mq-ready.py "127.0.0.1(1414)" "127.0.0.1(1415)"
uv run pytest -m connected
```

## 3. Verify CI

On `main`, confirm these required checks are green:

- `Build package`
- `Checks (3.10)`
- `Checks (3.11)`
- `Checks (3.12)`
- `Checks (3.13)`
- `Checks (3.14)`
- `connected`
- `Build docs`

## 4. Verify PyPI Trusted Publishing

Before the first release, configure the PyPI project trusted publisher for:

- PyPI project: `faststream-mq`
- Owner/repository: `davzucky/faststream-mq`
- Workflow: `.github/workflows/release.yml`
- Environment: `pypi`

The release workflow uses GitHub OIDC and runs:

```bash
uv publish --trusted-publishing automatic
```

No PyPI API token should be required.

## 5. Create the release tag

From an up-to-date `main`:

```bash
git switch main
git pull --ff-only
git tag v0.1.0
git push origin v0.1.0
```

Tags matching `v*` trigger the release workflow.

## 6. What the release workflow does

The release workflow:

1. installs the IBM MQ Client SDK
2. builds the source distribution and wheel with `uv build`
3. publishes the package to PyPI using Trusted Publishing
4. creates a GitHub Release for the tag and attaches the files from `dist/`

## 7. Post-release verification

After the workflow succeeds:

```bash
python -m pip install faststream-mq
python -c "from faststream_mq import MQBroker; print(MQBroker)"
```

Then confirm:

- the PyPI page is available
- the GitHub Release exists and has package artifacts attached
- Read the Docs has built the latest docs
- `CHANGELOG.md` links resolve for the released tag
