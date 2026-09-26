# -*- coding: utf-8 -*-
"""
E盘文件夹批量改名执行工具
- 读取 E:\\AiderData\\rename_preview.csv（B列旧名，C列新名）
- 执行前创建 git 备份存档，便于一键回滚
- 打印清单并等待手动输入 y 确认
- 校验重名冲突、文件夹不存在、权限错误
- 只操作文件夹名称，绝不读取任何文件内容
- 强制跳过 DeepSeek-API-KEY 相关文件
"""

import os
import csv
import sys
import shutil
import subprocess
from datetime import datetime

# ============ 配置区 ============
E_DRIVE = r"E:\\"
CSV_PATH = r"E:\AiderData\rename_preview.csv"
BACKUP_DIR = r"E:\AiderData\rename_backup"
FORBIDDEN_STEM = "DeepSeek-API-KEY"

# 执行阶段跳过的文件夹（程序正在使用该目录，不执行改名）
SKIP_NAMES = {"AiderData"}
# ================================


def is_forbidden(name: str) -> bool:
    """是否为强制忽略的密钥文档（忽略扩展名与大小写）"""
    stem = os.path.splitext(name)[0]
    return stem.strip().lower() == FORBIDDEN_STEM.lower()


def load_plan(csv_path: str):
    """读取 CSV，返回 [(旧名, 新名), ...]；只读名称，不读文件内容"""
    if not os.path.isfile(csv_path):
        print(f"[错误] 找不到清单文件: {csv_path}")
        sys.exit(1)

    plan = []
    with open(csv_path, "r", newline="", encoding="gbk") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # 跳过表头
        for row in reader:
            if len(row) < 3:
                continue
            old, new = row[1].strip(), row[2].strip()
            if not old or not new:
                continue
            if is_forbidden(old) or is_forbidden(new):
                print(f"[跳过] 密钥相关条目: {old}")
                continue
            plan.append((old, new))
    return plan


def validate(plan):
    """改名前校验：文件夹存在、目标不重名（仅提示，不终止）"""
    for old, new in plan:
        old_path = os.path.join(E_DRIVE, old)
        new_path = os.path.join(E_DRIVE, new)

        if not os.path.isdir(old_path):
            print(f"【{old}文件夹不存在，跳过】")
            continue

        if os.path.exists(new_path):
            print(f"[提示] 重名冲突，将跳过: {new_path}")
            continue

        if old == new:
            print(f"[提示] 新旧名称相同，将跳过: {old}")


def create_git_backup(plan):
    """在 E:\\AiderData 创建 git 备份存档，记录旧文件夹名称"""
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # 写入原名清单
    manifest = os.path.join(BACKUP_DIR, "original_names.txt")
    with open(manifest, "w", encoding="utf-8") as f:
        for old, new in plan:
            f.write(f"{old}\t{new}\n")

    # 初始化 git 仓库并提交
    try:
        if not os.path.isdir(os.path.join(BACKUP_DIR, ".git")):
            subprocess.run(["git", "init"], cwd=BACKUP_DIR, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "add", "-A"], cwd=BACKUP_DIR, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        msg = f"backup before rename {datetime.now():%Y-%m-%d %H:%M:%S}"
        subprocess.run(["git", "commit", "-m", msg], cwd=BACKUP_DIR, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[备份] git 存档已创建: {BACKUP_DIR}")
    except FileNotFoundError:
        print("[警告] 未检测到 git，已跳过 git 存档（原名清单仍已保存）")
    except subprocess.CalledProcessError as e:
        print(f"[警告] git 存档失败: {e}（原名清单仍已保存）")


def execute(plan):
    """执行改名，只操作文件夹名称"""
    for old, new in plan:
        if old in SKIP_NAMES:
            print(f"[跳过] 跳过{old}，当前程序正在使用该目录，不执行改名")
            continue
        if old == new:
            continue
        old_path = os.path.join(E_DRIVE, old)
        new_path = os.path.join(E_DRIVE, new)
        if not os.path.isdir(old_path):
            print(f"【{old}文件夹不存在，跳过】")
            continue
        try:
            os.rename(old_path, new_path)
            print(f"[完成] {old} -> {new}")
        except Exception as e:
            print(f"【{old}文件夹改名失败，跳过，继续处理下一项】({e})")
            continue


def main():
    plan = load_plan(CSV_PATH)
    if not plan:
        print("清单为空，无需改名。")
        return

    print("=" * 60)
    print("即将执行以下文件夹改名：")
    print("=" * 60)
    for old, new in plan:
        print(f"{old:<30} -> {new}")
    print("=" * 60)

    validate(plan)

    answer = input("确认执行改名？输入 y 继续，其他任意键退出: ").strip().lower()
    if answer != "y":
        print("已取消，未做任何改动。")
        return

    create_git_backup(plan)
    execute(plan)
    print("\n全部完成。如需回滚，请运行 rollback_rename.py")


if __name__ == "__main__":
    main()
