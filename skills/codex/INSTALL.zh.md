# Codex 安装指南

将 `ai-ssh-nodes` Skill 部署到 Codex 中。

## 前提条件

- Codex 已安装并正常运行
- 已通过 `git clone` 获取本仓库到本地

## 安装步骤

### 1. 复制 Skill 文件夹

将 Codex 版本的 Skill 复制到 Codex 技能目录：

**Windows（PowerShell）：**
```powershell
Copy-Item -Recurse .\skills\codex\ai-ssh-nodes "$env:USERPROFILE\.codex\skills\ai-ssh-nodes" -Force
```

**macOS / Linux：**
```bash
cp -r skills/codex/ai-ssh-nodes ~/.codex/skills/ai-ssh-nodes
```

### 2. 重启 Codex

完全退出并重新启动 Codex，让新 Skill 生效。

### 3. 验证安装

在 Codex 中输入：

```
Use $ai-ssh-nodes to inspect my SSH node topology and sync SSH config safely.
```

如果 Codex 识别并加载了 Skill，说明安装成功。

## 文件说明

部署到 Codex 的 Skill 包含：

| 文件 | 说明 |
|------|------|
| `SKILL.md` | Codex 原生技能定义，含安全规则和完整工作流 |
| `agents/openai.yaml` | Codex Agent UI 元数据（显示名称、默认提示） |

## 常见问题

**Q: Skill 不生效？**
- 确认路径正确：`~/.codex/skills/ai-ssh-nodes/SKILL.md` 必须存在
- 确认已完全退出 Codex 后重新启动
- 检查 `SKILL.md` 的 frontmatter 格式是否正确

**Q: 和 WorkBuddy 版本有什么区别？**
- `skills/codex/ai-ssh-nodes/` — 专为 Codex 定制的薄包装
- 根目录 `SKILL.md` — WorkBuddy 版本（含中文操作指南）
- 两者共享同一套脚本（`scripts/`）和配置（`workspace/servers.yaml`）
