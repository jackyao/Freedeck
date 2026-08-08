"""shutdown 清理路径的异常语义测试。"""

import asyncio
import logging


async def test_shutdown_cancels_running_post_process_job(service):
    started = asyncio.Event()

    async def long_job():
        started.set()
        await asyncio.sleep(3600)

    job = asyncio.create_task(long_job())
    service._post_process_jobs["t1"] = job
    await started.wait()

    await service.shutdown()  # 不应抛异常

    assert job.cancelled()


async def test_shutdown_logs_failing_cleanup_job(service, caplog):
    async def bad_job():
        raise ValueError("boom")

    job = asyncio.create_task(bad_job())
    service._post_process_jobs["t2"] = job
    # 让任务先跑起来并完成失败；否则 shutdown 会在其启动前 cancel，
    # 走 CancelledError 分支而非预期的异常记录分支。
    await asyncio.sleep(0)
    assert job.done()

    with caplog.at_level(logging.ERROR, logger="freedeck"):
        await service.shutdown()

    assert job.done()
    assert any("boom" in record.getMessage() or record.exc_info for record in caplog.records)
