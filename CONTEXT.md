# FastStream MQ Adapter

This context describes the language for publishing the IBM MQ broker adapter as a standalone FastStream extension package.

## Language

**FastStream MQ Adapter**:
A standalone package that provides IBM MQ broker support for FastStream applications while upstream FastStream review is pending. Its distribution name is `faststream-mq` and its Python import package is `faststream_mq`. Installing it should work on unsupported MQ client platforms for documentation and mock testing, include the native IBM MQ runtime dependency only on supported MQ client platforms, preserve the same public API names as the current in-tree `faststream.mq` implementation, document migration from `faststream.mq` to `faststream_mq`, and not provide a `faststream.mq` compatibility shim.
_Avoid_: `fastream_mq`, `faststream.mq` as the canonical external adapter name, mandatory native MQ dependency on unsupported MQ client platforms, compatibility shim

**Forked Extraction**:
An independently published adapter package extracted from the pending in-tree IBM MQ implementation. It should track the branch closely enough to preserve an upstream merge path, while allowing users to install IBM MQ support before upstream accepts it. The published package should live in `github.com/davzucky/faststream-mq`, preserve Apache-2.0 licensing and appropriate FastStream attribution, and document that it will be deprecated if equivalent IBM MQ support is accepted upstream.
_Avoid_: permanent fork, unrelated rewrite, publishing from the full FastStream fork, unattributed code extraction

**Standalone Project**:
The repository form of the FastStream MQ Adapter, including package code, tests, CI, release automation, devcontainer configuration, documentation, examples, and project metadata. It should be created as a clean repository, not by destructively converting the FastStream fork. It should be self-contained enough for development and publication without the full FastStream source tree, and CI should include all relevant MQ-specific tests, including mocked tests, real connected IBM MQ tests, documentation/example tests, AsyncAPI tests, observability tests, FastAPI tests, and typing checks. Documentation should be README-first with supporting Markdown pages under `docs/` rather than requiring a full documentation site for the First Release. Packaging should use `uv` and `uv_build` with a checked-in lockfile, pre-commit hooks should use `prek`, typing checks should use `ty` instead of mypy, and the current mypy sample should become a `tests/typing/` check.
_Avoid_: source-only extraction, package without release pipeline, undocumented package, mocked-only verification, full docs-site prerequisite, dropping existing MQ coverage, destructive conversion of the FastStream fork, mypy-only typing workflow

**IBM MQ Development Environment**:
The local and CI container setup used to run connected IBM MQ tests. It should include a Docker Compose service based on IBM's MQ container project and the devcontainer should start IBM MQ as a companion service.
_Avoid_: manual-only MQ setup, devcontainer without MQ service

**Supported MQ Client Platform**:
An operating-system and CPU-architecture combination for which IBM publishes a redistributable IBM MQ native C client library and the FastStream MQ Adapter can load `ibmmq` against that library. For IBM MQ 9.4 redistributable clients, this means Linux x86-64 and Windows x64 for native MQ applications; the Java/JMS redistributable package does not make a platform supported for this Python adapter.
_Avoid_: assuming all Python platforms are supported, Linux-only policy when IBM also ships Windows x64 native clients, treating Java/JMS-only redistributables as Python MQ runtime support, platform support without native MQ client libraries

**Release Automation**:
The GitHub Actions workflow that builds and publishes the FastStream MQ Adapter to PyPI. It should publish from version tags using PyPI Trusted Publishing rather than GitHub-stored PyPI API tokens.
_Avoid_: manual-only publishing, long-lived PyPI token secret

**First Release**:
The `0.1.0` initial public release of the FastStream MQ Adapter. It must include extraction from the FastStream tree and fixes for known high-severity runtime blockers. It should require Python 3.10 or newer, depend on a tightly bounded FastStream version range because it currently uses FastStream internals, and avoid broader internal-dependency isolation work. Its public status should be described as an early standalone adapter that is already production-used but still tracks pending upstream work.
_Avoid_: preview dump, unreviewed branch snapshot, broad FastStream compatibility claim, compatibility-layer refactor, unsupported toy project

**Internal-Dependency Isolation**:
A future refactoring effort that centralizes or reduces imports from FastStream internals inside the adapter. It is not part of the First Release.
_Avoid_: v0.1.0 prerequisite, public plugin API

**FastAPI Integration**:
The optional FastAPI router support for the FastStream MQ Adapter. It should ship in the First Release because the code already exists, but its dependencies should be installed through the `faststream-mq[fastapi]` extra.
_Avoid_: mandatory FastAPI dependency, separate later package

**Observability Integration**:
The optional OpenTelemetry and Prometheus support for the FastStream MQ Adapter. It should ship in the First Release with dependencies installed through `faststream-mq[otel]`, `faststream-mq[prometheus]`, or `faststream-mq[all]`.
_Avoid_: mandatory observability dependencies, excluding existing observability modules

## Example dialogue

Developer: "Which package should users install for IBM MQ support?"
Domain expert: "Install the FastStream MQ Adapter with `pip install faststream-mq`."

Developer: "Which module should examples import from?"
Domain expert: "Use `from faststream_mq import MQBroker`; `faststream.mq` belongs to the in-tree upstream implementation, not the standalone adapter."
