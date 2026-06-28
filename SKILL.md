---
name: ctrlplane
version: 3.0.0
description: "AI-native infrastructure control plane. Multi-server orchestration via SSH — register cloud/VM servers, batch execute commands, cross-server file transfer, generate VSCode remote workspaces. Triggers on: 服务器, 远程, 基础设施, 部署, 编排, 集群, 多台机器, 批量执行, 文件传输, 跨服务器, VSCode远程工作区, server, infrastructure, deploy, orchestrate, cluster, multi-node, remote exec, file transfer."
agent_created: true
keywords: infrastructure,server,deploy,orchestration,cluster,multi-node,SSH,remote,file-transfer,vscode,服务器,基础设施,远程,编排,集群,批量执行,传输,工作区
---

# CtrlPlane — AI 基础设施控制平面

## 核心理念

**你只需要一个文件：servers.yaml。**

不需要维护两份配置（SSH config + 服务器清单），不需要手动同步。servers.yaml 是单一数据源，~/.ssh/config 和 .code-workspace 都由它自动衍生。

```
用户编辑          AI 读取          自动衍生
─────────    ──────────────    ───────────────
                 ↓
servers.yaml  →  AI 理解拓扑  →  ssh <alias> 直接连接
                 ↓               vscode_gen.py 生成 .code-workspace
            sync_ssh_config   →  ~/.ssh/config
```

## 数据层

### 唯一配置文件

```
~/.workbuddy/skills/ctrlplane/
├── config.yaml              ← 自定义工作区路径（可选，默认内嵌）
└── workspace/               ← 默认内嵌工作区
    └── servers.yaml         ← ★ 唯一需要编辑的文件
```

**自定义路径**：编辑 config.yaml，设置 `workspace_dir`：

```yaml
workspace_dir: ~/my-infra
```

### servers.yaml 结构（完整版）

```yaml
servers:
  <alias>:                    # SSH 连接用的短名
    host: <ip>                # 必填
    port: <port>              # 默认 22
    user: <user>              # 默认 root
    identity_file: <path>     # 默认 ~/.ssh/id_ed25519
    role: <描述>               # 这台服务器是干什么的
    environment: development / staging / production
    permission: read_only / read_write / confirm_required
    tags: [tag1, tag2]        # 便于筛选
```

**这是唯一的配置入口。** 修改后运行一次 `sync_ssh_config.py` 即可。

## AI 标准工作流

### 场景 1：用户把服务器交给你管理

用户说"帮我看下服务器" / "帮我管理这些机器"

1. 读 `servers.yaml` 理解拓扑
2. 如果 servers.yaml 不存在 → 进入"首次设置"流程
3. 如果 servers.yaml 里没有服务器 → 问用户提供连接信息
4. 告诉用户当前的概貌（几台机器、各自环境、权限）

### 场景 2：添加新服务器

用户说"我还有一台 xxx 服务器"

1. 向用户确认：IP/端口/用户/用途/环境
2. 直接编辑 `servers.yaml`，追加新条目
3. 运行 `python scripts/sync_ssh_config.py` 同步 SSH config
4. 测试 `ssh <alias> "uname -a"`
5. 告诉用户添加成功

### 场景 3：执行远程操作

用户说"看下磁盘" / "更新系统" / "部署 xx"

```bash
# 读拓扑
cat ~/.workbuddy/skills/ctrlplane/workspace/servers.yaml

# 单台
ssh <alias> "df -h"

# 批量（多台独立命令 → 并行执行）
ssh <alias1> "df -h"
ssh <alias2> "free -h"
```

### 场景 4：文件传输

```bash
# 推送到服务器
scp <file> <alias>:~/path/

# 从服务器拉取
scp <alias>:/path/file workspace/transfers/

# 服务器间传输
ssh <A> "scp /file <B>:/path/"
```

### 场景 5：生成 VSCode 工作区

```bash
python scripts/vscode_gen.py --open
```

### 场景 6：同步 SSH config（servers.yaml 变更后）

```bash
python scripts/sync_ssh_config.py
```

## 首次设置（无 servers.yaml 时）

用户说"帮我管理服务器"但 servers.yaml 不存在：

1. **问用户要信息**：每台服务器的别名、IP、端口、用户、用途、环境
2. **创建 servers.yaml**：写入 workspace/servers.yaml
3. **同步 SSH config**：`python scripts/sync_ssh_config.py`
4. **确认 VSCode 扩展**：检查是否已安装 Remote-SSH（`ms-vscode-remote.remote-ssh`），未安装则引导安装
5. **测试连接**：逐台 `ssh <alias> "uname -a"` 或通过 VSCode Remote-SSH 连接
6. **展示概貌**：告诉用户他的基础设施全貌
7. **认证方式**：
   - 密码登录：不设 identity_file，连接时输入密码（适合新手，更直观）
   - 密钥免密：`identity_file: ~/.ssh/id_rsa` + 推送公钥到服务器（适合高频使用）

## 安全规则

1. **生产环境谨慎**：`environment: production` + `permission: confirm_required` → 修改性操作前必须确认
2. **先读后做**：操作前先读 servers.yaml
3. **禁止命令**：`rm -rf /`、`dd if=`、`mkfs` 等绝不执行
4. **操作透明**：
   ```
   ✓ mininet-vm: df -h → 磁盘使用 45%
   ✗ huawei-ecs: apt update → 连接超时
   ```
5. **生产环境确认模板**：
   ```
   即将在 huawei-ecs (production) 上执行: apt upgrade -y
   此操作属于生产环境修改性操作，请确认。
   ```

## 效率 Tips

- **免密登录**（首次）：`ssh-keygen -t ed25519 && ssh-copy-id user@host`
- **连接复用**（提速 3-5x）：在 ~/.ssh/config 顶部加 ControlMaster auto
- **防断连**：ServerAliveInterval 60（sync_ssh_config.py 已自动写入）
- **VSCode 断连**：`Ctrl+Shift+P` → Kill VS Code Server → 重连

## 依赖

- Python 3.8+（sync_ssh_config.py / vscode_gen.py 需要）
- PyYAML（`pip install pyyaml`）
- OpenSSH client
- VSCode + **Remote - SSH 扩展**（微软官方，ID: `ms-vscode-remote.remote-ssh`）

### VSCode Remote-SSH 前置步骤

**必须先安装扩展**，否则无法通过 VSCode 连接远程服务器：

1. 打开 VSCode → `Ctrl+Shift+X`（扩展面板）
2. 搜索 **"Remote - SSH"**（作者：Microsoft）
3. 点击 **安装**
4. 安装完成后，左侧活动栏会出现 **「显示器+插头」** 图标

### 连接行为说明

VSCode Remote-SSH 的连接机制：

| 行为 | 说明 |
|------|------|
| **逐台连接** | 默认每台服务器打开独立窗口（简单直接） |
| **Multi-root 工作区** | 一个窗口内管理多台服务器 + 本地文件（推荐） |

**Multi-root 工作区使用方法（推荐）：**

```bash
# 1. 生成工作区文件
python scripts/vscode_gen.py

# 2. 关键步骤：先单独连一次任意节点（让 VSCode 初始化 SSH 状态）
#    Ctrl+Shift+P → Remote-SSH: Connect to Host... → 选 dell-node4 → 输入密码

# 3. 在已连接的远端窗口中，打开工作区文件
#    File → Open Workspace from File → 选择 workspace/infra.code-workspace

# 4. 现在资源管理器里同时显示：
#    - Shared Workspace（本地）
#    - dell-node4（远端 /home/jkw/）
#    - dell-node8（远端 /home/jkw/）
```

⚠️ **注意**：如果直接在本地窗口打开 `.code-workspace`，远端节点可能显示为「无法解析」或连不上。必须先通过 Remote-SSH 连过一次，再加载工作区。
