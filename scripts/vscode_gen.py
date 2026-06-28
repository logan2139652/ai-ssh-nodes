#!/usr/bin/env python3
"""
ai-ssh-nodes — VSCode .code-workspace 生成器

从 servers.yaml 生成 VSCode Multi-root 工作区文件，
包含本地共享区 + 所有远程服务器的 home 目录。

工作区目录优先级：
  1. 命令行 --workspace 参数
  2. config.yaml 中的 workspace_dir（用户自定义）
  3. skill 目录内嵌 workspace/（默认）

用法:
  python vscode_gen.py                         # 使用默认/配置目录
  python vscode_gen.py --workspace /my/path    # 临时指定工作区
  python vscode_gen.py --open                  # 生成后自动用 VSCode 打开
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    print("需要 PyYAML: pip install pyyaml")
    sys.exit(1)

# ── 路径解析 ──────────────────────────────────────────────────────────────────

SKILL_DIR = Path(__file__).parent.parent  # ~/.workbuddy/skills/ai-ssh-nodes/
CONFIG_FILE = SKILL_DIR / "config.yaml"
DEFAULT_WORKSPACE = SKILL_DIR / "workspace"  # 内嵌默认目录


def resolve_workspace_dir(override: str = None) -> Path:
    """
    解析工作区目录，按优先级：
      1. 命令行 --workspace 参数（override）
      2. config.yaml 中的 workspace_dir
      3. skill 目录内嵌 workspace/（默认）
    """
    # 优先级 1：命令行参数
    if override:
        return Path(override).expanduser().resolve()

    # 优先级 2：config.yaml
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        workspace_dir = config.get("workspace_dir")
        if workspace_dir:
            return Path(workspace_dir).expanduser().resolve()

    # 优先级 3：默认内嵌目录
    return DEFAULT_WORKSPACE


# ── 读取服务器 ─────────────────────────────────────────────────────────────────

def read_servers(workspace_dir: Path) -> dict:
    """读取 servers.yaml"""
    servers_file = workspace_dir / "servers.yaml"

    if not servers_file.exists():
        print(f"✗ 未找到 {servers_file}")
        print()
        print("  请创建 servers.yaml，结构：")
        print("  servers:")
        print("    my-server:")
        print("      host: 1.2.3.4")
        print("      port: 22")
        print("      user: root")
        print("      os: Linux")
        print("      type: cloud")
        print("      role: 生产服务器")
        print("      environment: production")
        print("      permission: confirm_required")
        print("      tags: []")
        sys.exit(1)

    with open(servers_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    servers = data.get("servers", {})
    if not servers:
        print(f"✗ {servers_file} 中没有服务器条目")
        sys.exit(1)

    return servers


# ── 构建 .code-workspace ───────────────────────────────────────────────────────

def build_folders(servers: dict, workspace_dir: Path) -> list:
    """构建 VSCode folders 列表"""
    folders = []

    # 本地共享区
    share_dir = workspace_dir / "workspace" if (workspace_dir / "workspace").exists() else workspace_dir
    # 兼容：workspace_dir 本身可能就是共享区（内嵌方案），也可能有 workspace/ 子目录
    local_dir = workspace_dir / "workspace"
    if local_dir.exists():
        folders.append({
            "name": "📁 Shared Workspace",
            "path": str(local_dir),
        })
    elif workspace_dir.exists():
        # 工作区目录本身作为共享区（纯数据目录布局）
        scripts_dir = workspace_dir / "scripts"
        if scripts_dir.exists():
            folders.append({
                "name": "📁 Shared Workspace",
                "path": str(workspace_dir),
            })

    # 远程服务器
    for alias, s in sorted(servers.items()):
        user = s.get("user", "root")
        remote_path = "/root" if user == "root" else f"/home/{user}"
        folders.append({
            "name": alias,
            "uri": f"vscode-remote://ssh-remote+{alias}{remote_path}",
        })

    return folders


def build_settings(servers: dict, workspace_dir: Path) -> dict:
    """构建 VSCode settings，注入 AI context"""
    settings = {
        "remote.SSH.showLoginTerminal": True,
        "remote.SSH.connectTimeout": 10,
        "remote.SSH.maxReconnectionAttempts": 3,
        "terminal.integrated.defaultProfile.linux": "bash",
        "terminal.integrated.autoStart": True,
    }

    env_map = {}
    for alias, s in servers.items():
        env = s.get("environment", "unknown")
        if env not in env_map:
            env_map[env] = []
        env_map[env].append(alias)

    ai_context = {
        "ai_ssh_nodes.workspace_dir": str(workspace_dir),
        "ai_ssh_nodes.servers": {},
        "ai_ssh_nodes.environments": env_map,
        "ai_ssh_nodes.generated": datetime.now().isoformat(),
    }

    for alias, s in servers.items():
        ai_context["ai_ssh_nodes.servers"][alias] = {
            "host": f"{s.get('host')}:{s.get('port', 22)}",
            "os": s.get("os", ""),
            "type": s.get("type", ""),
            "role": s.get("role", ""),
            "environment": s.get("environment", ""),
            "permission": s.get("permission", "read_write"),
            "tags": s.get("tags", []),
        }

    settings.update(ai_context)
    return settings


def build_tasks(servers: dict) -> dict:
    """生成常用 VSCode tasks"""
    aliases = list(servers.keys())
    all_alias_cmd = " && ".join(f'ssh {a} "uptime && df -h && free -h"' for a in aliases)

    return {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Health Check (All Servers)",
                "type": "shell",
                "command": all_alias_cmd,
                "problemMatcher": [],
                "presentation": {"reveal": "always", "panel": "shared"},
            },
            {
                "label": "Disk Usage (All Servers)",
                "type": "shell",
                "command": " && ".join(f'ssh {a} "df -h"' for a in aliases),
                "problemMatcher": [],
            },
            {
                "label": "Memory Usage (All Servers)",
                "type": "shell",
                "command": " && ".join(f'ssh {a} "free -h"' for a in aliases),
                "problemMatcher": [],
            },
            {
                "label": "Docker Status (All Servers)",
                "type": "shell",
                "command": " && ".join(f'ssh {a} "docker ps 2>/dev/null || echo no docker"' for a in aliases),
                "problemMatcher": [],
            },
        ],
    }


# ── 主函数 ─────────────────────────────────────────────────────────────────────

def main():
    workspace_override = None
    auto_open = False

    args = sys.argv[1:]

    if "--open" in args:
        auto_open = True
        args.remove("--open")

    if "--workspace" in args:
        idx = args.index("--workspace")
        workspace_override = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    workspace_dir = resolve_workspace_dir(workspace_override)
    output_path = workspace_dir / "infra.code-workspace"

    if "--output" in args:
        idx = args.index("--output")
        output_path = Path(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    # 确保工作区目录存在
    workspace_dir.mkdir(parents=True, exist_ok=True)

    servers = read_servers(workspace_dir)
    folders = build_folders(servers, workspace_dir)
    settings = build_settings(servers, workspace_dir)
    tasks = build_tasks(servers)

    workspace_config = {
        "folders": folders,
        "settings": settings,
        "extensions": {
            "recommendations": [
                "ms-vscode-remote.remote-ssh",
                "ms-vscode-remote.remote-ssh-edit",
                "eamodio.gitlens",
            ]
        },
        "tasks": tasks,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(workspace_config, f, indent=2, ensure_ascii=False)

    local_count = sum(1 for f in folders if "path" in f)
    remote_count = sum(1 for f in folders if "uri" in f)

    print(f"✓ VSCode 工作区已生成")
    print(f"  文件: {output_path}")
    print(f"  工作区目录: {workspace_dir}")
    print()
    if local_count:
        print(f"  本地共享区: {local_count} 个")
    print(f"  远程服务器: {remote_count} 个")
    for f in folders:
        if "uri" in f:
            print(f"    ▸ {f['name']}")
    print()
    print(f"  AI Context: 已注入 (ai_ssh_nodes.workspace_dir = {workspace_dir})")
    print(f"  VSCode Tasks: {len(tasks['tasks'])} 个")

    if auto_open:
        import shutil
        code_cmd = shutil.which("code")
        if code_cmd:
            subprocess.run([code_cmd, str(output_path)])
            print(f"\n  已用 VSCode 打开")
        else:
            print(f"\n  未找到 code 命令，请手动打开:")
            print(f"    code \"{output_path}\"")
    else:
        print(f"\n  打开: code \"{output_path}\"")


if __name__ == "__main__":
    main()
