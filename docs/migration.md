# Migration from `faststream.mq`

`faststream-mq` is the standalone IBM MQ adapter extracted from unmerged FastStream IBM MQ work.

The PyPI package name is:

```bash
pip install faststream-mq
```

The Python import package is:

```python
faststream_mq
```

There is intentionally no `faststream.mq` compatibility shim.

## Why imports changed

The original implementation lived inside the FastStream source tree as `faststream.mq`. A standalone package cannot safely add `faststream.mq` under the installed `faststream` package because `faststream` is not a namespace package.

For that reason, all IBM MQ imports moved to `faststream_mq`.

## Import replacements

### Broker and test broker

Before:

```python
from faststream.mq import MQBroker, TestMQBroker
```

After:

```python
from faststream_mq import MQBroker, TestMQBroker
```

### FastAPI router

Before:

```python
from faststream.mq.fastapi import MQRouter
```

After:

```python
from faststream_mq.fastapi import MQRouter
```

Install the FastAPI extra if you use this integration:

```bash
pip install "faststream-mq[fastapi]"
```

### Security helpers

Before:

```python
from faststream.mq import MQTLSConfig
```

After:

```python
from faststream_mq import MQTLSConfig
```

### Message types

Before:

```python
from faststream.mq.message import MQMessage, MQRawMessage
```

After:

```python
from faststream_mq.message import MQMessage, MQRawMessage
```

### Schemas

Before:

```python
from faststream.mq.schemas import MQQueue
```

After:

```python
from faststream_mq.schemas import MQQueue
```

## Typical application migration

Before:

```python
from faststream import FastStream
from faststream.mq import MQBroker

broker = MQBroker(
    queue_manager="QM1",
    conn_name="localhost(1414)",
    username="app",
    password="password",
)
app = FastStream(broker)
```

After:

```python
from faststream import FastStream
from faststream_mq import MQBroker

broker = MQBroker(
    queue_manager="QM1",
    conn_name="localhost(1414)",
    username="app",
    password="password",
)
app = FastStream(broker)
```

The broker API is intended to remain source-compatible except for the import path.

## Dependency changes

Remove any dependency on a FastStream fork that provided `faststream.mq`, then install the standalone adapter:

```bash
pip install faststream-mq
```

`faststream-mq` depends on FastStream and installs IBM MQ runtime dependencies including `ibmmq` and `cryptography`.

Optional integrations are available as extras:

```bash
pip install "faststream-mq[fastapi]"
pip install "faststream-mq[otel]"
pip install "faststream-mq[prometheus]"
pip install "faststream-mq[all]"
```

For local development or source installs, `ibmmq` may require the IBM MQ Client SDK. See [IBM MQ Client SDK](mq-client-sdk.md).

## Search-and-replace checklist

In most projects, migration starts with these replacements:

```text
faststream.mq.fastapi -> faststream_mq.fastapi
faststream.mq.message -> faststream_mq.message
faststream.mq.schemas -> faststream_mq.schemas
faststream.mq -> faststream_mq
```

Run tests after each change if your project has custom imports from deeper modules.

## Behavior notes

- There is no `faststream.mq` compatibility shim.
- Queue names, broker configuration, publish/subscribe APIs, manual acknowledgement, request/reply, FastAPI integration, AsyncAPI generation, and observability integrations are intended to match the extracted implementation.
- The adapter depends on FastStream internals, so releases currently pin a narrow compatible FastStream range.
- If equivalent IBM MQ support is accepted upstream by FastStream, `faststream-mq` will be deprecated in favor of the upstream implementation.

## Validation after migration

Recommended checks for your application:

```bash
python -c "from faststream_mq import MQBroker; print(MQBroker)"
pytest
```

If your application has connected IBM MQ tests, run them against a real queue manager. For this repository's local setup, see [Connected IBM MQ testing](connected-testing.md).
