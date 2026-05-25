# IBM MQ Client SDK

`faststream-mq` depends on [`ibmmq`](https://github.com/ibm-messaging/mq-mqi-python){.external-link target="_blank"}, which is a Python wrapper around IBM MQ native client libraries.

Depending on your platform and wheel availability, installing `ibmmq` may require the IBM MQ C headers and client libraries to be present on the machine where the package is installed.

## Common build error

If the IBM MQ client SDK is missing, installing dependencies can fail with an error like this:

```text
fatal error: cmqc.h: No such file or directory
```

`cmqc.h` is an IBM MQ C header. This error means the native IBM MQ client headers are missing or not discoverable while `ibmmq` is being built.

## Recommended setup for this repository

Use the checked-in helper script before syncing Python dependencies:

```bash
MQ_FILE_PATH="$HOME/.local/opt/mqm" ./scripts/install-mq-client.sh
export MQ_FILE_PATH="$HOME/.local/opt/mqm"
export LD_LIBRARY_PATH="$MQ_FILE_PATH/lib64:$LD_LIBRARY_PATH"

uv sync --all-extras --group dev
```

The script downloads and extracts the IBM MQ redistributable client into `MQ_FILE_PATH`. The important files are:

- headers such as `cmqc.h`
- native client libraries under `lib64`

After installing the client SDK, rerun `uv sync` so `ibmmq` can build or install against the available MQ client files.

## Environment variables

### `MQ_FILE_PATH`

`MQ_FILE_PATH` points to the IBM MQ client installation root used by this repository's setup scripts.

Example:

```bash
export MQ_FILE_PATH="$HOME/.local/opt/mqm"
```

### `LD_LIBRARY_PATH`

On Linux, the IBM MQ native libraries must be discoverable at runtime:

```bash
export LD_LIBRARY_PATH="$MQ_FILE_PATH/lib64:$LD_LIBRARY_PATH"
```

If you installed the client SDK in a new shell, restart your terminal, IDE, or devcontainer session so the environment is picked up consistently.

## Devcontainer

The devcontainer is configured to install the IBM MQ client SDK and run IBM MQ services through Docker Compose. Prefer the devcontainer if you want the most reproducible local development environment.

## CI

The GitHub workflows use `scripts/install-mq-client.sh` before installing dependencies and running tests. If you copy this project into another CI system, keep the same ordering:

1. install IBM MQ client SDK
2. export the MQ client environment variables
3. install Python dependencies
4. run tests

## Troubleshooting checklist

If dependency installation still fails:

1. Confirm the client SDK was installed under `MQ_FILE_PATH`.
2. Confirm `cmqc.h` exists somewhere under that installation directory.
3. Confirm `lib64` contains IBM MQ client libraries.
4. Export `MQ_FILE_PATH` and `LD_LIBRARY_PATH` in the same shell where you run `uv sync`.
5. Rerun `uv sync --all-extras --group dev`.

If installation succeeds but consumers crash with an OpenTelemetry-related `UnboundLocalError` involving `hc`, see [Troubleshooting](troubleshooting.md).
