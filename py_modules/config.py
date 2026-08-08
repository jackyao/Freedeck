# config.py - Freedeck 配置与日志

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_FORMAT = "[%(asctime)s | %(filename)s:%(lineno)s:%(funcName)s] %(levelname)s: %(message)s"
_LOG_MAX_BYTES = 10 * 1024 * 1024
_LOG_BACKUP_COUNT = 7


def _resolve_log_dir() -> str:
    """日志目录：优先 Decky 持久日志目录，开发环境回退到插件目录下的 .tmp/logs。

    注意不能写 /tmp：SteamOS 上 /tmp 是 tmpfs，重启即丢，故障现场无法保留。
    """
    try:
        import decky

        candidate = str(getattr(decky, "DECKY_PLUGIN_LOG_DIR", "") or "").strip()
        if candidate:
            return candidate
    except Exception:
        pass
    return str(Path(__file__).resolve().parents[1] / ".tmp" / "logs")


def setup_logger() -> logging.Logger:
    """初始化日志器：RotatingFileHandler（10MB × 7），落盘失败降级到控制台。"""
    named = logging.getLogger("freedeck")
    named.setLevel(logging.INFO)
    if named.handlers:
        return named

    handler: logging.Handler
    try:
        log_dir = _resolve_log_dir()
        os.makedirs(log_dir, exist_ok=True)
        handler = RotatingFileHandler(
            os.path.join(log_dir, "freedeck.log"),
            maxBytes=_LOG_MAX_BYTES,
            backupCount=_LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
    except Exception:
        handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    named.addHandler(handler)
    return named


logger = setup_logger()

# 路径配置
HOME_DIR = str(Path.home())
DOWNLOADS_DIR = str(Path.home() / "Downloads")
SHARE_DIR = str(Path.home() / ".local" / "share")
DECKY_SEND_DIR = os.path.join(SHARE_DIR, "Freedeck")

# 服务配置
# 仅监听回环地址，禁止局域网访问。
DEFAULT_SERVER_HOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 59271
PORT_CHECK_RETRIES = 5
PORT_CHECK_RETRY_DELAY = 0.3
PORT_RELEASE_TIMEOUT = 5.0

# 设置键
SETTINGS_KEY = "freedeck_settings"
SETTING_RUNNING = "running"
SETTING_PORT = "port"
SETTING_DOWNLOAD_DIR = "download_dir"
