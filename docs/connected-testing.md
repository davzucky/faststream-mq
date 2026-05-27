# Connected IBM MQ testing

Most tests in this repository run without a real queue manager. Tests marked `connected` exercise the adapter against real IBM MQ containers and are required in CI before changes can merge.

Connected tests also require the native IBM MQ runtime. `faststream-mq` is installable on unsupported MQ client platforms for mock testing, but real MQ connections require a Supported MQ Client Platform and importable `ibmmq` runtime. For IBM MQ 9.4 native redistributable C clients, Supported MQ Client Platforms are Linux x86-64 and Windows x64. The connected CI workflow currently automates the Linux path.

## Start local IBM MQ services

From the repository root, start both queue managers:

```bash
docker compose up -d ibmmq ibmmq_ha2
```

The compose services expose:

| Service | Queue manager | Connection name |
| ------- | ------------- | --------------- |
| `ibmmq` | `QM1` | `127.0.0.1(1414)` |
| `ibmmq_ha2` | `QM1` | `127.0.0.1(1415)` |

Both services use the development application credentials:

```text
username: app
password: password
```

## Wait for readiness

Container health checks are not enough by themselves. The repository includes a readiness probe that waits for Docker health and then verifies client connectivity through `ibmmq`:

```bash
uv run python scripts/wait-mq-ready.py "127.0.0.1(1414)" "127.0.0.1(1415)"
```

Run this before connected tests. It catches cases where the container is running but the queue manager is not ready to accept client connections yet.

## Run connected tests

```bash
uv run pytest -m connected
```

To run the full local test suite including connected tests:

```bash
uv run pytest
```

## Stop services

```bash
docker compose down
```

If you need a clean MQ data directory, remove volumes too:

```bash
docker compose down -v
```

## Devcontainer

The devcontainer uses Docker Compose for the same IBM MQ services. After opening the devcontainer, run the readiness probe before connected tests:

```bash
uv run python scripts/wait-mq-ready.py "127.0.0.1(1414)" "127.0.0.1(1415)"
uv run pytest -m connected
```

If the devcontainer was already running while services were recreated, reopen the devcontainer or restart the terminal session to refresh environment variables.

## Troubleshooting

### `ibmmq` cannot be imported, `cmqc.h` is missing, or the platform is unsupported

Install the IBM MQ Client SDK before syncing dependencies when you are on a Supported MQ Client Platform. See [IBM MQ Client SDK](mq-client-sdk.md). On unsupported MQ client platforms, use `TestMQBroker` and tests that do not require the native runtime.

### Readiness probe times out

Check container status:

```bash
docker compose ps
```

Then inspect logs:

```bash
docker compose logs ibmmq
docker compose logs ibmmq_ha2
```

If the containers are unhealthy or stuck during initialization, recreate them:

```bash
docker compose down -v
docker compose up -d ibmmq ibmmq_ha2
uv run python scripts/wait-mq-ready.py "127.0.0.1(1414)" "127.0.0.1(1415)"
```

### Port already in use

The local services bind `1414` and `1415`. If either port is already used by another MQ installation or container, stop the conflicting process or adjust the Compose mapping before running connected tests.

### Connected test timeout

Run the readiness probe again first. If it passes, rerun the specific failing test with verbose output:

```bash
uv run pytest -m connected -vv
```

### OpenTelemetry `hc` crash from `ibmmq`

If consumers fail with:

```text
UnboundLocalError: cannot access local variable 'hc' where it is not associated with a value
```

see [Troubleshooting](troubleshooting.md) for the upstream `ibmmq` OpenTelemetry issue and the `MQIPY_NOOTEL=true` workaround.
