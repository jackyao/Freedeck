"""静默 except 补日志后的回归测试：代表性兜底路径应留下日志记录。"""

import logging

import steam_shortcuts
import tianyi_client


def _has_record(caplog, *, level: int, needle: str) -> bool:
    return any(
        record.name == "freedeck" and record.levelno == level and needle in record.getMessage()
        for record in caplog.records
    )


def test_tianyi_client_parse_int_fallback_logs_debug(caplog):
    """_parse_int 解析失败回退默认值时应有 debug 记录。"""
    with caplog.at_level(logging.DEBUG, logger="freedeck"):
        assert tianyi_client._parse_int("not-a-number", 7) == 7
    assert _has_record(caplog, level=logging.DEBUG, needle="解析整数失败")


def test_tianyi_client_jsonp_parse_fallback_logs_debug(caplog):
    """JSONP 内层 JSON 解析失败回退时应有 debug 记录，且返回结构不变。"""
    with caplog.at_level(logging.DEBUG, logger="freedeck"):
        payload = tianyi_client._normalize_json_payload("cb({invalid json})")
    assert payload == {"message": "cb({invalid json})", "_raw_text": "cb({invalid json})"}
    assert _has_record(caplog, level=logging.DEBUG, needle="解析 JSONP 响应失败")


def test_steam_shortcuts_account_id_fallback_logs_debug(caplog):
    """Steam64 ID 解析失败回退空串时应有 debug 记录。"""
    with caplog.at_level(logging.DEBUG, logger="freedeck"):
        assert steam_shortcuts._steam64_to_account_id("bad-id") == ""
    assert _has_record(caplog, level=logging.DEBUG, needle="解析 Steam64 ID 失败")
