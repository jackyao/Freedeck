"""内置 7zz 运行时的发布护栏测试。

守护"仓库必须随包携带运行时"这一发布约束，防止误删后真机退化为组件不可用。
node 因超过 GitHub 100MB 单文件限制不内置，运行时回退系统 node。
"""

import os

from conftest import PROJECT_ROOT

BUNDLED_7ZZ = os.path.join(PROJECT_ROOT, "defaults", "7z", "linux-x86_64", "7zz")


def _assert_elf_x86_64(path: str) -> None:
    with open(path, "rb") as f:
        header = f.read(20)
    assert header[:4] == b"\x7fELF", f"{path} 不是 ELF"
    assert header[4] == 2, f"{path} 不是 64-bit"
    assert header[18] == 0x3E, f"{path} 不是 x86-64"


def test_bundled_7zz_exists_executable_and_is_elf_x86_64():
    assert os.path.isfile(BUNDLED_7ZZ), "内置 7zz 缺失，发布包在 SteamOS 上将无法解压安装"
    assert os.access(BUNDLED_7ZZ, os.X_OK), "内置 7zz 没有执行权限"
    _assert_elf_x86_64(BUNDLED_7ZZ)

