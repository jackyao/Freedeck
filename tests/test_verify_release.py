"""verify_release.py 发布完整性检查测试。"""

import subprocess
import sys

import verify_release

from conftest import PROJECT_ROOT


def test_check_binary_ok_for_bundled_aria2():
    ok, message = verify_release.check_binary("defaults/aria2/linux-x64/aria2c", "aria2")
    assert ok, message


def test_check_binary_fails_when_missing():
    ok, message = verify_release.check_binary("defaults/aria2/linux-x64/nonexistent", "aria2")
    assert not ok
    assert "缺失" in message


def test_check_binary_fails_for_non_elf(tmp_path):
    fake = tmp_path / "aria2c"
    fake.write_text("not an elf", encoding="utf-8")
    ok, message = verify_release.check_binary(str(fake), "aria2")
    assert not ok


def test_check_catalog_ok():
    ok, message = verify_release.check_catalog()
    assert ok, message


def test_check_frontend_dist_ok():
    ok, message = verify_release.check_frontend()
    assert ok, message


def test_check_python_compiles_ok():
    ok, message = verify_release.check_python_compiles()
    assert ok, message


def test_check_plugin_json_ok():
    ok, message = verify_release.check_plugin_json()
    assert ok, message


def test_main_passes_on_current_repo(capsys):
    assert verify_release.main() == 0


def test_cli_exit_zero_on_current_repo():
    result = subprocess.run(
        [sys.executable, "verify_release.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
