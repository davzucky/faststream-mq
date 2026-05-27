from pathlib import Path
from typing import Any

import pytest

from faststream_mq.helpers.client import _load_ibmmq
from faststream_mq.runtime import (
    MQRuntimeStatus,
    ensure_mq_runtime_available,
    get_mq_platform_warning,
    get_mq_runtime_status,
    is_mq_runtime_available,
    is_mq_supported_platform,
)
from faststream_mq.testing import TestMQBroker, require_mq_runtime


def test_supported_mq_client_platforms_follow_ibm_native_redist_matrix() -> None:
    assert is_mq_supported_platform(system="Linux", machine="x86_64")
    assert is_mq_supported_platform(system="linux", machine="amd64")
    assert is_mq_supported_platform(system="Windows", machine="AMD64")
    assert is_mq_supported_platform(system="win32", machine="x86_64")

    assert not is_mq_supported_platform(system="Darwin", machine="x86_64")
    assert not is_mq_supported_platform(system="Linux", machine="aarch64")
    assert not is_mq_supported_platform(system="Windows", machine="arm64")


def test_platform_warning_explains_unsupported_native_client_platform() -> None:
    warning = get_mq_platform_warning(system="Darwin", machine="arm64")

    assert warning is not None
    assert "IBM redistributable C client" in warning
    assert "linux/x86_64" in warning
    assert "windows/x64" in warning
    assert "darwin/arm64" in warning


def test_runtime_status_is_unavailable_on_unsupported_platform() -> None:
    status = get_mq_runtime_status(system="Darwin", machine="arm64")

    assert status.supported_platform is False
    assert status.ibmmq_installed is False
    assert status.reason is not None
    assert "darwin/arm64" in status.reason
    assert not status.available
    assert not is_mq_runtime_available(system="Darwin", machine="arm64")


def test_runtime_status_requires_ibmmq_on_supported_platform(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_import(_module: str) -> object:
        raise ImportError("No module named 'ibmmq'")

    monkeypatch.setattr("faststream_mq.runtime.importlib.import_module", fail_import)

    status = get_mq_runtime_status(system="Linux", machine="x86_64")

    assert status.supported_platform is True
    assert status.ibmmq_installed is False
    assert status.available is False
    assert status.reason is not None
    assert "unloadable module: ibmmq" in status.reason
    assert "No module named 'ibmmq'" in status.reason


def test_runtime_status_is_available_when_supported_platform_has_ibmmq(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "faststream_mq.runtime.importlib.import_module",
        lambda _: object(),
    )

    status = get_mq_runtime_status(system="Windows", machine="AMD64")

    assert status == MQRuntimeStatus(supported_platform=True, ibmmq_installed=True)
    assert status.available


def test_ensure_mq_runtime_available_raises_clear_error() -> None:
    with pytest.raises(RuntimeError, match="Current platform: darwin/arm64"):
        ensure_mq_runtime_available(system="Darwin", machine="arm64")


def test_ibmmq_loader_reports_runtime_status_before_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "faststream_mq.helpers.client.get_mq_runtime_status",
        lambda: MQRuntimeStatus(
            supported_platform=False,
            ibmmq_installed=False,
            reason="unsupported test platform",
        ),
    )

    with pytest.raises(ImportError, match="unsupported test platform"):
        _load_ibmmq()


def test_require_mq_runtime_skips_when_runtime_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "faststream_mq.testing.get_mq_runtime_status",
        lambda: MQRuntimeStatus(
            supported_platform=True,
            ibmmq_installed=False,
            reason="missing ibmmq for test",
        ),
    )

    @require_mq_runtime
    def sample_test() -> None: ...

    marks = _pytest_marks(sample_test)
    assert len(marks) == 1
    assert marks[0].name == "skipif"
    assert marks[0].args == (True,)
    assert marks[0].kwargs["reason"] == "missing ibmmq for test"


def test_require_mq_runtime_does_not_skip_when_runtime_is_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "faststream_mq.testing.get_mq_runtime_status",
        lambda: MQRuntimeStatus(supported_platform=True, ibmmq_installed=True),
    )

    @require_mq_runtime
    def sample_test() -> None: ...

    marks = _pytest_marks(sample_test)
    assert len(marks) == 1
    assert marks[0].name == "skipif"
    assert marks[0].args == (False,)


def test_mock_testing_surface_is_importable_without_ibmmq() -> None:
    assert TestMQBroker is not None


def test_ibmmq_dependency_is_limited_to_supported_native_client_platforms() -> None:
    pyproject = Path("pyproject.toml").read_text()

    assert "ibmmq>=2,<3;" in pyproject
    assert "sys_platform == 'linux'" in pyproject
    assert "sys_platform == 'win32'" in pyproject
    assert "platform_machine == 'x86_64'" in pyproject
    assert "platform_machine == 'AMD64'" in pyproject


def _pytest_marks(test_func: Any) -> list[pytest.Mark]:
    marks = getattr(test_func, "pytestmark", [])
    if isinstance(marks, list):
        return marks
    return [marks]
