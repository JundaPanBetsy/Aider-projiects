# -*- coding: utf-8 -*-
"""扫描指定目录，输出所有文件的名称、大小、修改时间，保存为 file_info.md"""

import os
import time

# 要扫描的根目录
ROOT_DIR = r"E:\AiderData"
# 输出文件路径
OUTPUT_FILE = "file_info.md"


def format_size(size):
    """把字节数转换成易读的格式"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def scan_directory(root):
    """遍历目录，返回文件信息列表"""
    results = []
    # os.walk 递归遍历所有子目录
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            full_path = os.path.join(dirpath, name)
            try:
                # 获取文件状态信息
                stat = os.stat(full_path)
                size = stat.st_size
                mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
                results.append((full_path, size, mtime))
            except (OSError, PermissionError) as e:
                # 无法访问的文件跳过并提示
                print(f"[跳过] 无法访问: {full_path} -> {e}")
                continue
    return results


def write_markdown(results, output):
    """把结果写入 Markdown 文件"""
    with open(output, "w", encoding="utf-8") as f:
        f.write("# 文件信息列表\n\n")
        f.write(f"扫描目录: `{ROOT_DIR}`\n\n")
        f.write(f"文件总数: {len(results)}\n\n")
        f.write("| 文件名 | 大小 | 修改时间 |\n")
        f.write("| --- | --- | --- |\n")
        for path, size, mtime in results:
            f.write(f"| {path} | {format_size(size)} | {mtime} |\n")


def main():
    # 检查根目录是否存在
    if not os.path.isdir(ROOT_DIR):
        print(f"错误: 目录不存在 -> {ROOT_DIR}")
        return

    print(f"开始扫描: {ROOT_DIR}")
    results = scan_directory(ROOT_DIR)
    write_markdown(results, OUTPUT_FILE)
    print(f"扫描完成，共 {len(results)} 个文件，结果已保存到 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
