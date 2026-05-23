#!/usr/bin/env bash
set -euo pipefail

uv run --no-sync ty check faststream_mq tests/typing \
  --ignore assert-type-unspellable-subtype \
  --ignore deprecated \
  --ignore invalid-argument-type \
  --ignore invalid-generic-class \
  --ignore invalid-method-override \
  --ignore invalid-return-type \
  --ignore invalid-type-arguments \
  --ignore invalid-yield \
  --ignore unknown-argument \
  --ignore unresolved-attribute \
  --ignore unresolved-import \
  --ignore unresolved-reference
