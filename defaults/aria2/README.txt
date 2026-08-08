内置 aria2 运行时说明
=====================

linux-x64/aria2c
  版本:   aria2 1.37.0（静态编译，musl static，x86-64）
  来源:   https://github.com/abcfy2/aria2-static-build/releases/tag/1.37.0
  文件:   aria2-x86_64-linux-musl_static.zip
  许可证: aria2 为 GPLv2，上游源码 https://github.com/aria2/aria2
  说明:   全静态链接，不依赖系统 glibc/openssl 等库，
          SteamOS 更新后仍可直接运行。
          py_modules/aria2_manager.py 的 _resolve_binary_path 会优先命中此路径，
          其次回退 FREEDECK_ARIA2_BIN 环境变量（兼容旧拼写 FRIENDECK_ARIA2_BIN），
          最后回退系统 aria2c。

升级方式: 下载同来源新版静态包，替换 linux-x64/aria2c 并保持 chmod 755，
          然后运行 ./.venv/bin/python -m pytest tests/test_bundled_aria2.py 确认护栏通过。
