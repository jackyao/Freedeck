"""下载后处理的标志位时序与中断恢复测试。"""

import os

from conftest import make_task


async def test_post_process_sets_flag_only_after_completion(service, tmp_path, monkeypatch):
    # 用非压缩包走 copy 路径，避免测试依赖 7z 二进制
    src = tmp_path / "game.bin"
    src.write_bytes(b"x" * 16)
    task = make_task(status="complete", file_name="game.bin",
                     download_dir=str(tmp_path), local_path=str(src))
    service.store.tasks = [task]
    service.store.set_settings(download_dir=str(tmp_path / "dl"),
                               install_dir=str(tmp_path / "installed"))

    observed = {}

    async def fake_register(*, task, target_dir):
        observed["post_processed_during"] = task.post_processed
        return {"ok": False, "message": "skip"}

    monkeypatch.setattr(service, "_auto_register_task_to_steam", fake_register)

    await service._post_process_completed_task(task)

    assert observed["post_processed_during"] is False  # 修复前入口就置 True
    assert task.post_processed is True
    assert task.install_status == "installed"
    assert os.path.isfile(os.path.join(task.installed_path, "game.bin"))


async def test_initialize_reschedules_interrupted_post_process(service, monkeypatch):
    task = make_task(status="complete", post_processed=False)
    service.store.tasks = [task]
    scheduled = []
    monkeypatch.setattr(service, "_schedule_post_process_task", scheduled.append)

    await service.initialize()

    assert scheduled == [task.task_id]


async def test_initialize_ignores_finished_post_process(service, monkeypatch):
    task = make_task(status="complete", post_processed=True)
    service.store.tasks = [task]
    scheduled = []
    monkeypatch.setattr(service, "_schedule_post_process_task", scheduled.append)

    await service.initialize()

    assert scheduled == []
