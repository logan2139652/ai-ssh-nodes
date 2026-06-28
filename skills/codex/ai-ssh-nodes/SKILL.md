---
name: ai-ssh-nodes
description: Use the ai-ssh-nodes repository from Codex to manage SSH node topology through a single workspace/servers.yaml file. Trigger when the user asks to configure SSH nodes, inspect or operate multiple remote servers, sync ~/.ssh/config from servers.yaml, generate VSCode Remote-SSH workspaces, set up SSH keys, run bounded commands across aliases, transfer files between nodes, or adapt ai-ssh-nodes for Codex.
---

# AI SSH Nodes For Codex

## Overview

Use this skill to operate a local clone of `ai-ssh-nodes` from Codex. The repository's source of truth is `workspace/servers.yaml`; the generated artifacts are `~/.ssh/config` and `workspace/infra.code-workspace`.

The root `SKILL.md` is intended for WorkBuddy and other generic agents. This Codex skill is a thin wrapper that teaches Codex how to use the repository safely and where the project scripts live.

## Locate The Repository

Before acting, find the `ai-ssh-nodes` repository root. Prefer the current workspace or a user-provided path. The root should contain:

```text
SKILL.md
README.md
config.yaml
workspace/servers.yaml.example
scripts/sync_ssh_config.py
scripts/vscode_gen.py
scripts/setup_keys.py
```

If multiple copies exist, ask which one to use.

## Safety Rules

- Read `workspace/servers.yaml` before remote work.
- Never print private key contents, passwords, tokens, `.env` values, kubeconfigs, or cloud credentials.
- Do not ask users to paste passwords or private keys into chat.
- Prefer SSH aliases from `servers.yaml` after running `scripts/sync_ssh_config.py`.
- Use bounded SSH commands with `BatchMode=yes`, `ConnectTimeout`, `head`, line ranges, or grep limits.
- For `environment: production` or `permission: confirm_required`, ask for explicit confirmation before mutation.
- Ask before installing packages, editing remote files, restarting services, deleting files, or copying sensitive files.
- Treat persistent interactive `ssh <alias>` shells as a user-terminal action. Codex should run bounded commands and show output.

## First-Time Setup

1. Check local tools.
   - Use `ssh -V`.
   - Use `scp` for transfer availability.
   - `rsync` is optional.

2. Create `workspace/servers.yaml` if missing.
   - Copy from `workspace/servers.yaml.example`.
   - Ask for required server fields:
     - alias
     - host
     - port, default `22`
     - user, default `root`
     - identity_file, optional
     - role
     - environment: `development`, `staging`, or `production`
     - permission: `read_only`, `read_write`, or `confirm_required`
     - tags

3. Sync SSH config.
   - Run:
     `python scripts/sync_ssh_config.py`
   - Preview first when risk is unclear:
     `python scripts/sync_ssh_config.py --dry-run`

4. Test connections.
   - Use bounded commands:
     `ssh -o BatchMode=yes -o ConnectTimeout=10 <alias> "hostname; whoami; pwd"`
   - If password login is expected, explain that Codex may not handle interactive prompts reliably and recommend key setup.

5. Optionally generate VSCode workspace.
   - Run:
     `python scripts/vscode_gen.py`
   - Tell the user to open `workspace/infra.code-workspace` through VSCode Remote-SSH after connecting to at least one host once.

## Routine Workflows

### Inspect All Nodes

1. Read `workspace/servers.yaml`.
2. Summarize aliases, roles, environments, permissions, and tags.
3. Run read-only checks as requested:
   `ssh <alias> "uptime; df -h; free -h"`

Parallelize independent node checks when useful, but keep output bounded.

### Add A Node

1. Ask for the node fields.
2. Edit `workspace/servers.yaml`.
3. Run `python scripts/sync_ssh_config.py --dry-run`.
4. If the generated SSH block is correct, run `python scripts/sync_ssh_config.py`.
5. Test `ssh <alias> "hostname; whoami; pwd"`.

### Set Up Key Login

Use `scripts/setup_keys.py` only when the user explicitly asks for key setup and understands it may prompt for remote passwords in the terminal. Do not ask the user to paste those passwords into chat.

### Transfer Files

Prefer a local relay unless direct source-to-target SSH is intentionally configured:

1. Pull from source:
   `scp <source>:/path/file workspace/transfers/`
2. Inspect filenames and avoid secrets unless approved.
3. Push to target:
   `scp workspace/transfers/file <target>:/path/file`
4. Verify size, checksum, owner, permissions, or service behavior.

### Mutating Remote Commands

For production or `confirm_required`, present:

- target alias
- environment and permission
- exact command
- rollback or backup plan when relevant
- verification command

Wait for user confirmation before running the command.

## Repository Scripts

- `scripts/sync_ssh_config.py`: generate the managed `ai-ssh-nodes` block in `~/.ssh/config` from `workspace/servers.yaml`.
- `scripts/vscode_gen.py`: generate `workspace/infra.code-workspace` for VSCode Remote-SSH multi-root use.
- `scripts/setup_keys.py`: push a local public key to nodes using password authentication, then update `servers.yaml`.

## Example Requests

- "Use $ai-ssh-nodes to inspect my configured servers."
- "Use $ai-ssh-nodes to add a new Huawei ECS node."
- "Use $ai-ssh-nodes to sync SSH config and test all aliases."
- "Use $ai-ssh-nodes to generate the VSCode Remote workspace."
- "Use $ai-ssh-nodes to copy this config from one node to another after showing me the plan."
