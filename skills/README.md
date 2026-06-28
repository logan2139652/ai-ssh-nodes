# Skills

This directory collects agent-specific skill adapters for `ai-ssh-nodes`.

## Layout

```text
skills/
├─ workbuddy/
│  └─ SKILL.md
├─ codex/
│  └─ ai-ssh-nodes/
│     ├─ SKILL.md
│     └─ agents/openai.yaml
└─ generic-agent/
   └─ SKILL.md
```

## Which One To Use

- `skills/workbuddy/SKILL.md`: WorkBuddy-compatible skill. The repository root `SKILL.md` is kept as a compatibility copy.
- `skills/codex/ai-ssh-nodes/`: Codex-native skill folder with strict Codex frontmatter and UI metadata.
- `skills/generic-agent/SKILL.md`: compact prompt-style instructions for tools that support custom rules but not Codex/WorkBuddy skill packaging.

## Codex Install

Copy the Codex skill folder into your Codex skills directory:

```powershell
Copy-Item -Recurse .\skills\codex\ai-ssh-nodes "$env:USERPROFILE\.codex\skills\ai-ssh-nodes" -Force
```

Restart Codex, then ask:

```text
Use $ai-ssh-nodes to inspect my SSH node topology and sync SSH config safely.
```

See `skills/codex/INSTALL.md` or `skills/codex/INSTALL.zh.md` for detailed Codex installation instructions.
