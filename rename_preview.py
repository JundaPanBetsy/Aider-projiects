# -*- coding: utf-8 -*-
"""
E盘文件改名预览工具（只预览，不改名）
- 只扫描指定根目录
- 跳过系统目录
- 强制排除 DeepSeek–API–KEY 文档及其所在文件夹
"""

import os
import re
import csv
import sys

# ============ 配置区 ============
# E 盘根目录
E_DRIVE = r"E:\\"

# 只处理这些一级文件夹（不深入子文件夹）
TARGET_DIRS = [
    "AiderData",
    "Betsy",
    "cursor",
    "C语言",
    "C语言.1",
    "Excel",
    "JianyingPro",
    "JianyingPro Drafts",
    "Project1",
    "Visual Studio-C语言",
    "WeGameApps",
    "Windows Kits",
]

# 强制忽略的密钥文档（不读取、不打开、不扫描）
FORBIDDEN_STEM = "DeepSeek-API-KEY"

OUTPUT_CSV = "rename_preview.csv"

# Windows 非法字符
ILLEGAL_CHARS = r'[\\/:*?"<>|]'
# ================================


def is_forbidden(name: str) -> bool:
    """是否为强制忽略的密钥文档（忽略扩展名与大小写）"""
    stem = os.path.splitext(name)[0]
    return stem.strip().lower() == FORBIDDEN_STEM.lower()


def sanitize_name(name: str) -> str:
    """过滤 Windows 非法字符，并压缩多余空格"""
    name = re.sub(ILLEGAL_CHARS, "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


# 精确名称映射（优先匹配，避免关键词误判）
EXACT_NAME_MAP = {
    "c语言": "C语言-基础代码",
    "c语言.1": "C语言-练习项目",
    "project1": "VS-C语言小项目",
    "betsy": "Betsy-代码项目",
    "visual studio-c语言": "VS-C语言开发工具",
    "windows kits": "Windows系统开发工具包",
}


# 关键词 -> 简洁名称 的映射（按内容特征推断）
KEYWORD_RULES = [
    (("aider",), "Aider-AI编程"),
    (("betsy",), "Betsy-项目"),
    (("cursor",), "Cursor-编辑器"),
    (("jianyingpro drafts", "draft"), "剪映草稿"),
    (("jianyingpro", "剪映"), "剪映-程序"),
    (("wegame",), "WeGame-游戏"),
    (("windows kits", "sdk", "wdk"), "Windows开发工具包"),
    (("visual studio", "vs", "msvc"), "VS-C语言开发"),
    (("excel", "xlsx", "xls", "csv"), "Excel-表格资料"),
    (("project1", "project"), "Project1-工程"),
    (("c语言", "c语言.1", ".c", ".h"), "C语言-学习资料"),
]


def analyze_dir(dirpath: str) -> str:
    """读取文件夹内部的文件/子目录名，推断简洁新名称"""
    try:
        entries = os.listdir(dirpath)
    except OSError:
        return ""

    # 强制忽略密钥文档：不读取、不打开、不扫描
    entries = [e for e in entries if not is_forbidden(e)]

    # 收集用于判断的文本（仅名称，不读取文件内容）
    text = " ".join(entries).lower()
    base = os.path.basename(dirpath).lower()

    # 优先按旧文件夹名精确匹配
    if base in EXACT_NAME_MAP:
        return sanitize_name(EXACT_NAME_MAP[base])

    for keywords, new_name in KEYWORD_RULES:
        for kw in keywords:
            if kw in text or kw in base:
                return sanitize_name(new_name)

    # 无匹配时：用原文件夹名清理后作为推荐名
    return sanitize_name(os.path.basename(dirpath))


def scan():
    """只扫描 E 盘根目录下指定的一级文件夹，不深入子文件夹"""
    results = []
    if not os.path.isdir(E_DRIVE):
        print(f"[跳过] 目录不存在: {E_DRIVE}", file=sys.stderr)
        return results

    for name in TARGET_DIRS:
        # 强制忽略密钥文档
        if is_forbidden(name):
            continue

        dirpath = os.path.join(E_DRIVE, name)
        if not os.path.isdir(dirpath):
            print(f"[跳过] 文件夹不存在: {dirpath}", file=sys.stderr)
            continue

        new_name = analyze_dir(dirpath)
        if new_name and new_name != name:
            results.append((dirpath, name, new_name))
    return results


def main():
    results = scan()
    if not results:
        print("没有需要改名的文件。")
        return
    print(f"{'旧文件夹名':<30} -> 推荐新名称")
    print("-" * 80)
    for _, old, new in results:
        print(f"{old:<30} -> {new}")
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["所在目录", "旧文件夹名", "推荐新名称"])
        for path, old, new in results:
            w.writerow([os.path.dirname(path), old, new])
    print(f"\n共 {len(results)} 项，已导出: {OUTPUT_CSV}")
    print("（本工具只预览，未执行任何改名操作）")


if __name__ == "__main__":
    main()
