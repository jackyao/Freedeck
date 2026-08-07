"""state.json 损坏恢复、备份与权限测试。"""

import json
import os
import stat

from tianyi_store import TianyiStateStore


def test_load_corrupted_state_falls_back_to_defaults(tmp_path):
    state_file = tmp_path / "tianyi" / "state.json"
    state_file.parent.mkdir(parents=True)
    state_file.write_text("{not valid json", encoding="utf-8")

    store = TianyiStateStore(str(state_file))
    store.load()  # 不应抛异常

    assert store.login.cookie == ""
    assert store.tasks == []
    # 损坏文件被保留为现场，便于排查
    backups = list(state_file.parent.glob("state.json.corrupt-*"))
    assert len(backups) == 1


def test_load_corrupted_state_restores_from_bak(tmp_path):
    state_file = tmp_path / "tianyi" / "state.json"
    state_file.parent.mkdir(parents=True)
    state_file.write_text("### broken ###", encoding="utf-8")
    with open(str(state_file) + ".bak", "w", encoding="utf-8") as f:
        json.dump({"login": {"cookie": "abc", "user_account": "u", "updated_at": 1}}, f)

    store = TianyiStateStore(str(state_file))
    store.load()

    assert store.login.cookie == "abc"


def test_save_creates_backup_and_restricts_permissions(tmp_path):
    state_file = tmp_path / "tianyi" / "state.json"
    store = TianyiStateStore(str(state_file))
    store.set_login(cookie="secret", user_account="u")
    store.save()

    with open(str(state_file) + ".bak", encoding="utf-8") as f:
        bak_data = json.load(f)
    assert bak_data["login"]["cookie"] == "secret"
    assert stat.S_IMODE(os.stat(state_file).st_mode) == 0o600
