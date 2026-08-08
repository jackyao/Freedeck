"""启动自检（run_startup_checks）测试。"""

import platform

import pytest

from aria2_manager import Aria2Error

from startup_checks import run_startup_checks

EXPECTED_IDS = {"aria2", "seven_zip", "node", "download_dir", "install_dir", "state_dir", "steam"}


def _checks_by_id(service):
    return {c["id"]: c for c in run_startup_checks(service)}


async def test_all_checks_present(service):
    await service.initialize()
    checks = _checks_by_id(service)
    assert set(checks) == EXPECTED_IDS
    for check in checks.values():
        assert check["level"] in {"critical", "optional"}
        assert isinstance(check["message"], str)


async def test_healthy_environment_reports_core_ok(service, monkeypatch):
    # 模拟 SteamOS x86_64，命中内置 aria2c/7zz
    monkeypatch.setattr(platform, "machine", lambda: "x86_64")
    await service.initialize()

    checks = _checks_by_id(service)

    for check_id in ("aria2", "seven_zip", "download_dir", "install_dir", "state_dir"):
        assert checks[check_id]["ok"] is True, f"{check_id}: {checks[check_id]['message']}"


async def test_broken_aria2_reported_with_message(service, monkeypatch):
    await service.initialize()

    def _raise():
        raise Aria2Error("下载组件不可用，未找到内置 aria2 或系统 aria2c")

    monkeypatch.setattr(service.aria2, "_resolve_binary_path", _raise)

    checks = _checks_by_id(service)
    assert checks["aria2"]["ok"] is False
    assert checks["aria2"]["level"] == "critical"
    assert "aria2" in checks["aria2"]["message"]


async def test_unwritable_download_dir_reported(service, tmp_path):
    # 把下载目录指向一个已存在的文件：makedirs 必然失败，真实复现"目录不可写"
    blocker = tmp_path / "blocked"
    blocker.write_text("x", encoding="utf-8")
    service.store.set_settings(download_dir=str(blocker), install_dir=str(tmp_path / "in"))

    checks = _checks_by_id(service)

    assert checks["download_dir"]["ok"] is False
    assert checks["download_dir"]["level"] == "critical"


async def test_node_and_steam_are_optional(service):
    checks = _checks_by_id(service)
    assert checks["node"]["level"] == "optional"
    assert checks["steam"]["level"] == "optional"


async def test_panel_state_includes_startup_checks(service):
    await service.initialize()
    state = await service.get_panel_state()

    assert "startup_checks" in state
    ids = {c["id"] for c in state["startup_checks"]}
    assert ids == EXPECTED_IDS
