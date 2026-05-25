#!/usr/bin/env bash
set -euo pipefail

uv run --no-sync ty check faststream_mq tests/typing
