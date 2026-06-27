---
name: vibe-coding-inspiration
description: Use when finding vibe coding, open-source, product, or indie hacking inspiration from public growth signals. Helps collect fast-growing projects, normalize signals, generate Chinese summaries, explain why a trend is growing, and turn findings into actionable opportunity angles. Trigger on requests like finding vibe coding inspiration, analyzing fast-growing GitHub projects, generating a Chinese vibe coding inspiration report, or exploring product ideas from GitHub/Product Hunt/Hacker News trends.
---

# vibe coding inspiration

Use this skill to turn public growth signals into Chinese inspiration reports and actionable product ideas.

## Current Source

The first implemented source is GitHub Trending weekly.

Run the bundled scripts from the skill directory:

```powershell
python .\scripts\github_fast_growing_web_repos.py --out-dir . --limit 50 --metadata-source html
python .\scripts\build_github_growth_html.py --input .\github_fast_growing_web_repos.json --zh-summaries .\assets\github_growth_radar_zh_summaries.json --output .\vibe-coding-inspiration.html
```

## Workflow

1. Fetch growth data from the selected source.
2. Keep original names and links.
3. Normalize metrics into growth and usage signals.
4. Write concise Chinese summaries for Chinese readers.
5. Explain why the item may be growing now.
6. Extract opportunity angles such as Chinese version, vertical niche, plugin version, workflow template, or simpler MVP.
7. Generate HTML, Markdown, JSON, or CSV outputs as requested.

## Interpretation Heuristics

- Growth signal shows recent attention, not necessarily durable demand.
- Usage signal helps distinguish hype from real adoption.
- Issues and discussions often reveal missing features and pain points.
- Forks suggest reuse, integration, or self-hosting interest.
- The best inspiration is usually not to copy the project, but to identify a narrower audience or simpler workflow.

## Output Style

For Chinese users, prefer:

- Chinese summaries
- plain explanations of who needs it and why
- short opportunity angles
- links to original projects
- metrics preserved as evidence

Keep project names unchanged.
