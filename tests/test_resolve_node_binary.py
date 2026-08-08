"""node 运行时定位（_resolve_node_binary）测试。"""

import os

import pytest

import tianyi_client
from tianyi_client import TianyiApiError


def test_env_var_wins(monkeypatch, tmp_path):
    fake_node = tmp_path / "node"
    fake_node.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setenv("FREEDECK_NODE_BIN", str(fake_node))

    assert tianyi_client._resolve_node_binary() == str(fake_node)


def test_bundled_node_selected_via_plugin_dir(monkeypatch, tmp_path):
    bundled = tmp_path / "defaults" / "runtime" / "linux-x64" / "node"
    bundled.parent.mkdir(parents=True)
    bundled.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.delenv("FREEDECK_NODE_BIN", raising=False)
    monkeypatch.setenv("DECKY_PLUGIN_DIR", str(tmp_path))

    assert tianyi_client._resolve_node_binary() == str(bundled)


def test_falls_back_to_system_node_when_no_bundled(monkeypatch):
    # 仓库不内置 node（GitHub 100MB 限制），无环境变量时应回退系统 node
    monkeypatch.delenv("FREEDECK_NODE_BIN", raising=False)
    monkeypatch.delenv("DECKY_PLUGIN_DIR", raising=False)
    monkeypatch.setattr(tianyi_client.shutil, "which", lambda cmd: "/usr/local/bin/node")

    assert tianyi_client._resolve_node_binary() == "/usr/local/bin/node"


def test_raises_when_nothing_available(monkeypatch, tmp_path):
    from pathlib import Path

    monkeypatch.delenv("FREEDECK_NODE_BIN", raising=False)
    monkeypatch.setenv("DECKY_PLUGIN_DIR", str(tmp_path))  # 空目录，无内置
    # _resolve_node_binary 的候选用的是 Path.is_file（内部走 os.stat），
    # 要在 pathlib 层 patch 才能屏蔽仓库里真实存在的内置 node
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    monkeypatch.setattr(tianyi_client.shutil, "which", lambda cmd: None)

    with pytest.raises(TianyiApiError, match="node"):
        tianyi_client._resolve_node_binary()
