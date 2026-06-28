# ai-ssh-nodes Generic Agent Skill

You are operating the `ai-ssh-nodes` infrastructure control plane.

## Source Of Truth

- Repository root: the directory containing `README.md`, `SKILL.md`, `workspace/`, and `scripts/`.
- Server topology: `workspace/servers.yaml`.
- SSH config is generated from `workspace/servers.yaml` with:
  `python scripts/sync_ssh_config.py`
- VSCode Remote-SSH workspace is generated with:
  `python scripts/vscode_gen.py`
- Key setup helper:
  `python scripts/setup_keys.py`

## Workflow

1. Locate the repository root.
2. Read `workspace/servers.yaml` before operating on remote nodes.
3. If `workspace/servers.yaml` is missing, ask the user for server alias, host, port, user, role, environment, permission, tags, and optional identity file.
4. After editing `workspace/servers.yaml`, run `python scripts/sync_ssh_config.py --dry-run` first when the change affects SSH config.
5. Run `python scripts/sync_ssh_config.py` after the user accepts the generated SSH config.
6. Test aliases with bounded commands:
   `ssh -o BatchMode=yes -o ConnectTimeout=10 <alias> "hostname; whoami; pwd"`
7. For VSCode Remote-SSH usage, run `python scripts/vscode_gen.py`.

## Safety Rules

- Never ask users to paste passwords, private keys, tokens, `.env` values, kubeconfigs, or cloud credentials into chat.
- Do not read private key files or sensitive config values unless explicitly approved.
- Use bounded SSH commands rather than persistent interactive shells.
- For `environment: production` or `permission: confirm_required`, ask for confirmation before mutation.
- Ask before installing packages, editing remote files, restarting services, deleting files, or transferring sensitive files.
- Report every remote action with alias, command, and result summary.

## Common Commands

```bash
python scripts/sync_ssh_config.py --dry-run
python scripts/sync_ssh_config.py
python scripts/vscode_gen.py
ssh <alias> "df -h"
ssh <alias> "free -h"
scp <file> <alias>:~/path/
scp <alias>:/path/file workspace/transfers/
```
