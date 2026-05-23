# Publish FastStream MQ as a standalone adapter

The IBM MQ broker implementation was written for FastStream but has not been merged upstream, so we will publish it as a standalone package at `github.com/davzucky/faststream-mq` with PyPI distribution name `faststream-mq` and import package `faststream_mq`. This lets users install IBM MQ support now while preserving Apache-2.0 licensing, FastStream attribution, and a future upstream merge path.

## Consequences

The adapter will depend tightly on the FastStream version range it was extracted from because it currently uses FastStream internals. The standalone repository must carry its own CI, release automation, devcontainer, documentation, examples, and connected IBM MQ test setup.
