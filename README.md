# faststream-mq

Standalone IBM MQ adapter for [FastStream](https://github.com/ag2ai/faststream).

`faststream-mq` is an early standalone adapter extracted from pending FastStream IBM MQ work. It is already used in production, but still tracks upstream FastStream work closely. If equivalent IBM MQ support is accepted upstream, this package will be deprecated in favor of upstream FastStream.

## Install

```bash
pip install faststream-mq
```

Optional integrations:

```bash
pip install "faststream-mq[fastapi]"
pip install "faststream-mq[otel]"
pip install "faststream-mq[prometheus]"
pip install "faststream-mq[all]"
```

## Quick start

```python
from faststream import FastStream
from faststream_mq import MQBroker

broker = MQBroker(queue_manager="QM1")
app = FastStream(broker)


@broker.subscriber("DEV.QUEUE.1")
async def handle(message: str) -> None:
    print(message)
```

Run a local IBM MQ broker with Docker Compose:

```bash
docker compose up -d ibmmq
```

## Migration from the pending FastStream PR

The standalone adapter intentionally uses `faststream_mq` as its canonical import package.

```python
# Before
from faststream.mq import MQBroker, TestMQBroker

# After
from faststream_mq import MQBroker, TestMQBroker
```

There is intentionally no `faststream.mq` compatibility shim. A standalone package cannot safely inject a submodule into the non-namespace `faststream` package.

## Development

This repository uses `uv`, `uv_build`, `ruff`, `ty`, and `prek`.

Install the IBM MQ client SDK first; the `ibmmq` Python package needs the MQ C headers to build.

```bash
MQ_FILE_PATH="$HOME/.local/opt/mqm" ./scripts/install-mq-client.sh
export MQ_FILE_PATH="$HOME/.local/opt/mqm"
export LD_LIBRARY_PATH="$MQ_FILE_PATH/lib64:$LD_LIBRARY_PATH"

uv sync --all-extras --group dev
uv run prek install
uv run ruff format
uv run ruff check
./scripts/ty-check.sh
uv run pytest
uv run --only-group docs mkdocs build --strict
```

Connected IBM MQ tests require the local MQ services and a successful client-connectivity probe:

```bash
docker compose up -d ibmmq ibmmq_ha2
uv run python scripts/wait-mq-ready.py "127.0.0.1(1414)" "127.0.0.1(1415)"
uv run pytest -m connected
```

## Documentation

Documentation is built with MkDocs using the `docs` uv dependency group.
Read the Docs can build the site from `.readthedocs.yaml` without a separate `requirements.txt`.

```bash
uv sync --only-group docs
uv run --only-group docs mkdocs serve
```

## Release

Releases are published from version tags by GitHub Actions using PyPI Trusted Publishing.

```bash
git tag v0.1.0
git push origin v0.1.0
```

## License and attribution

Apache-2.0. This package is extracted from IBM MQ broker work originally written for FastStream and preserves the FastStream upstream attribution and API style where appropriate.
