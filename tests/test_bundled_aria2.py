"""内置 aria2 运行时的发布护栏测试。

说明：`_resolve_binary_path` 的内置优先逻辑在 V1a 之前已存在，
本文件守护的是"仓库必须随包携带静态 aria2c"这一发布约束，
防止二进制被误删后在真机上退化为"组件不可用"。
"""

import os
import platform
import shutil

from aria2_manager import Aria2Manager

from conftest import PROJECT_ROOT

BUNDLED_ARIA2 = os.path.join(PROJECT_ROOT, "defaults", "aria2", "linux-x64", "aria2c")


def test_bundled_linux_x64_binary_exists_and_is_executable():
    assert os.path.isfile(BUNDLED_ARIA2), "内置 aria2c 缺失，发布包在 SteamOS 上将无法下载"
    assert os.access(BUNDLED_ARIA2, os.X_OK), "内置 aria2c 没有执行权限"


def test_bundled_binary_is_static_elf():
    with open(BUNDLED_ARIA2, "rb") as f:
        header = f.read(20)
    # ELF magic + 64-bit + x86-64
    assert header[:4] == b"\x7fELF"
    assert header[4] == 2  # ELFCLASS64
    assert header[18] == 0x3E  # EM_X86_64 (little-endian)


def test_bundled_binary_is_selected_on_linux_x64(monkeypatch, tmp_path):
    monkeypatch.setattr(platform, "machine", lambda: "x86_64")
    monkeypatch.delenv("FREEDECK_ARIA2_BIN", raising=False)
    monkeypatch.delenv("FRIENDECK_ARIA2_BIN", raising=False)
    # 屏蔽系统 aria2c，验证命中的确实是内置路径而不是系统回退
    monkeypatch.setattr(shutil, "which", lambda cmd: None)

    mgr = Aria2Manager(plugin_dir=PROJECT_ROOT, work_dir=str(tmp_path / "w"))

    assert mgr._resolve_binary_path() == BUNDLED_ARIA2
