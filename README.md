# vibe coding inspiration

A Codex Skill for finding vibe coding inspiration from fast-growing open-source projects.

## What This Skill Helps You Do

This skill helps Codex:

- find fast-growing GitHub projects
- turn trend signals into Chinese inspiration summaries
- explain why a project may be getting attention
- identify useful product, plugin, workflow, or niche ideas
- generate a local HTML inspiration report you can browse

It is useful when you want to discover what developers are paying attention to and turn that into ideas for vibe coding projects.

## Install

Clone this repository into your Codex skills directory.

macOS / Linux:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/hahadu4520/vibe-coding-inspiration.git ~/.codex/skills/vibe-coding-inspiration
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
git clone https://github.com/hahadu4520/vibe-coding-inspiration.git "$env:USERPROFILE\.codex\skills\vibe-coding-inspiration"
```

Restart Codex after installing.

## How To Use

Ask Codex things like:

```text
Use vibe coding inspiration to find this week's project ideas.
```

```text
帮我找最近适合做的 vibe coding 项目灵感。
```

```text
生成一份中文 vibe coding inspiration 报告。
```

```text
分析本周增长最快的 GitHub 项目，看看有哪些值得做成小工具、插件或垂直版本。
```

Codex will use the skill to gather signals, summarize the projects, and produce an inspiration report.

## Best For

- indie hackers looking for project ideas
- developers looking for useful tool ideas
- creators tracking open-source trends
- people who want Chinese summaries of fast-moving GitHub projects

## License

MIT
