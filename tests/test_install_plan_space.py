"""安装计划的空间估算测试。"""

import types

import tianyi_service
from conftest import make_task  # noqa: F401  （保持 conftest 导入一致性）


async def test_install_plan_estimates_install_space_with_factor(service, tmp_path, monkeypatch):
    async def fake_check_login():
        return True, {}, "ok"

    monkeypatch.setattr(service, "check_login_state", fake_check_login)

    files = [types.SimpleNamespace(file_id="f1", name="game.7z", size=1_000_000, is_folder=False)]
    resolved = types.SimpleNamespace(share_code="sc", share_id="sid", pwd="pwd", files=files)

    async def fake_resolve(url, cookie):
        return resolved

    monkeypatch.setattr(tianyi_service, "resolve_share", fake_resolve)
    service.store.set_settings(download_dir=str(tmp_path / "dl"),
                               install_dir=str(tmp_path / "in"))

    plan = await service._build_install_plan(share_url="https://cloud.189.cn/t/not-in-catalog")

    assert plan["required_download_bytes"] == 1_000_000
    assert plan["required_install_bytes"] == int(1_000_000 * 1.5)
