# startup_checks.py - 启动环境自检
#
# 打开面板时告诉用户具体缺什么（aria2/7z/node/目录/Steam），
# 而不是流程走到一半才报一个模糊错误。

from __future__ import annotations

import os
import tempfile
from typing import Any, Callable, Dict, List

from steam_shortcuts import _find_steam_root
from tianyi_client import _resolve_node_binary


def _check_binary(
    resolve: Callable[[], str],
    check_id: str,
    label: str,
    level: str,
) -> Dict[str, Any]:
    """二进制可用性检查：解析成功返回路径，失败返回异常信息。"""
    try:
        path = resolve()
        return {"id": check_id, "label": label, "ok": True, "level": level, "message": path}
    except Exception as exc:
        return {"id": check_id, "label": label, "ok": False, "level": level, "message": str(exc)}


def _check_dir_writable(path: str, check_id: str, label: str) -> Dict[str, Any]:
    """目录可写性检查：创建目录并真实写入探测文件。"""
    target = str(path or "").strip()
    if not target:
        return {"id": check_id, "label": label, "ok": False, "level": "critical", "message": "目录未配置"}
    try:
        os.makedirs(target, exist_ok=True)
        fd, probe = tempfile.mkstemp(prefix=".freedeck_probe_", dir=target)
        os.close(fd)
        os.remove(probe)
        return {"id": check_id, "label": label, "ok": True, "level": "critical", "message": target}
    except Exception as exc:
        return {
            "id": check_id,
            "label": label,
            "ok": False,
            "level": "critical",
            "message": f"目录不可写 {target}: {exc}",
        }


def run_startup_checks(service: Any) -> List[Dict[str, Any]]:
    """执行全部启动自检，返回结构化结果列表（供面板展示）。"""
    checks: List[Dict[str, Any]] = [
        _check_binary(service.aria2._resolve_binary_path, "aria2", "下载组件 aria2", "critical"),
        _check_binary(service.seven_zip._resolve_binary_path, "seven_zip", "解压组件 7z", "critical"),
        _check_binary(_resolve_node_binary, "node", "Node 运行时（云存档上传/JS 解析）", "optional"),
        _check_dir_writable(service.store.settings.download_dir, "download_dir", "下载目录"),
        _check_dir_writable(service.store.settings.install_dir, "install_dir", "安装目录"),
        _check_dir_writable(os.path.dirname(service.store.state_file), "state_dir", "状态目录"),
    ]

    steam_root = ""
    try:
        steam_root = _find_steam_root()
    except Exception:
        steam_root = ""
    if steam_root:
        checks.append({"id": "steam", "label": "Steam 客户端", "ok": True, "level": "optional", "message": steam_root})
    else:
        checks.append(
            {
                "id": "steam",
                "label": "Steam 客户端",
                "ok": False,
                "level": "optional",
                "message": "未找到 Steam 安装目录，安装的游戏无法自动加入 Steam 库",
            }
        )
    return checks
