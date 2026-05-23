# PRD: Publish FastStream MQ as a standalone adapter

## Problem Statement

IBM MQ broker support has been implemented for FastStream, but the implementation has not been merged upstream and there is no maintainer update. The user is already using this IBM MQ implementation in production and needs a reliable way to move forward by publishing it as an installable Python package without waiting for upstream FastStream.

The current implementation lives inside the FastStream tree as `faststream.mq`, depends on FastStream internals, and includes broker code, FastAPI integration, observability integrations, examples, docs, and tests. Publishing the full FastStream fork would be confusing and risky. Users need a clean Standalone Project for the FastStream MQ Adapter with its own package metadata, CI, release automation, devcontainer, documentation, examples, and connected IBM MQ verification.

## Solution

Create a clean standalone repository at `github.com/davzucky/faststream-mq` and publish the FastStream MQ Adapter as the PyPI package `faststream-mq`, imported as `faststream_mq`. The package will be a Forked Extraction of the current IBM MQ implementation, preserving the public API names from the in-tree implementation while changing the package path from `faststream.mq` to `faststream_mq`.

The First Release will be `0.1.0`. It will include the existing IBM MQ broker implementation, FastAPI Integration behind an optional extra, Observability Integration behind optional extras, documentation, examples, tests, CI, release automation, and an IBM MQ Development Environment. Before publishing, the release must fix known high-severity runtime blockers in reconnect, settlement, and reply behavior.

The package will be described as an early standalone adapter that is already production-used and still tracks pending upstream work. If equivalent IBM MQ support is accepted upstream, `faststream-mq` will be deprecated in favor of upstream FastStream.

## User Stories

1. As a FastStream user, I want to install IBM MQ support with `pip install faststream-mq`, so that I can use IBM MQ without waiting for upstream FastStream to merge support.
2. As a FastStream user, I want to import the adapter from `faststream_mq`, so that the standalone package has a clear and reliable Python import path.
3. As a FastStream user, I want the package to preserve public API names like `MQBroker`, `TestMQBroker`, `MQMessage`, and `MQResponse`, so that migration from the in-tree implementation is straightforward.
4. As a FastStream user, I want the README to show migration from `faststream.mq` to `faststream_mq`, so that I can update existing code confidently.
5. As a FastStream user, I want the package to avoid a `faststream.mq` compatibility shim, so that there is no fragile module injection into the upstream FastStream package.
6. As an IBM MQ user, I want `pip install faststream-mq` to install IBM MQ runtime dependencies, so that the base package can connect to IBM MQ without an additional broker-runtime extra.
7. As an IBM MQ user, I want TLS helper APIs to remain available, so that existing IBM MQ security configuration patterns continue to work.
8. As an IBM MQ user, I want plaintext username/password security to work as documented, so that I can connect to common IBM MQ development and production configurations.
9. As an IBM MQ user, I want unsupported FastStream security objects to be rejected explicitly, so that runtime behavior does not silently differ from generated AsyncAPI security descriptions.
10. As an IBM MQ user, I want automatic replies to preserve `ReplyToQMgr`, so that cross-queue-manager request/reply workflows work correctly.
11. As an IBM MQ user, I want reconnect during automatic reply publishing not to break the subscriber, so that a transient MQ failure does not permanently stop consumption.
12. As an IBM MQ user, I want commit and backout operations to recover from retryable MQ failures, so that settlement is as resilient as message consumption and publishing.
13. As an IBM MQ user, I want manual-ack consumers to avoid deadlocking when settlement fails, so that failures are observable and the consumer loop has a deterministic outcome.
14. As a production operator, I want the package status to be honest about being early but production-used, so that I can assess adoption risk.
15. As a production operator, I want the package to depend on a tight FastStream version range, so that internal FastStream API changes do not silently break the adapter.
16. As a production operator, I want CI to run real connected IBM MQ tests, so that regressions against a real broker are caught before release.
17. As a production operator, I want mocked tests to run in CI, so that logic regressions are caught quickly without always requiring a broker.
18. As a production operator, I want release artifacts to be built by CI, so that published packages are reproducible and not built manually on a developer machine.
19. As a package maintainer, I want PyPI Trusted Publishing, so that releases do not depend on long-lived PyPI API tokens stored in GitHub secrets.
20. As a package maintainer, I want releases to publish from version tags, so that package versions correspond to source control history.
21. As a package maintainer, I want a clean standalone repository, so that the package does not look like a fork of all FastStream.
22. As a package maintainer, I want Apache-2.0 licensing and FastStream attribution preserved, so that code extraction is compliant and clear.
23. As a package maintainer, I want the README to state the future deprecation policy, so that users know what happens if upstream FastStream accepts equivalent IBM MQ support.
24. As a contributor, I want a devcontainer that starts IBM MQ as a companion service, so that I can develop and run connected tests with minimal setup.
25. As a contributor, I want Docker Compose based on IBM's MQ container project, so that local and CI IBM MQ environments are consistent.
26. As a contributor, I want `uv` and `uv_build`, so that package builds and dependency management are fast and consistent.
27. As a contributor, I want a checked-in lockfile, so that development and CI environments are reproducible.
28. As a contributor, I want pre-commit hooks run by `prek`, so that formatting and validation are easy to run locally.
29. As a contributor, I want `ruff` for formatting and linting, so that style checks are fast and consistent.
30. As a contributor, I want `ty` instead of mypy for typing checks, so that the project uses the preferred type-checking tool.
31. As a contributor, I want the old mypy sample converted into a `tests/typing` check, so that public typing behavior remains covered without retaining mypy terminology.
32. As a FastAPI user, I want FastAPI Integration available through `faststream-mq[fastapi]`, so that I can use MQ routing in FastAPI without making FastAPI a base dependency.
33. As an observability user, I want OpenTelemetry support available through `faststream-mq[otel]`, so that I can instrument IBM MQ messaging when I opt in.
34. As an observability user, I want Prometheus support available through `faststream-mq[prometheus]`, so that I can export IBM MQ messaging metrics when I opt in.
35. As a user who wants all optional integrations, I want `faststream-mq[all]`, so that I can install every supported integration in one command.
36. As a documentation reader, I want README-first documentation, so that I can quickly install, configure, and run the package.
37. As a documentation reader, I want supporting Markdown docs adapted from the existing IBM MQ docs, so that advanced topics are covered without requiring a full docs site for the First Release.
38. As a documentation reader, I want examples updated to `faststream_mq`, so that copy-pasted examples work with the standalone package.
39. As a tester, I want AsyncAPI tests extracted and updated, so that generated specifications stay compatible with the adapter behavior.
40. As a tester, I want docs and examples tested, so that published guidance remains executable.
41. As a tester, I want FastAPI-specific tests run with the FastAPI extra, so that optional integration behavior is verified only when its dependencies are installed.
42. As a tester, I want observability-specific tests run with observability extras, so that optional telemetry and metrics behavior is verified without bloating the base install.
43. As a user on supported Python versions, I want metadata and CI to support Python 3.10 through 3.14, so that the adapter tracks FastStream's supported Python range.
44. As a future maintainer, I want internal FastStream dependency isolation documented as future work, so that the First Release does not take on a risky compatibility-layer refactor.
45. As a future maintainer, I want the package to preserve an upstream merge path, so that standalone publication does not force a permanent fork.

## Implementation Decisions

- Build a new clean Standalone Project rather than destructively converting the FastStream fork.
- Publish the package as `faststream-mq` and expose the Python package as `faststream_mq`.
- Preserve the same public API names as the current in-tree implementation while changing the package path.
- Do not provide a `faststream.mq` compatibility shim.
- Treat this as a Forked Extraction that tracks the current IBM MQ implementation closely enough to preserve an upstream merge path.
- Set the First Release version to `0.1.0`.
- Require Python 3.10 or newer and test Python 3.10, 3.11, 3.12, 3.13, and 3.14.
- Use a tight FastStream dependency range because the adapter currently imports FastStream internals.
- Include IBM MQ runtime dependencies in the base install.
- Provide optional extras for FastAPI Integration, Observability Integration, and an `all` extra.
- Use `uv` and `uv_build` for packaging and dependency workflows.
- Commit a lockfile for reproducible development and CI.
- Use `prek` for pre-commit hooks.
- Use `ruff` for formatting and linting.
- Use `ty` instead of mypy for type checking.
- Move the existing mypy-oriented typing sample into a neutral typing-test area and run it with `ty`.
- Use PyPI Trusted Publishing for Release Automation rather than storing a PyPI token in GitHub secrets.
- Publish releases from version tags.
- Include a devcontainer that starts IBM MQ as a companion service.
- Include Docker Compose configuration for IBM MQ based on IBM's MQ container project.
- Make documentation README-first and include supporting Markdown pages adapted from the existing IBM MQ docs.
- Document that the adapter is early, already production-used, and still tracking pending upstream work.
- Document that `faststream-mq` will be deprecated if equivalent IBM MQ support is accepted upstream.
- Preserve Apache-2.0 licensing and appropriate FastStream attribution.

### Major modules to build or modify

- **Package surface module**: exposes the stable public API for the FastStream MQ Adapter and keeps the import surface simple.
- **Broker module**: owns the `MQBroker` behavior and integration with FastStream broker lifecycle abstractions.
- **Connection/client module**: encapsulates IBM MQ connection setup, reconnect behavior, publish, consume, commit, and backout interactions. This is a deep module candidate because it hides complex MQI/reconnect semantics behind a small broker-facing API.
- **Publisher module**: owns publish commands, request/reply behavior, reply queue manager propagation, and fake publisher behavior for tests.
- **Subscriber module**: owns consumption, handler execution, automatic replies, manual settlement behavior, and deterministic failure behavior for settlement errors.
- **Message module**: owns raw and parsed IBM MQ message concepts, acknowledgement state, reply metadata, and settlement coordination.
- **Security/TLS module**: owns supported security parsing, explicit rejection of unsupported security objects, and TLS helper APIs.
- **Specification module**: owns AsyncAPI/Specification generation for IBM MQ connection, publisher, subscriber, and security metadata.
- **FastAPI Integration module**: provides optional router support installed through the FastAPI extra.
- **Observability Integration modules**: provide optional OpenTelemetry and Prometheus behavior installed through their extras.
- **Testing support module**: provides `TestMQBroker` and fake producer/test utilities used by downstream users and the package test suite.
- **Project automation modules**: provide CI, Release Automation, pre-commit hooks, devcontainer, and IBM MQ Development Environment configuration.
- **Documentation/examples module**: adapts current IBM MQ docs and examples to the standalone package and canonical `faststream_mq` import path.

## Testing Decisions

- Tests should verify external behavior and public contracts, not implementation details.
- Connection tests should verify observable reconnect and settlement outcomes rather than private method calls.
- Publisher tests should verify message destinations, reply metadata, correlation behavior, and fake publisher behavior.
- Subscriber tests should verify consumption, handler invocation, automatic replies, manual ack behavior, and failure behavior under settlement errors.
- Security tests should verify accepted security configurations and explicit rejection of unsupported configurations.
- TLS tests should verify public helper behavior and resulting connection configuration.
- Specification tests should verify generated AsyncAPI/Specification output for connection metadata, publishers, subscribers, and security.
- FastAPI tests should run only when FastAPI Integration dependencies are installed.
- Observability tests should run only when OpenTelemetry and Prometheus dependencies are installed.
- Typing tests should use `ty` against the adapter package and the public typing sample.
- Documentation and example tests should ensure published examples remain executable with `faststream_mq` imports.
- Connected tests should run against a real IBM MQ container in CI and local devcontainer workflows.
- Mocked/unit tests should run independently of IBM MQ for fast feedback.
- The First Release must add or preserve regression coverage for known blockers: reconnect during automatic replies, reconnect-safe commit/backout, manual-ack settlement failure behavior, `ReplyToQMgr` propagation, and unsupported security rejection.
- Prior art exists in the current FastStream tree's MQ-specific tests across broker behavior, AsyncAPI output, docs/examples, observability, FastAPI integration, and typing samples.

## Out of Scope

- Providing a `faststream.mq` compatibility shim.
- Publishing from the full FastStream fork.
- Broad compatibility with arbitrary FastStream versions.
- Removing all FastStream internal dependencies in the First Release.
- Building a public FastStream broker-plugin API.
- Creating a full documentation website as a First Release prerequisite.
- Making FastAPI, OpenTelemetry, or Prometheus mandatory base dependencies.
- Rewriting the IBM MQ implementation from scratch.
- Long-term independent divergence from upstream FastStream as a goal.
- Manual-only release publishing.
- Using long-lived PyPI API tokens for release automation.
- Keeping mypy as the primary type checker.

## Further Notes

- The domain glossary and ADR for this work are captured in the repository documentation.
- The package is intended to unblock IBM MQ users now while preserving the option of upstreaming or deprecating later.
- The implementation should fix known high-severity runtime blockers before publishing `0.1.0`.
- The package should be clear that it is production-used, but still an early standalone adapter extracted from pending FastStream work.
