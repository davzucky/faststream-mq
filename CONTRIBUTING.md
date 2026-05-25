# Contributing

Thanks for contributing to `faststream-mq`.

This package is a standalone extraction of IBM MQ support for FastStream. It intentionally tracks FastStream internals closely, so changes should keep compatibility, tests, and documentation together.

## Development setup

Install the IBM MQ Client SDK before syncing Python dependencies. The `ibmmq` package may need MQ C headers such as `cmqc.h` during installation.

```bash
MQ_FILE_PATH="$HOME/.local/opt/mqm" ./scripts/install-mq-client.sh
export MQ_FILE_PATH="$HOME/.local/opt/mqm"
export LD_LIBRARY_PATH="$MQ_FILE_PATH/lib64:$LD_LIBRARY_PATH"

uv sync --all-extras --group dev
uv run prek install
```

See the [IBM MQ Client SDK docs](https://faststream-mq.readthedocs.io/en/latest/mq-client-sdk/) for details.

## Local checks

Run the fast checks before opening a PR:

```bash
uv run ruff format
uv run ruff check
./scripts/ty-check.sh
uv run pytest -m 'not connected and not slow'
uv run --only-group docs mkdocs build --strict
```

## Connected IBM MQ tests

Connected tests run against real IBM MQ containers and are required in CI.

```bash
docker compose up -d ibmmq ibmmq_ha2
uv run python scripts/wait-mq-ready.py "127.0.0.1(1414)" "127.0.0.1(1415)"
uv run pytest -m connected
```

See the [connected testing docs](https://faststream-mq.readthedocs.io/en/latest/connected-testing/) for troubleshooting.

## Pull request expectations

- Work from a branch and open a PR; `main` is protected.
- Keep behavior changes covered by tests.
- Add connected regression coverage when behavior depends on real MQ semantics.
- Update documentation when user-facing behavior, setup, or migration steps change.
- Keep the canonical import path as `faststream_mq`; do not add a `faststream.mq` compatibility shim.
- Keep package management on `uv` and keep `uv.lock` in sync when dependencies change.

## Style and tooling

- Package manager/build backend: `uv` / `uv_build`
- Formatting/linting: `ruff`
- Type checking: `ty`
- Pre-commit runner: `prek`

## Release process

Maintainers release from protected `main` by pushing a version tag after final validation and PyPI Trusted Publishing verification. See [Release checklist](https://faststream-mq.readthedocs.io/en/latest/release-checklist/).
