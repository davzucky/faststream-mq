# Changelog

All notable changes to `faststream-mq` will be documented in this file.

This project follows [Semantic Versioning](https://semver.org/). Until `1.0.0`, minor versions may include API adjustments needed to track FastStream internals.

## [Unreleased]

### Added

- Release checklist and contributor documentation.

## [0.1.0] - 2026-05-25

Initial standalone release of the FastStream IBM MQ adapter.

### Added

- Standalone PyPI package `faststream-mq` with canonical import package `faststream_mq`.
- IBM MQ broker, publisher, subscriber, request/reply, and manual acknowledgement support.
- FastAPI router integration through the `fastapi` extra.
- OpenTelemetry and Prometheus integrations through optional extras.
- IBM MQ TLS helper APIs.
- AsyncAPI/specification support for IBM MQ publishers, subscribers, and security metadata.
- Docker Compose and devcontainer setup for local IBM MQ development.
- CI for mocked tests, package builds, documentation builds, and real connected IBM MQ tests.
- Release workflow using PyPI Trusted Publishing from version tags.
- Documentation for migration from `faststream.mq`, IBM MQ Client SDK setup, connected testing, high availability, security, RPC, message handling, and troubleshooting.

### Fixed

- Reconnect-safe automatic reply publishing.
- Reconnect-safe `commit()` and `backout()` settlement operations.
- Manual settlement failure handling so consumers do not deadlock.
- `ReplyToQMgr` propagation for reply flows.
- Explicit rejection of unsupported FastStream security objects.
- IBM MQ Client SDK extraction in local/CI setup.

### Notes

- There is intentionally no `faststream.mq` compatibility shim. Use `faststream_mq` imports.
- The adapter depends on FastStream internals and currently uses a narrow FastStream compatibility range.
- If equivalent IBM MQ support is accepted upstream by FastStream, this package will be deprecated in favor of upstream FastStream.

[Unreleased]: https://github.com/davzucky/faststream-mq/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/davzucky/faststream-mq/releases/tag/v0.1.0
