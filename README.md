<p align="center">
  <h1 align="center">ai-ssh-nodes</h1>
  <p align="center"><strong>AI-native infrastructure control plane</strong></p>
  <p align="center">One YAML file to manage all servers · AI understands your topology · Zero agent, zero daemon</p>
  <p align="center">Built-in <strong>WorkBuddy / Codex / Generic-Agent</strong> skill adapters</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="Platform">
</p>

---

> [中文文档](README.zh.md)

## What is this

You have a few remote servers — maybe a lab GPU workstation, a cloud dev VM, or production machines. Normally you open XShell, connect one by one, type commands, switch windows, repeat.

ai-ssh-nodes changes that:

- **Write one file** (`servers.yaml`) listing all servers — IP, port, user, role
- **Tell your AI** "check disk usage on all servers" — the AI SSHs in, runs commands, returns results
- **See all server files in one VSCode window** — like working with local folders

Core philosophy: **The agent runs on your host. Servers install nothing.** No remote agents, daemons, or playbooks. Your host controls all nodes over standard SSH. The AI understands the topology, executes commands, and orchestrates across machines.

Built-in skill adapters for **WorkBuddy**, **Codex**, and **generic AI agents** (Cursor, Claude Code, Copilot, Cline, etc.).

## Quick Start

```bash
# 1. Clone
git clone https://github.com/logan2139652/ai-ssh-nodes.git
cd ai-ssh-nodes

# 2. Create your config from template
cp workspace/servers.yaml.example workspace/servers.yaml

# 3. Edit servers.yaml with your servers
vim workspace/servers.yaml

# 4. Sync to ~/.ssh/config
python scripts/sync_ssh_config.py

# 5. Set up authentication — pick one

# Option A: Password login (no extra setup)
#   Leave identity_file unset in servers.yaml
#   → SSH will use password auth after sync
#   → Best for: quick start, few servers

# Option B: Key-based login (recommended for frequent use)
python scripts/setup_keys.py
#   → Enter each server's password once, public key is pushed automatically
#   → Best for: daily operations, AI agent automation

# 6. Tell your AI: "check disk usage on all servers"
```

## servers.yaml

```yaml
servers:
  dev-vm:
    host: 10.0.0.5            # [required]
    port: 22
    user: ubuntu
    role: local dev machine
    environment: development
    permission: read_write
    tags: [docker, dev]

  prod-db:
    host: 10.0.1.20           # [required]
    user: root
    role: production database
    environment: production
    permission: confirm_required
    tags: [postgres, critical]
```

### Field Reference

| Field | Required | Default | Description |
|------|:--:|--------|------|
| `host` | ✅ | — | Server IP or hostname |
| `port` | | `22` | SSH port |
| `user` | | `root` | Login user |
| `identity_file` | | `~/.ssh/id_ed25519` | SSH private key path |
| `role` | | — | Human-readable purpose |
| `environment` | | `development` | `development` / `staging` / `production` |
| `permission` | | `read_write` | `read_only` / `read_write` / `confirm_required` |
| `tags` | | `[]` | Tag list |

### Permission Model

| Permission | AI Behavior |
|------|---------|
| `read_only` | Execute any read-only operation directly |
| `read_write` | Execute read & write operations directly |
| `confirm_required` | **Mutating operations** require user confirmation first |

`environment: production` + `permission: confirm_required` = double protection.

## Project Structure

```
ai-ssh-nodes/
├── SKILL.md                          # AI skill definition (WorkBuddy)
├── README.md                         # This file (English)
├── README.zh.md                      # Chinese documentation
├── config.yaml                       # Custom workspace path (optional)
├── .gitignore
├── scripts/
│   ├── sync_ssh_config.py            # servers.yaml → ~/.ssh/config
│   ├── vscode_gen.py                 # servers.yaml → .code-workspace
│   └── setup_keys.py                 # Push public key for passwordless SSH
├── skills/
│   ├── README.md                     # Platform adapter overview
│   ├── workbuddy/SKILL.md            # WorkBuddy index → root SKILL.md
│   ├── codex/
│   │   ├── INSTALL.md                # Codex install guide (English)
│   │   ├── INSTALL.zh.md             # Codex install guide (Chinese)
│   │   └── ai-ssh-nodes/
│   │       ├── SKILL.md              # Codex-native skill
│   │       └── agents/openai.yaml    # Agent UI metadata
│   └── generic-agent/
│       └── SKILL.md                  # Generic prompt version
└── workspace/
    ├── servers.yaml.example          # Config template (your real config is .gitignored)
    ├── scripts/                      # Shared scripts
    ├── share/                        # Shared files
    └── transfers/                    # File transfer staging
```

## Scripts

### sync_ssh_config.py

Generates the ai-ssh-nodes managed block in `~/.ssh/config` from `servers.yaml`.

```bash
python scripts/sync_ssh_config.py              # Write
python scripts/sync_ssh_config.py --dry-run    # Preview
```

Uses `# >>> ai-ssh-nodes managed` / `# <<< ai-ssh-nodes managed` markers. Only the block between markers is managed; manual entries outside are untouched.

### vscode_gen.py

Generates a VSCode Multi-root `.code-workspace` file from `servers.yaml`.

```bash
python scripts/vscode_gen.py                    # Generate
python scripts/vscode_gen.py --workspace ~/my-infra  # Custom path
```

**⚠️ Important — correct open method:**

Do NOT open `infra.code-workspace` directly from a local window. Files will show as "unresolved." Instead:

1. Connect to any remote host first: `Ctrl+Shift+P → Remote-SSH: Connect to Host...`
2. From the connected remote window: `File → Open Workspace from File` → select `infra.code-workspace`
3. Expand each node → enter password → all directories appear

**To reload after workspace changes:**

```
Ctrl+Shift+P → File: Open Workspace from File → re-select infra.code-workspace
```

Generated workspace includes: local shared workspace, per-server remote folders, AI context injection, and preset VSCode Tasks (Health Check / Disk / Memory).

### setup_keys.py

One-shot passwordless SSH setup: connects to each server with a password, pushes your public key, and updates `servers.yaml`.

```bash
python scripts/setup_keys.py                      # Default ~/.ssh/id_ed25519.pub
python scripts/setup_keys.py --key ~/.ssh/id_ed25519.pub
```

## AI Agent Integration

The `skills/` directory contains platform-specific skill adapters:

| Platform | Path | How to use |
|----------|------|------------|
| **WorkBuddy** | `SKILL.md` (root) | Import via WorkBuddy sidebar |
| **Codex** | `skills/codex/ai-ssh-nodes/` | Copy to `~/.codex/skills/` — see install guides |
| **Generic** | `skills/generic-agent/SKILL.md` | Inject as system prompt or rules file |

All adapters share the same `workspace/servers.yaml` and `scripts/`. They differ only in how the AI is taught to use them.

### For Cursor / Claude Code / Copilot / Cline

Copy the core instruction block below into your project's rules file:

```text
You are the ai-ssh-nodes infrastructure control plane AI.

## Data
- Single source of truth: workspace/servers.yaml
- Read servers.yaml to understand all aliases, IPs, ports, users, environments, permissions
- Connect via SSH alias: ssh <alias> "command"

## Workflow
1. Read servers.yaml before operating on remote nodes
2. Parallelize independent commands across servers
3. File transfer: scp <file> <alias>:~/path/
4. After editing servers.yaml: python scripts/sync_ssh_config.py
5. VSCode workspace: python scripts/vscode_gen.py

## Safety
- production + confirm_required: confirm before mutation
- Forbidden: rm -rf /, dd if=, mkfs, shutdown/reboot, fork bombs, curl|bash (unreviewed)
- Report every action: ✓ server: command → result
```

## Why not traditional tools

| Traditional tool | Problem |
|----------|------|
| Ansible / Salt | Needs agent, write playbooks, steep learning curve |
| XShell / MobaXterm | GUI tools, not callable by AI |
| Manual ssh-config | Only connection info, no semantics (env/role/permission) |
| Kubernetes | Container orchestration, can't manage bare metal / VMs |

ai-ssh-nodes answer: **one YAML declares topology, AI executes directly.**

## Dependencies

- Python ≥ 3.8
- PyYAML (`pip install pyyaml`)
- paramiko (`pip install paramiko` — needed by setup_keys.py)
- OpenSSH client
- VSCode + Remote-SSH extension (`ms-vscode-remote.remote-ssh`)

## Tips

- **Keep the INFRA workspace open**: VSCode remembers connections; reopen restores all nodes
- **Parallel commands**: Tell your AI "run df -h on both servers" — it parallelizes automatically
- **Quick tasks**: `Ctrl+Shift+B` for VSCode Tasks — Health Check / Disk / Memory on all servers
- **Add a server**: Edit servers.yaml → `sync_ssh_config.py` → reload workspace — three steps
- **Password to key**: `python scripts/setup_keys.py` — enter each password once, zero friction after

## License

MIT © 2026
