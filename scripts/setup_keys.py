#!/usr/bin/env python3
"""
CtrlPlane — 一键免密配置

读取 servers.yaml，用密码连上每台服务器，推送公钥，
然后更新 servers.yaml 的 identity_file 字段并重新同步 SSH config。

用法:
  python scripts/setup_keys.py              # 使用默认 id_ed25519.pub
  python scripts/setup_keys.py --key ~/.ssh/id_ed25519.pub
"""

import sys
import getpass
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
WORKSPACE_DIR = SKILL_DIR / "workspace"
SERVERS_FILE = WORKSPACE_DIR / "servers.yaml"

try:
    import yaml
except ImportError:
    print("需要 PyYAML: pip install pyyaml")
    sys.exit(1)

try:
    import paramiko
except ImportError:
    print("需要 paramiko: pip install paramiko")
    sys.exit(1)


def push_key(host, port, user, password, pubkey, alias):
    """用 paramiko 连接服务器并推送公钥到 ~/.ssh/authorized_keys"""
    print(f"  ▸ {alias} ({user}@{host}:{port}) ... ", end="", flush=True)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, port=port, username=user, password=password,
                       timeout=10, look_for_keys=False, allow_agent=False)
    except paramiko.AuthenticationException:
        print("FAILED — 密码错误或认证失败")
        return False
    except Exception as e:
        print(f"FAILED — {e}")
        return False

    # 检查公钥是否已存在
    stdin, stdout, stderr = client.exec_command(
        "cat ~/.ssh/authorized_keys 2>/dev/null"
    )
    existing = stdout.read().decode()
    if pubkey.strip() in existing:
        print("SKIPPED — 已存在")
        client.close()
        return True

    # 推送公钥
    escaped_key = pubkey.strip().replace("'", "'\\''")
    cmd = (
        f"mkdir -p ~/.ssh && chmod 700 ~/.ssh && "
        f"echo '{escaped_key}' >> ~/.ssh/authorized_keys && "
        f"chmod 600 ~/.ssh/authorized_keys"
    )
    stdin, stdout, stderr = client.exec_command(cmd)
    err = stderr.read().decode().strip()
    exit_code = stdout.channel.recv_exit_status()
    client.close()

    if exit_code != 0:
        print(f"FAILED — {err if err else 'unknown error'}")
        return False

    print("OK")
    return True


def main():
    # 解析 --key 参数
    key_path = Path.home() / ".ssh" / "id_ed25519.pub"
    args = sys.argv[1:]
    if "--key" in args:
        idx = args.index("--key")
        key_path = Path(args[idx + 1]).expanduser()
        args = args[:idx] + args[idx + 2:]

    if not key_path.exists():
        print(f"✗ 公钥文件不存在: {key_path}")
        print("  请先生成密钥: ssh-keygen -t ed25519")
        sys.exit(1)

    if not SERVERS_FILE.exists():
        print(f"✗ 未找到 {SERVERS_FILE}")
        sys.exit(1)

    # 读取 servers.yaml
    with open(SERVERS_FILE, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    servers = config.get("servers", {})
    if not servers:
        print("✗ servers.yaml 中没有配置服务器")
        sys.exit(1)

    # 读取公钥
    with open(key_path, encoding="utf-8") as f:
        pubkey = f.read()

    print(f"\n{'='*50}")
    print(f"CtrlPlane — 一键免密配置")
    print(f"{'='*50}")
    print(f"  公钥: {key_path}")
    print(f"  服务器: {len(servers)} 台")
    print(f"  身份文件将设为: ~/.ssh/id_ed25519")
    print()

    # 逐台推送
    print("正在推送公钥（每台服务器分别输入密码）...\n")
    all_ok = True
    for alias, s in servers.items():
        host = s["host"]
        port = s.get("port", 22)
        user = s.get("user", "root")
        role = s.get("role", "")

        print(f"  [{alias}] {role} ({user}@{host}:{port})")
        password = getpass.getpass(f"  请输入密码: ")
        if not password:
            print("  SKIPPED — 密码为空\n")
            continue

        ok = push_key(host, port, user, password, pubkey, alias)
        if not ok:
            all_ok = False
        print()

    if not all_ok:
        print("\n部分服务器推送失败，请检查密码后重试。")
        sys.exit(1)

    # 更新 servers.yaml — 添加 identity_file
    print("\n更新 servers.yaml ...")
    for alias in servers:
        if "identity_file" not in servers[alias]:
            servers[alias]["identity_file"] = "~/.ssh/id_ed25519"

    with open(SERVERS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # 重新同步 SSH config
    print("同步 SSH config ...")
    import subprocess
    sync_script = SKILL_DIR / "scripts" / "sync_ssh_config.py"
    result = subprocess.run(
        [sys.executable, str(sync_script)],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    # 测试连接
    print("测试免密连接...")
    for alias in servers:
        test_result = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
             alias, "echo OK"],
            capture_output=True, text=True
        )
        if test_result.returncode == 0:
            print(f"  ✓ {alias} — 免密连接成功")
        else:
            print(f"  ✗ {alias} — 连接失败: {test_result.stderr.strip()}")

    print(f"\n{'='*50}")
    print("完成！现在可以免密连接了：")
    for alias in servers:
        print(f"  ssh {alias}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
