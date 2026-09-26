# -*- coding: utf-8 -*-
"""
E盘文件夹改名回滚工具
- 读取 E:\\AiderData\\rename_backup\\original_names.txt 中的原名清单
- 一键把文件夹恢复为改名之前的原始名称
- 只操作文件夹名称，绝不读取任何文件内容
- 强制跳过 DeepSeek-API-KEY 相关文件
"""

import os
import sys

# ============ 配置区 ============
E_DRIVE = r"E:\\"
MANIFEST = r"E:\AiderData\rename_backup\original_names.txt"
FORBIDDEN_STEM = "DeepSeek-API-KEY"

# 回滚阶段跳过的文件夹（程序正在使用该目录，不执行回滚）
SKIP_NAMES = {"AiderData"}
# ================================


def is_forbidden(name: str) -> bool:
    """是否为强制忽略的密钥文档（忽略扩展名与大小写）"""
    stem = os.path.splitext(name)[0]
    return stem.strip().lower() == FORBIDDEN_STEM.lower()


def load_manifest(path: str):
    """读取原名清单，返回 [(旧名, 新名), ...]"""
    if not os.path.isfile(path):
        print(f"[错误] 找不到备份清单: {path}")
        sys.exit(1)

    plan = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            old, new = parts[0].strip(), parts[1].strip()
            if is_forbidden(old) or is_forbidden(new):
                print(f"[跳过] 密钥相关条目: {old}")
                continue
            plan.append((old, new))
    return plan


def main():
    plan = load_manifest(MANIFEST)
    if not plan:
        print("备份清单为空，无需回滚。")
        return

    print("=" * 60)
    print("即将回滚以下文件夹名称：")
    print("=" * 60)
    for old, new in plan:
        print(f"{new:<30} -> {old}")
    print("=" * 60)

    # 校验：当前新名文件夹存在，且原旧名未被占用
    for old, new in plan:
        cur_path = os.path.join(E_DRIVE, new)
        old_path = os.path.join(E_DRIVE, old)
        if not os.path.isdir(cur_path):
            print(f"[错误] 当前文件夹不存在: {cur_path}")
            sys.exit(1)
        if os.path.exists(old_path):
            print(f"[错误] 原名称已被占用，无法回滚: {old_path}")
            sys.exit(1)

    answer = input("确认回滚？输入 y 继续，其他任意键退出: ").strip().lower()
    if answer != "y":
        print("已取消，未做任何改动。")
        return

    for old, new in plan:
        if old in SKIP_NAMES:
            print(f"[跳过] 跳过{old}，当前程序正在使用该目录，不执行回滚")
            continue
        cur_path = os.path.join(E_DRIVE, new)
        old_path = os.path.join(E_DRIVE, old)
        if not os.path.isdir(cur_path):
            print(f"【{new} 原文件夹不存在，跳过这条回滚】")
            continue
        try:
            os.rename(cur_path, old_path)
            print(f"[回滚] {new} -> {old}")
        except Exception as e:
            print(f"【{new}文件夹回滚失败，跳过，继续处理下一项】({e})")
            continue

    print("\n回滚完成。")


if __name__ == "__main__":
    main()
