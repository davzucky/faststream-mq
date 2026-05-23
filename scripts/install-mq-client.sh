#!/usr/bin/env bash
set -euo pipefail

MQ_VERSION="${MQ_VERSION:-9.4.3.0}"
MQ_ARCHIVE="${MQ_VERSION}-IBM-MQC-Redist-LinuxX64.tar.gz"
MQ_URL="${MQ_URL:-https://public.dhe.ibm.com/ibmdl/export/pub/software/websphere/messaging/mqdev/redist/${MQ_ARCHIVE}}"
MQ_INSTALL_DIR="${MQ_FILE_PATH:-/opt/mqm}"

if [ -f "${MQ_INSTALL_DIR}/inc/cmqc.h" ]; then
  echo "IBM MQ client SDK already installed at ${MQ_INSTALL_DIR}"
  exit 0
fi

if [ "$(id -u)" -ne 0 ]; then
  SUDO=sudo
else
  SUDO=
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

curl --fail --location --retry 3 --output "${TMP_DIR}/${MQ_ARCHIVE}" "${MQ_URL}"
${SUDO} mkdir -p "${MQ_INSTALL_DIR}"
${SUDO} tar -xzf "${TMP_DIR}/${MQ_ARCHIVE}" -C "${MQ_INSTALL_DIR}"

if [ ! -f "${MQ_INSTALL_DIR}/inc/cmqc.h" ]; then
  echo "IBM MQ client SDK extraction did not create ${MQ_INSTALL_DIR}/inc/cmqc.h" >&2
  echo "Found candidate header paths:" >&2
  find "${MQ_INSTALL_DIR}" -name cmqc.h -print >&2 || true
  exit 1
fi

if [ ! -d "${MQ_INSTALL_DIR}/lib64" ]; then
  echo "IBM MQ client SDK extraction did not create ${MQ_INSTALL_DIR}/lib64" >&2
  exit 1
fi

echo "Installed IBM MQ client SDK at ${MQ_INSTALL_DIR}"
