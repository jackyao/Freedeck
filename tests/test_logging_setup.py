"""日志配置测试：落盘目录、轮转参数、降级路径。"""

import os
import sys
from logging.handlers import RotatingFileHandler

import decky

import config


def test_log_dir_prefers_decky_plugin_log_dir():
    assert config._resolve_log_dir() == str(decky.DECKY_PLUGIN_LOG_DIR)


def test_log_dir_falls_back_when_decky_missing(monkeypatch):
    # sys.modules 里 decky 为 None 时 import decky 会抛 ImportError，应走开发回退目录
    monkeypatch.setitem(sys.modules, "decky", None)
    assert config._resolve_log_dir().endswith(os.path.join(".tmp", "logs"))


def test_logger_uses_rotating_file_handler_with_limits():
    handlers = [h for h in config.logger.handlers if isinstance(h, RotatingFileHandler)]
    assert handlers, "freedeck logger 应挂 RotatingFileHandler，而不是写到 /tmp"
    handler = handlers[0]
    assert handler.maxBytes == 10 * 1024 * 1024
    assert handler.backupCount == 7


def test_log_file_created_under_decky_log_dir():
    log_file = os.path.join(str(decky.DECKY_PLUGIN_LOG_DIR), "freedeck.log")
    assert os.path.isfile(log_file), f"日志文件应创建于 {log_file}（tmpfs 的 /tmp 重启即丢）"
