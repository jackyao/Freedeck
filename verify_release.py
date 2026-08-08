#!/usr/bin/env python3
"""verify_release.py - Freedeck 发布完整性检查。

发布前运行：检查内置运行时、游戏目录、前端产物、Python 语法与插件清单。
任一关键项缺失以非零退出，阻止发布。

用法: python verify_release.py
"""

import glob
import json
import os
import py_compile
import sys
import tempfile
from typing import List, Tuple

ROOT = os.path.dirname(os.path.abspath(__file__))

MIN_DIST_BYTES = 50 * 1024
MIN_CATALOG_BYTES = 100 * 1024
CATALOG_REQUIRED_COLUMNS = ("game_id", "title", "down_url")


def _abs(path: str) -> str:
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def check_binary(rel_path: str, label: str) -> Tuple[bool, str]:
    """内置二进制：存在、可执行、是 ELF x86-64。"""
    path = _abs(rel_path)
    if not os.path.isfile(path):
        return False, f"{label} 缺失: {path}"
    if not os.access(path, os.X_OK):
        return False, f"{label} 没有执行权限: {path}"
    with open(path, "rb") as f:
        header = f.read(20)
    if len(header) < 20 or header[:4] != b"\x7fELF" or header[4] != 2 or header[18] != 0x3E:
        return False, f"{label} 不是 ELF x86-64 二进制: {path}"
    return True, f"{label} OK（{os.path.getsize(path)} 字节）"


def check_catalog() -> Tuple[bool, str]:
    """游戏目录 CSV：存在、足够大、表头包含必需列。"""
    csv_files = sorted(glob.glob(os.path.join(ROOT, "defaults", "tianyi_catalog", "*.csv")))
    if not csv_files:
        return False, "游戏目录 CSV 缺失: defaults/tianyi_catalog/*.csv"
    path = csv_files[0]
    size = os.path.getsize(path)
    if size < MIN_CATALOG_BYTES:
        return False, f"游戏目录 CSV 异常（仅 {size} 字节）: {path}"
    with open(path, "r", encoding="utf-8-sig") as f:
        header = f.readline()
    missing = [col for col in CATALOG_REQUIRED_COLUMNS if col not in header]
    if missing:
        return False, f"游戏目录 CSV 表头缺少列 {missing}: {path}"
    return True, f"游戏目录 OK（{os.path.basename(path)}，{size} 字节）"


def check_frontend() -> Tuple[bool, str]:
    """前端产物：dist/index.js 存在且体积合理。"""
    path = os.path.join(ROOT, "dist", "index.js")
    if not os.path.isfile(path):
        return False, "前端产物缺失: dist/index.js（先运行 pnpm build）"
    size = os.path.getsize(path)
    if size < MIN_DIST_BYTES:
        return False, f"前端产物异常（仅 {size} 字节），可能构建不完整: {path}"
    return True, f"前端产物 OK（{size} 字节）"


def check_python_compiles() -> Tuple[bool, str]:
    """全部 Python 源文件语法可编译。"""
    sources = [os.path.join(ROOT, "main.py")]
    sources.extend(sorted(glob.glob(os.path.join(ROOT, "py_modules", "**", "*.py"), recursive=True)))
    if not sources:
        return False, "未找到 Python 源文件"
    with tempfile.TemporaryDirectory(prefix="freedeck_pyc_") as tmp:
        for index, path in enumerate(sources):
            try:
                py_compile.compile(path, cfile=os.path.join(tmp, f"{index}.pyc"), doraise=True)
            except py_compile.PyCompileError as exc:
                return False, f"Python 语法错误: {path}: {exc.msg}"
    return True, f"Python 语法 OK（{len(sources)} 个文件）"


def check_plugin_json() -> Tuple[bool, str]:
    """插件清单：合法 JSON 且含 name 字段。"""
    path = os.path.join(ROOT, "plugin.json")
    if not os.path.isfile(path):
        return False, "plugin.json 缺失"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        return False, f"plugin.json 不是合法 JSON: {exc}"
    if not str(data.get("name", "")).strip():
        return False, "plugin.json 缺少 name 字段"
    return True, f"plugin.json OK（{data['name']}）"


def main() -> int:
    checks: List[Tuple[bool, str]] = [
        check_binary("defaults/aria2/linux-x64/aria2c", "aria2c"),
        check_binary("defaults/7z/linux-x86_64/7zz", "7zz"),
        check_catalog(),
        check_frontend(),
        check_python_compiles(),
        check_plugin_json(),
    ]
    failed = 0
    for ok, message in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {message}")
        if not ok:
            failed += 1
    if failed:
        print(f"\n发布检查未通过：{failed} 项失败")
        return 1
    print("\n发布检查全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
