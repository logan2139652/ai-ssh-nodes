#!/usr/bin/env python3
"""
CtrlPlane — SSH config 同步器

从 servers.yaml 生成 ~/.ssh/config 的 CtrlPlane 管理区块。
读取 servers.yaml 中的连接信息（host/port/user/identity_file 等），
写入 ~/.ssh/config 的标记区块中（区块外的手动配置不受影响）。

用法:
  python sync_ssh_config.py             # 默认内嵌工作区
  python sync_ssh_config.py --workspace ~/my-infra
  python sync_ssh_config.py --dry-run   # 预览，不写入
"""

import sys
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    print("需要 PyYAML: pip install pyyaml")
    sys.exit(1)

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.yaml"
DEFAULT_WORKSPACE = SKILL_DIR / "workspace"
SSH_CONFIG = Path.home() / ".ssh" / "config"

# ~/.ssh/config 中 CtrlPlane 管理的标记行
BLOCK_START = "# >>> CtrlPlane managed — DO NOT EDIT between markers <<<"
BLOCK_END = "# <<< CtrlPlane managed"


def resolve_workspace(override=None):
    if override:
        return Path(override).expanduser().resolve()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            c = yaml.safe_load(f) or {}
        if c.get("workspace_dir"):
            return Path(c["workspace_dir"]).expanduser().resolve()
    return DEFAULT_WORKSPACE


def read_servers(workspace_dir):
    sf = workspace_dir / "servers.yaml"
    if not sf.exists():
        print(f"✗ 未找到 {sf}")
        sys.exit(1)
    with open(sf, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("servers", {})


def build_ssh_entries(servers):
    """从 servers.yaml 生成 SSH config 条目"""
    lines = []
    lines.append(BLOCK_START)
    lines.append(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"# 来源: servers.yaml")
    lines.append(f"# 服务器数: {len(servers)}")
    lines.append("")

    for alias, s in sorted(servers.items()):
        lines.append(f"Host {alias}")
        lines.append(f"    HostName {s['host']}")
        lines.append(f"    User {s.get('user', 'root')}")
        if s.get("port") and s["port"] != 22:
            lines.append(f"    Port {s['port']}")

        identity_file = s.get("identity_file", "~/.ssh/id_ed25519")
        lines.append(f"    IdentityFile {identity_file}")
        lines.append(f"    StrictHostKeyChecking no")
        lines.append(f"    ServerAliveInterval 60")
        lines.append(f"    ServerAliveCountMax 3")
        lines.append("")

    lines.append(BLOCK_END)
    return "\n".join(lines)


def sync(dry_run=False, override=None):
    workspace_dir = resolve_workspace(override)
    servers = read_servers(workspace_dir)
    new_block = build_ssh_entries(servers)

    if dry_run:
        print("=" * 60)
        print("DRY RUN — 将写入以下内容到 ~/.ssh/config:")
        print("=" * 60)
        print(new_block)
        return

    # 读取现有 SSH config
    if SSH_CONFIG.exists():
        old = SSH_CONFIG.read_text(encoding="utf-8")
    else:
        SSH_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        old = ""

    # 替换 CtrlPlane 管理区块（区块外保持不变）
    if BLOCK_START in old and BLOCK_END in old:
        before = old.split(BLOCK_START)[0].rstrip()
        after = old.split(BLOCK_END)[1]
        new_content = before + "\n\n" + new_block + after
    else:
        # 首次写入：追加到文件末尾
        if old and not old.endswith("\n"):
            old += "\n"
        new_content = old + "\n" + new_block + "\n"

    # 备份
    backup = SSH_CONFIG.with_suffix(".config.bak")
    SSH_CONFIG.write_text(new_content, encoding="utf-8")

    print(f"✓ SSH config 已同步")
    print(f"  {len(servers)} 台服务器 → {SSH_CONFIG}")
    for alias in sorted(servers):
        s = servers[alias]
        print(f"  ▸ {alias} ({s['user']}@{s['host']})")


def main():
    workspace_override = None
    dry_run = False

    args = sys.argv[1:]
    if "--dry-run" in args:
        dry_run = True
        args.remove("--dry-run")
    if "--workspace" in args:
        idx = args.index("--workspace")
        workspace_override = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    sync(dry_run=dry_run, override=workspace_override)


if __name__ == "__main__":
    main()
