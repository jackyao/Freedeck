内置 7-Zip 运行时说明
=====================

linux-x86_64/7zz
  版本:   7-Zip 26.02（官方 linux-x64 构建）
  来源:   https://www.7-zip.org/a/7z2602-linux-x64.tar.xz
  许可证: GNU LGPL，详见同目录 License.txt
  说明:   动态链接，但依赖仅为 libpthread/libstdc++/libgcc_s/libc，
          这些是 SteamOS 基础系统组件（Steam 客户端本身依赖 libstdc++），
          SteamOS 更新不会影响。
          py_modules/seven_zip_manager.py 的 _resolve_binary_path 优先命中此路径，
          其次回退 FREEDECK_7Z_BIN 环境变量，最后回退系统 7zz/7zr/7z。

升级方式: 从 https://www.7-zip.org/download.html 下载最新 linux-x64 包，
          解出 7zz 替换本目录文件并保持 chmod 755，
          然后运行 ./.venv/bin/python -m pytest tests/test_bundled_runtimes.py 确认护栏通过。
