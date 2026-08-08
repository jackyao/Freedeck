"""aria2 二进制定位的环境变量测试。"""

import os

from aria2_manager import Aria2Manager


def _make_fake_bin(tmp_path):
    fake_bin = tmp_path / "aria2c"
    fake_bin.write_text("#!/bin/sh\n", encoding="utf-8")
    return str(fake_bin)


def test_freedeck_env_var_is_respected(monkeypatch, tmp_path):
    path = _make_fake_bin(tmp_path)
    monkeypatch.setenv("FREEDECK_ARIA2_BIN", path)
    monkeypatch.delenv("FRIENDECK_ARIA2_BIN", raising=False)

    mgr = Aria2Manager(plugin_dir=str(tmp_path), work_dir=str(tmp_path / "w"))

    assert mgr._resolve_binary_path() == path


def test_legacy_friendeck_env_var_still_works(monkeypatch, tmp_path):
    path = _make_fake_bin(tmp_path)
    monkeypatch.delenv("FREEDECK_ARIA2_BIN", raising=False)
    monkeypatch.setenv("FRIENDECK_ARIA2_BIN", path)

    mgr = Aria2Manager(plugin_dir=str(tmp_path), work_dir=str(tmp_path / "w"))

    assert mgr._resolve_binary_path() == path


def test_freedeck_env_wins_over_legacy(monkeypatch, tmp_path):
    new_path = _make_fake_bin(tmp_path)
    legacy = tmp_path / "legacy-aria2c"
    legacy.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setenv("FREEDECK_ARIA2_BIN", new_path)
    monkeypatch.setenv("FRIENDECK_ARIA2_BIN", str(legacy))

    mgr = Aria2Manager(plugin_dir=str(tmp_path), work_dir=str(tmp_path / "w"))

    assert mgr._resolve_binary_path() == new_path
