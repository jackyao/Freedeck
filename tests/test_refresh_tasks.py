"""refresh_tasks 的 aria2 异常容错测试。"""

from aria2_manager import Aria2Error

from conftest import make_task


class FakeAria2:
    """可控的 aria2 管理器替身（外部进程边界，允许 fake）。"""

    def __init__(self, *, ensure_error=None, status_map=None, status_error=None):
        self.ensure_calls = 0
        self._ensure_error = ensure_error
        self._status_map = status_map or {}
        self._status_error = status_error

    async def ensure_running(self):
        self.ensure_calls += 1
        if self._ensure_error:
            raise self._ensure_error
        return {"rpc_url": "fake", "binary_path": "fake"}

    async def tell_status(self, gid):
        if self._status_error:
            raise self._status_error
        return self._status_map[gid]


async def test_refresh_keeps_tasks_when_aria2_unavailable(service):
    task = make_task(status="active")
    service.store.tasks = [task]
    service.aria2 = FakeAria2(ensure_error=Aria2Error("aria2 未运行"))

    views = await service.refresh_tasks()

    assert views[0]["status"] == "active"  # 修复前会被误判为 error
    assert service.aria2.ensure_calls >= 1


async def test_refresh_keeps_status_on_transient_rpc_error(service):
    task = make_task(status="active")
    service.store.tasks = [task]
    service.aria2 = FakeAria2(status_error=Aria2Error("aria2 rpc 请求失败 status=502"))

    views = await service.refresh_tasks()

    assert views[0]["status"] == "active"


async def test_refresh_marks_error_only_when_gid_not_found(service):
    task = make_task(status="active", gid="gid-1")
    service.store.tasks = [task]
    service.aria2 = FakeAria2(
        status_error=Aria2Error("aria2 rpc 错误 code=1 message=GID gid-1 is not found")
    )

    views = await service.refresh_tasks()

    assert views[0]["status"] == "error"


async def test_refresh_syncs_progress_when_healthy(service):
    task = make_task(status="active", gid="gid-1")
    service.store.tasks = [task]
    service.aria2 = FakeAria2(status_map={
        "gid-1": {"status": "active", "totalLength": "200",
                  "completedLength": "50", "downloadSpeed": "1024"},
    })

    views = await service.refresh_tasks()

    assert views[0]["status"] == "active"
    assert views[0]["progress"] == 25.0
