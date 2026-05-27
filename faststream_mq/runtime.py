from __future__ import annotations

import importlib.util
import platform
from dataclasses import dataclass

_SUPPORTED_NATIVE_CLIENT_PLATFORMS: tuple[tuple[str, frozenset[str]], ...] = (
    ("linux", frozenset({"x86_64", "amd64"})),
    ("windows", frozenset({"x86_64", "amd64"})),
)


@dataclass(frozen=True)
class MQRuntimeStatus:
    """Availability of the native IBM MQ runtime for this process."""

    supported_platform: bool
    ibmmq_installed: bool
    reason: str | None = None

    @property
    def available(self) -> bool:
        return self.supported_platform and self.ibmmq_installed


def is_mq_supported_platform(
    system: str | None = None,
    machine: str | None = None,
) -> bool:
    """Return whether IBM publishes a native C redistributable for a platform."""

    resolved_system = _normalise_system(system or platform.system())
    resolved_machine = _normalise_platform_value(machine or platform.machine())

    return any(
        resolved_system == supported_system and resolved_machine in supported_machines
        for supported_system, supported_machines in _SUPPORTED_NATIVE_CLIENT_PLATFORMS
    )


def get_mq_platform_warning(
    system: str | None = None,
    machine: str | None = None,
) -> str | None:
    resolved_system = _normalise_system(system or platform.system())
    resolved_machine = _normalise_platform_value(machine or platform.machine())

    if is_mq_supported_platform(resolved_system, resolved_machine):
        return None

    return (
        "IBM MQ native client support requires an IBM redistributable C client "
        "for the current platform. IBM MQ 9.4 provides native redistributable "
        "C clients for linux/x86_64 and windows/x64. "
        f"Current platform: {resolved_system}/{resolved_machine}."
    )


def get_mq_runtime_status(
    system: str | None = None,
    machine: str | None = None,
) -> MQRuntimeStatus:
    platform_warning = get_mq_platform_warning(system=system, machine=machine)
    if platform_warning is not None:
        return MQRuntimeStatus(
            supported_platform=False,
            ibmmq_installed=False,
            reason=platform_warning,
        )

    if importlib.util.find_spec("ibmmq") is None:
        return MQRuntimeStatus(
            supported_platform=True,
            ibmmq_installed=False,
            reason=(
                "IBM MQ Python runtime is unavailable. Missing module: ibmmq. "
                "Install faststream-mq on a supported MQ client platform with "
                "the IBM MQ native client libraries available."
            ),
        )

    return MQRuntimeStatus(supported_platform=True, ibmmq_installed=True)


def is_mq_runtime_available(
    system: str | None = None,
    machine: str | None = None,
) -> bool:
    return get_mq_runtime_status(system=system, machine=machine).available


def ensure_mq_runtime_available(
    system: str | None = None,
    machine: str | None = None,
) -> None:
    status = get_mq_runtime_status(system=system, machine=machine)
    if not status.available:
        raise RuntimeError(status.reason)


def _normalise_system(value: str) -> str:
    normalised = _normalise_platform_value(value)
    if normalised in {"win32", "cygwin", "msys"}:
        return "windows"
    return normalised


def _normalise_platform_value(value: str) -> str:
    normalised = value.strip().lower()
    return normalised or "unknown"
