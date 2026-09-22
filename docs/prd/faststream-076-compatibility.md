# FastStream 0.7.6 compatibility

## Problem

FastStream 0.7.6 requires `address` when constructing both `SubscriberSpec` and `PublisherSpec`. The adapter omits it in both places, causing schema generation to fail. The reported downstream symptom is HTTP 500 from Magpie's `/magpie/asyncapi` endpoint on !8159.

This repository declares `faststream>=0.7.0rc1,<0.8` and locks `0.7.0rc1`. The report's `0.7.5` lock refers to Magpie's main branch.

Upstream definitions: [subscriber](https://github.com/ag2ai/faststream/blob/0.7.6/faststream/specification/schema/subscriber.py), [publisher](https://github.com/ag2ai/faststream/blob/0.7.6/faststream/specification/schema/publisher.py), and [AsyncAPI 3 channels](https://github.com/ag2ai/faststream/blob/0.7.6/faststream/specification/asyncapi/v3_0_0/schema/channels.py).

## Agreed decisions

- Prepare a release-ready adapter fix with regression coverage and release notes. Publishing and changing Magpie's constraint are separate follow-up work.
- Require `faststream>=0.7.6,<0.8`. Do not add compatibility code for older FastStream constructors.

## Implementation plan

- Pass the queue name with the effective router prefix as `address` in both MQ specification constructors. Display titles and handler names must not change the destination address.
- Update dependency metadata and the lockfile, and document the minimum version and fix under the unreleased changelog entry.
- Extend existing AsyncAPI tests to cover subscribers and publishers with prefixes and custom titles. Check that generated addresses match runtime queue destinations.
- Exercise the FastAPI schema endpoint with registered MQ endpoints, without requiring a live MQ connection.
- Run both AsyncAPI 2.6 and 3.0 suites against FastStream 0.7.6, then the repository's standard validation checks. Report any checks blocked by the local environment.

The implementation plan was approved on 2026-09-22 and is tracked in [issue #20](https://github.com/davzucky/faststream-mq/issues/20). The dependency review and cryptography upgrade were approved for the same ticket.

## Dependency review

Checked direct runtime, optional, build, test, lint, and documentation dependencies against PyPI on 2026-09-22. Updated dependencies needed for FastStream compatibility or to address advisories in the runtime lockfile.

| Dependency | Previous lock | Updated lock | Reason |
| --- | --- | --- | --- |
| FastStream | 0.7.0rc1 | 0.7.6 | Fix the schema contract and require the tested minimum. |
| FastDepends | 3.0.8 | 3.0.9 | Required by FastStream 0.7.6. |
| AnyIO | 4.13.0 | 4.15.1 | FastStream requires at least 4.14.2, which fixes TLS hostname matching and process-worker deadlocks. |
| FastAPI | 0.136.1 | 0.141.1 | Refresh the optional HTTP integration alongside Starlette. |
| Starlette | 1.0.1 | 1.6.0 | Exclude known vulnerable releases with a minimum of 1.3.1 in both FastAPI extras. |
| cryptography | 46.0.7 | 50.0.1 | The old `<47` bound blocks security fixes. Require `>=50,<51`. |
| typing-extensions | 4.15.0 | 4.16.0 | Transitive resolver update. |

Cryptography 49 removed Intel macOS and 32-bit Windows wheels and tightened certificate parsing. Its 50.0 release fixes the PKCS7 decryption oracle; 50.0.1 refreshes bundled OpenSSL. The adapter uses PEM certificates and PKCS12 serialization, so its TLS tests are part of validation. Intel macOS and 32-bit Windows are no longer supported by cryptography. This does not change the native IBM MQ supported-platform policy.

IBM MQ's Python client has a newer 2.1.1 release than the locked 2.0.6. The existing `>=2,<3` range already permits it. Keep the lock on 2.0.6 for this fix; a native client upgrade needs its own runtime review. OpenTelemetry, Prometheus, Pydantic Settings, test tools, lint tools, and MkDocs Material also have newer releases, but no compatibility or runtime audit finding requires changing them here. Existing exact pins and the Typer cap remain. `uv_build` 0.12.17 is available, but the package build succeeds with existing metadata despite uv's backend-version warning; defer that tooling update.

Sources: [IBM MQ client metadata](https://pypi.org/pypi/ibmmq/json), [FastStream 0.7.6](https://github.com/ag2ai/faststream/releases/tag/0.7.6), [AnyIO changelog](https://anyio.readthedocs.io/en/stable/versionhistory.html), [Starlette advisories](https://github.com/Kludex/starlette/security/advisories), and [cryptography changelog](https://cryptography.io/en/latest/changelog/).

The runtime audit uses `uv export --frozen --no-dev --all-extras --no-hashes --no-emit-project` followed by `pip-audit --no-deps --disable-pip`. The updated lockfile has no known vulnerabilities reported by that audit. This does not establish exploitability of the old findings in this adapter.
