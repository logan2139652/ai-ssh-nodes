# Codex Installation Guide

Deploy the `ai-ssh-nodes` skill into Codex.

## Prerequisites

- Codex installed and running
- This repository cloned locally (`git clone`)

## Installation

### 1. Copy the Skill Folder

Copy the Codex skill folder into your Codex skills directory:

**Windows (PowerShell):**
```powershell
Copy-Item -Recurse .\skills\codex\ai-ssh-nodes "$env:USERPROFILE\.codex\skills\ai-ssh-nodes" -Force
```

**macOS / Linux:**
```bash
cp -r skills/codex/ai-ssh-nodes ~/.codex/skills/ai-ssh-nodes
```

### 2. Restart Codex

Quit Codex completely and relaunch it to load the new skill.

### 3. Verify

In Codex, type:

```
Use $ai-ssh-nodes to inspect my SSH node topology and sync SSH config safely.
```

If Codex recognizes and loads the skill, installation succeeded.

## What's Deployed

| File | Purpose |
|------|---------|
| `SKILL.md` | Codex-native skill definition with safety rules and full workflows |
| `agents/openai.yaml` | Codex Agent UI metadata (display name, default prompt) |

## FAQ

**Q: Skill isn't working?**
- Verify `~/.codex/skills/ai-ssh-nodes/SKILL.md` exists
- Confirm you fully quit and restarted Codex
- Check `SKILL.md` frontmatter formatting

**Q: How is this different from the WorkBuddy version?**
- `skills/codex/ai-ssh-nodes/` — thin wrapper customized for Codex
- Root `SKILL.md` — WorkBuddy version (Chinese operation guide)
- Both share the same scripts (`scripts/`) and config (`workspace/servers.yaml`)
