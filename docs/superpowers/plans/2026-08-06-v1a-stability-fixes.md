# Freedeck V1a 止血修复（稳定性增强第一阶段）实施计划 — 已执行完毕

> 本文件是 `docs/superpowers/plans/` 归档副本。执行方式：Inline（当前会话逐 Task 执行）。
> 执行日期：2026-08-06。全部 17 个测试通过，前端构建冒烟通过。

**Goal:** 修复 6 个已核实的稳定性硬伤（state.json 崩溃、重启误杀任务、后处理卡死、BaseException 吞异常、空间估算低估、环境变量拼写），并建立 pytest 测试设施——全程 TDD（先写失败测试，再写最小实现）。

**Architecture:** 不引入新架构、不改业务流程和 UI。所有修复落在现有模块内：`tianyi_store.py`（状态持久化）、`tianyi_service.py`（任务编排）、`aria2_manager.py`（环境变量）。测试设施为新增 `tests/` 目录 + python3.11 venv，用桩模块替代仅存在于 Steam Deck 的 `decky` 模块。

**Tech Stack:** Python 3.11（`/opt/homebrew/bin/python3.11`）、pytest + pytest-asyncio、aiohttp/yarl（被测代码的既有依赖）。

## Global Constraints

- 全程 TDD 铁律：**先写失败测试 → 验证失败 → 最小实现 → 验证通过**。任何生产代码改动必须先有其失败测试。
- 每个 Task 的测试运行命令：在仓库根目录执行 `./.venv/bin/python -m pytest tests/<file> -v`。
- 不改动前端 `src/`、不改业务流程、不改 UI 文案（错误信息沿用现有中文风格）。
- `tianyi_service.py` / `tianyi_store.py` 存在**混合换行符**（部分行尾是孤立 `\r`），Edit 时 `old_string` 必须精确匹配 Read 输出（含 `\r` 行）。
- 测试禁止触碰真实用户目录：构造 `TianyiService` 前必须 monkeypatch `config.DECKY_SEND_DIR` 到 `tmp_path`。

## 执行记录

| Task | 内容 | 测试 | Commit |
|---|---|---|---|
| 0 | pytest 测试设施 | 1 个（冒烟） | `4df1e31` |
| 1 | state.json 损坏恢复 + .bak 备份 + chmod 600 | 3 个 | `371288b` |
| 2 | refresh_tasks 不误杀进行中任务 | 4 个 | `3ce4c7d` |
| 3 | 后处理中断恢复 | 3 个 | `132adf7` |
| 4 | 5 处 `except BaseException: pass` 修复 | 2 个 | `e50165a` |
| 5 | 安装空间估算 ×1.5 | 1 个 | `1a440ce` |
| 6 | `FREEDECK_ARIA2_BIN` 拼写兼容 | 3 个 | `06fec5e` |
| 7 | 全量回归（17 passed）+ 前端构建冒烟 + 归档 | — | 见文末 |

每个 Task 均遵循 RED（先跑出新测试的失败）→ GREEN（最小实现至通过）→ 全量回归 → commit 的循环。

## 实施要点（对应原计划的实现方式）

- [x] **Task 0**: `tests/conftest.py`（decky 桩 + `make_task` 工厂 + `service` fixture）、`pytest.ini`（asyncio_mode=auto）、`.gitignore`、`.venv`（python3.11 + pytest/pytest-asyncio/aiohttp/yarl）。
- [x] **Task 1**: `tianyi_store.py` 新增 `_recover_from_backup()`（损坏文件改名 `.corrupt-<ts>` 留现场，回退读 `.bak`）与 `_post_write_housekeeping()`（chmod 600 + copy2 刷新 .bak），`load()` 容错，`save()` 三个写出口都挂 housekeeping。
- [x] **Task 2**: `refresh_tasks()` 同步前先 `ensure_running()`，aria2 不可用则本轮跳过同步（状态不变）；per-task 异常仅当错误含 "not found" 才判 error。
- [x] **Task 3**: `_post_process_completed_task` 入口不再置 `post_processed`，改在三个失败分支与成功末尾置位；`initialize()` 末尾对 `complete + 未后处理` 任务重新调度。
- [x] **Task 4**: 5 处（shutdown×2、登录采集×2、云存档取消×1）改为 `except asyncio.CancelledError: pass` + `except Exception: config.logger.exception(...)`。
- [x] **Task 5**: 新增常量 `INSTALL_SPACE_ESTIMATE_FACTOR = 1.5`，`required_install_bytes = int(required_download_bytes * 1.5)`。
- [x] **Task 6**: `os.getenv("FREEDECK_ARIA2_BIN") or os.getenv("FRIENDECK_ARIA2_BIN")`，新名优先、旧名兼容。

## 执行中发现的偏差记录

- `tianyi_service.py` 大量 CRLF 行导致编辑器精确匹配困难，三处失败分支与空间估算行改用按行号/字节精确的脚本替换（替换前后均断言出现次数为 1）。
- `test_shutdown_logs_failing_cleanup_job` 初版测试有场景错误（任务未启动即被 cancel，走不到异常分支），已修正为 `await asyncio.sleep(0)` 让任务先失败——属测试修正，非生产代码让步。
- 前端构建：`npm install` 因 pnpm-lock 中 linux-musl 依赖失败，改用 `npx pnpm install` 成功；`npm run build`（rollup）通过。`dist/index.js.map` 的构建版本差异已还原，未入库。
- 顺带补充：`.gitignore` 增加 `node_modules/`。

## 遗留（不在 V1a 范围，按重设计路线图）

- V1b：Runtime 自包含（内置 node/aria2/7zz + RuntimeManager）。
- V1c：日志迁至 `DECKY_PLUGIN_LOG_DIR` + 轮转、消灭其余静默 except（39+ 处）、启动自检 + 前端"后端未就绪"状态。
- V1d：CI + `verify_release.py`。
- V2：拆分 6538 行 `tianyi_service.py`（需在测试覆盖进一步扩大后进行）。
