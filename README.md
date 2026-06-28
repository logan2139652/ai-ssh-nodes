<p align="center">
  <h1 align="center">CtrlPlane</h1>
  <p align="center"><strong>AI-native infrastructure control plane</strong></p>
  <p align="center">一个 YAML 文件管理所有服务器 · AI 原生理解拓扑 · 零 Agent/零 Daemon</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="Platform">
</p>

---

## 这是什么

CtrlPlane 是一套 AI 驱动的基础设施管理方案。编辑 `servers.yaml` 这一个文件声明你的服务器拓扑，AI（以及配套脚本）自动搞定 SSH 连接、批量执行、VSCode 远程工作区。

**不是又一个 SSH 客户端。** CtrlPlane 是为 AI 设计的——你的大模型助手读 `servers.yaml` 就能理解整个基础设施拓扑，直接 `ssh`/`scp` 操作，不需要 CLI 包装层。

## 为什么不用传统工具

| 传统工具 | 问题 |
|----------|------|
| Ansible / Salt | 需要 agent，写 playbook，学习曲线陡 |
| XShell / MobaXterm | GUI 工具，无法被 AI 调用 |
| ssh-config 手动管理 | 只有连接信息，没有语义（环境/角色/权限） |
| Kubernetes | 容器编排，管不了裸机/VM |

CtrlPlane 的答案：**一个 YAML 文件声明拓扑，AI 直接执行。**

## 快速开始

```bash
# 1. 克隆
git clone https://github.com/logan2139652/ai-ssh-nodes.git
cd ai-ssh-nodes

# 2. 复制配置模板
cp workspace/servers.yaml.example workspace/servers.yaml

# 3. 编辑 servers.yaml，填入你的服务器
vim workspace/servers.yaml

# 4. 同步到 ~/.ssh/config
python scripts/sync_ssh_config.py

# 5. （可选）生成 VSCode 远程工作区
python scripts/vscode_gen.py --open

# 6. 对 AI 说：「帮我看下所有服务器的磁盘使用情况」
```

## servers.yaml — 唯一配置

```yaml
servers:
  dev-vm:
    host: 10.0.0.5            # [必填]
    port: 22
    user: ubuntu
    role: 本地开发机
    environment: development
    permission: read_write
    tags: [docker, dev]

  prod-db:
    host: 10.0.1.20           # [必填]
    user: root
    role: 生产数据库
    environment: production
    permission: confirm_required
    tags: [postgres, critical]
```

### 字段说明

| 字段 | 必填 | 默认值 | 说明 |
|------|:--:|--------|------|
| `host` | ✅ | — | 服务器 IP 或域名 |
| `port` | | `22` | SSH 端口 |
| `user` | | `root` | 登录用户名 |
| `identity_file` | | `~/.ssh/id_ed25519` | SSH 私钥路径 |
| `role` | | — | 服务器用途描述 |
| `environment` | | `development` | `development` / `staging` / `production` |
| `permission` | | `read_write` | `read_only` / `read_write` / `confirm_required` |
| `tags` | | `[]` | 标签列表 |

### 权限模型

| 权限 | AI 行为 |
|------|---------|
| `read_only` | 直接执行任何只读操作 |
| `read_write` | 直接执行读写操作 |
| `confirm_required` | **修改性操作**必须先经用户确认 |

`environment: production` + `permission: confirm_required` = 双重保护。

## 目录结构

```
ctrlplane/
├── SKILL.md                          # AI 操作手册（WorkBuddy Skill）
├── README.md                         # 本文件
├── config.yaml                       # 自定义工作区路径（可选）
├── .gitignore                        # 排除 servers.yaml / 生成产物
├── scripts/
│   ├── sync_ssh_config.py            # servers.yaml → ~/.ssh/config
│   └── vscode_gen.py                 # servers.yaml → .code-workspace
└── workspace/
    ├── servers.yaml.example          # 配置模板（你的真实配置不提交）
    ├── scripts/                      # 共享脚本
    ├── share/                        # 共享文件
    └── transfers/                    # 文件传输中转
```

## 配套脚本

### sync_ssh_config.py

从 servers.yaml 自动生成 `~/.ssh/config` 中的 CtrlPlane 管理区块。

```bash
python scripts/sync_ssh_config.py          # 写入
python scripts/sync_ssh_config.py --dry-run # 预览
```

**工作原理**：使用 `# >>> CtrlPlane managed` / `# <<< CtrlPlane managed` 标记区块，区块内由脚本自动管理，区块外的手动配置不受影响。

### vscode_gen.py

从 servers.yaml 生成 VSCode Multi-root `.code-workspace` 文件。

```bash
python scripts/vscode_gen.py --open            # 生成并打开
python scripts/vscode_gen.py --workspace ~/my-infra  # 指定路径
```

生成的 workspace 包含：
- 本地 `📁 Shared Workspace`（scripts/share/transfers）
- 每台服务器的远程目录（Remote-SSH）
- AI Context 注入（settings 中嵌入服务器元数据）
- 预置 VSCode Tasks（Health Check / Disk / Memory / Docker）

## AI 如何工作

CtrlPlane 的核心设计理念：**AI 就是操作层，不需要 CLI。**

```
用户编辑 → AI 读取 → 直接执行
─────────  ──────────  ──────────
servers.yaml →  AI 理解拓扑 →  ssh <alias> "df -h"
                               scp file <alias>:/path
                               并行批量操作
```

AI 看到 `servers.yaml` 就知道：
- 有几台服务器、各是什么环境
- 哪些是生产环境需要谨慎操作
- 对 `confirm_required` 的服务器，修改性操作前会自动请求用户确认

## 依赖

- Python ≥ 3.8
- PyYAML (`pip install pyyaml`)
- OpenSSH client
- VSCode + Remote-SSH 扩展（可选）

## 效率 Tips

```bash
# SSH 免密登录
ssh-keygen -t ed25519 -C "ctrlplane"
ssh-copy-id -i ~/.ssh/id_ed25519 user@host

# SSH 连接复用（大幅提速）
cat >> ~/.ssh/config << 'EOF'
Host *
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 600
    ServerAliveInterval 60
EOF
```

## License

MIT © 2026
