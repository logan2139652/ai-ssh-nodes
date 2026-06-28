<p align="center">
  <h1 align="center">CtrlPlane</h1>
  <p align="center"><strong>AI-native infrastructure control plane</strong></p>
  <p align="center">一个 YAML 文件管理所有服务器 · AI 原生理解拓扑 · 零 Agent/零 Daemon</p>
  <p align="center">内嵌 <strong>WorkBuddy Skill</strong>，开箱即用 · 可适配 <strong>Cursor / Claude Code / Copilot</strong> 等主流 AI 工具</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="Platform">
</p>

---

## 这是什么

想象你有几台远程服务器——可能是实验室的 GPU 工作站、云上的开发机、或者公司的生产环境。平常你需要打开 XShell 一台台连上去，敲命令，切窗口，来回折腾。

CtrlPlane 让这件事变得简单：

- **写一个文件**（`servers.yaml`），列出所有服务器的 IP、端口、用户名
- **告诉 AI**「帮我看下所有服务器的磁盘使用」—— AI 通过 SSH 直接连上去执行，返回结果
- **在 VSCode 一个窗口里看到所有服务器的文件**，像操作本地文件夹一样

核心理念：**Agent 装在你的主机上，服务器不需要装任何东西。** 不需要在远端部署 agent、daemon、playbook。你的主机通过标准 SSH 协议控制所有节点，AI 作为操作层理解拓扑、执行命令、联动多台机器。

**内置 WorkBuddy Skill（`SKILL.md`）**，安装即用；同时提供核心指令模板，可快速适配 Cursor、Claude Code、GitHub Copilot、Cline 等主流 AI 工具。

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

# 5. 配置认证——二选一

# 方案 A：密码登录（无需额外配置）
#   编辑 servers.yaml 时不设 identity_file 即可
#   → sync 后 SSH 会自动走密码认证
#   → 适合: 快速上手、少量服务器

# 方案 B：密钥免密登录（推荐高频使用）
python scripts/setup_keys.py
#   → 逐台输入密码，自动推送公钥，后续无需重复输入
#   → 适合: 日常频繁操作、AI Agent 自动化

# 6. 对 AI 说：「帮我看下所有服务器的磁盘使用情况」
```

### 首次使用 VSCode Remote-SSH（推荐）

如果要通过 VSCode 图形化操作远程服务器，需要额外配置：

```bash
# 1. 安装 VSCode 扩展（必装）
#    打开 VSCode → Ctrl+Shift+X → 搜索 "Remote - SSH"（作者: Microsoft）→ 安装

# 2. 生成 Multi-root 工作区
python scripts/vscode_gen.py

# 3. 打开工作区——关键步骤：不能直接打开！
#    a) Ctrl+Shift+P → Remote-SSH: Connect to Host... → 选择任意节点 → 输入密码
#    b) 在已连接的远端窗口中: File → Open Workspace from File → 选 workspace/infra.code-workspace
#    c) 资源管理器里现在同时显示所有节点的文件

# 4. 重新加载（工作区文件变更后）
#    Ctrl+Shift+P → File: Open Workspace from File → 重新选 infra.code-workspace
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
│   ├── vscode_gen.py                 # servers.yaml → .code-workspace
│   └── setup_keys.py                 # 一键推送公钥，配置免密登录
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
python scripts/vscode_gen.py                 # 生成工作区文件
python scripts/vscode_gen.py --open           # 生成并打开（不推荐直接 --open）
python scripts/vscode_gen.py --workspace ~/my-infra  # 指定路径
```

**⚠️ 正确打开方式（重要）：**

不要直接打开 `infra.code-workspace`，会显示「无法解析工作区文件夹」。必须：

1. 先通过 Remote-SSH 连接一次任意节点（`Ctrl+Shift+P → Remote-SSH: Connect to Host...`）
2. 在已连接的远端窗口中：`File → Open Workspace from File` → 选择 `infra.code-workspace`
3. 连接后逐台展开节点 → 输入密码 → 全部目录出现

**工作区文件变更后如何刷新：**

VSCode 不会自动检测 `.code-workspace` 文件变更。需手动重载：

```
Ctrl+Shift+P → File: Open Workspace from File → 重新选 infra.code-workspace
```

生成的 workspace 包含：
- 本地 `📁 Shared Workspace`（scripts/share/transfers）
- 每台服务器的远程目录（Remote-SSH）
- AI Context 注入（settings 中嵌入服务器元数据）
- 预置 VSCode Tasks（Health Check / Disk / Memory / Docker）

### setup_keys.py

一键免密配置：用密码连上每台服务器，自动推送公钥，更新配置。

```bash
python scripts/setup_keys.py              # 使用默认 ~/.ssh/id_rsa.pub
python scripts/setup_keys.py --key ~/.ssh/id_ed25519.pub  # 指定密钥
```

**工作流程：**

1. 读取 `servers.yaml` 中所有服务器
2. **逐台提示输入密码**（每台可不同）
3. 用 paramiko 连接，推送公钥到 `~/.ssh/authorized_keys`
4. 自动在 `servers.yaml` 中添加 `identity_file` 字段
5. 重新同步 `~/.ssh/config`
6. 自动测试免密连接是否成功

## SKILL.md — AI 操作指令

CtrlPlane 的核心不只是脚本，更重要的是让 AI 理解你的基础设施拓扑并直接操作。

仓库中的 `SKILL.md` 是为 **WorkBuddy**（[workbuddy.cn](https://www.codebuddy.cn)）编写的 Skill 文件。WorkBuddy 会自动加载 `SKILL.md` 的内容作为 AI 的系统指令，使其理解 `servers.yaml` 的语义和操作规范。

### 安装到 WorkBuddy

```bash
# 克隆到的任意目录，例如:
git clone https://github.com/logan2139652/ai-ssh-nodes.git D:/Office_Tools/ctrlplane

# 在 WorkBuddy 中导入 Skill:
#  左侧栏 → 专家 → 导入 Skill → 选择 SKILL.md
```

安装后对着 WorkBuddy 说「帮我看下所有服务器的磁盘」即可。

### 适配其他 AI Agent

`SKILL.md` 的语义与 `servers.yaml` 的结构、Python 脚本的使用方式完全通用。只需将核心指令以各工具的格式注入即可。

| 工具 | 适配方式 | 操作 |
|------|----------|------|
| **WorkBuddy** | `SKILL.md` | 已内置，直接导入 |
| **Cursor** | `.cursorrules` | 将核心指令写入项目根目录 `.cursorrules` |
| **Claude Code** | `CLAUDE.md` | 写入项目根目录 `CLAUDE.md` |
| **GitHub Copilot** | `.github/copilot-instructions.md` | 写入 `copilot-instructions.md` |
| **Cline / Roo Code** | `.clinerules` | 写入 `.clinerules` |
| **通用终端 Agent** | system prompt | 直接注入核心指令 |

**核心指令模板（适用于所有 Agent）：**

```
你是 CtrlPlane 基础设施控制面 AI。你的行为规范：

## 数据层
- 唯一配置: workspace/servers.yaml
- 读取 servers.yaml 理解所有服务器的别名、IP、端口、用户、环境、权限
- 通过服务器的 alias 直接 SSH 连接: ssh <alias> "命令"

## 操作规范
1. 操作前先读 servers.yaml 理解拓扑
2. 批量操作多台服务器时，并行执行独立命令
3. 文件传输使用 scp: scp <file> <alias>:~/path/
4. servers.yaml 变更后运行: python scripts/sync_ssh_config.py
5. 生成 VSCode 工作区: python scripts/vscode_gen.py

## 安全规则
- production + confirm_required: 修改性操作前必须确认
- 禁止命令: rm -rf /, dd if=, mkfs, shutdown/reboot, fdisk, chmod -R 777 /, iptables -F(生产), fork bomb, curl|bash(未审查)
- 操作结果透明汇报: ✓ server: command → 结果

## 首次设置（无 servers.yaml 时）
- 向用户收集服务器信息 → 创建 workspace/servers.yaml → sync → 测试连接
```

`servers.yaml` 结构和三个 Python 脚本对任何 Agent 都是透明的——数据格式不变，脚本用法不变，变的只是 AI 如何被"教会"使用它们。

## 依赖

- Python ≥ 3.8
- PyYAML (`pip install pyyaml`)
- paramiko (`pip install paramiko` — setup_keys.py 需要)
- OpenSSH client
- VSCode + Remote-SSH 扩展 (`ms-vscode-remote.remote-ssh`)

## 效率 Tips

- **别关 INFRA 工作区**：VSCode 会记住连接状态，下次打开直接恢复所有节点
- **多台并行**：对 AI 说「在两台上同时跑 df -h」，命令会自动并行执行
- **快捷任务**：`Ctrl+Shift+B` 打开 VSCode Tasks，一键 Health Check / Disk / Memory 所有服务器
- **新增服务器**：编辑 servers.yaml → `python scripts/sync_ssh_config.py` → 重载工作区，三步完成
- **密码变免密**：`python scripts/setup_keys.py`，逐台输一次密码，之后零摩擦

## License

MIT © 2026
