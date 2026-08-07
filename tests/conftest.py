"""pytest 共享设施：decky 桩模块 + TianyiService 测试工厂。"""

import logging
import os
import sys
import types

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY_MODULES = os.path.join(PROJECT_ROOT, "py_modules")
if PY_MODULES not in sys.path:
    sys.path.insert(0, PY_MODULES)

# decky 仅存在于 Steam Deck 运行时，测试环境用桩模块替代（必须在 import 被测模块前安装）。
decky_stub = types.ModuleType("decky")
decky_stub.DECKY_PLUGIN_DIR = PROJECT_ROOT
decky_stub.DECKY_PLUGIN_NAME = "Freedeck"
decky_stub.DECKY_PLUGIN_VERSION = "0.0.0-test"
decky_stub.DECKY_PLUGIN_SETTINGS_DIR = os.path.join(PROJECT_ROOT, ".tmp", "test-settings")
decky_stub.DECKY_PLUGIN_LOG_DIR = os.path.join(PROJECT_ROOT, ".tmp", "test-logs")
decky_stub.DECKY_HOME = os.path.join(PROJECT_ROOT, ".tmp", "test-decky-home")
decky_stub.DECKY_USER_HOME = os.path.expanduser("~")
decky_stub.DECKY_USER = "deck"
decky_stub.logger = logging.getLogger("decky-stub")
sys.modules.setdefault("decky", decky_stub)

from tianyi_store import TianyiTaskRecord  # noqa: E402


def make_task(
    *,
    task_id: str = "task-1",
    gid: str = "gid-1",
    status: str = "active",
    post_processed: bool = False,
    file_name: str = "game.7z",
    download_dir: str = "",
    local_path: str = "",
) -> TianyiTaskRecord:
    """构造一条最小任务记录。"""
    return TianyiTaskRecord(
        task_id=task_id,
        gid=gid,
        game_id="game-1",
        game_title="测试游戏",
        share_code="sc",
        share_id="sid",
        file_id="fid",
        file_name=file_name,
        download_dir=download_dir,
        local_path=local_path,
        status=status,
        progress=0.0,
        speed=0,
        post_processed=post_processed,
    )


@pytest.fixture
def service(tmp_path, monkeypatch):
    """构造状态目录隔离到 tmp_path 的 TianyiService。"""
    import config

    monkeypatch.setattr(config, "DECKY_SEND_DIR", str(tmp_path / "share"))

    from tianyi_service import TianyiService

    plugin = types.SimpleNamespace(downloads_dir=str(tmp_path / "downloads"))
    return TianyiService(plugin)
