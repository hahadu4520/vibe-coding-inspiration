# vibe coding inspiration

A Codex Skill for finding vibe coding inspiration from fast-growing public projects.

This skill helps Codex discover fast-growing GitHub projects, turn them into a Chinese inspiration report, and explain what product or workflow ideas they may suggest.

## What It Does

- Finds fast-growing repositories from GitHub Trending weekly
- Uses weekly star growth as the main momentum signal
- Adds usage signals such as open issues, forks, and total stars
- Keeps original GitHub project names and links
- Generates Chinese summaries for Chinese readers
- Builds a local HTML report called `vibe-coding-inspiration.html`
- Outputs JSON, CSV, and Markdown data for further analysis

## Install

Clone this repository into your Codex skills directory.

On macOS or Linux:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/hahadu4520/vibe-coding-inspiration.git ~/.codex/skills/vibe-coding-inspiration
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
git clone https://github.com/hahadu4520/vibe-coding-inspiration.git "$env:USERPROFILE\.codex\skills\vibe-coding-inspiration"
```

Restart Codex after installing so the skill can be discovered.

## Example Prompts

After installation, ask Codex things like:

```text
Use vibe coding inspiration to find this week's fastest-growing GitHub projects.
```

```text
帮我找最近适合做的 vibe coding 项目灵感。
```

```text
生成一份中文 vibe coding inspiration 报告。
```

```text
分析本周增长最快的 GitHub 项目，看看有哪些可以做成中文化、小工具、插件或垂直版本。
```

## Manual Run

You can also run the bundled scripts yourself from the skill directory.

```powershell
python .\scripts\github_fast_growing_web_repos.py --out-dir . --limit 50 --metadata-source html
python .\scripts\build_github_growth_html.py --input .\github_fast_growing_web_repos.json --zh-summaries .\assets\github_growth_radar_zh_summaries.json --output .\vibe-coding-inspiration.html
```

Then open:

```text
vibe-coding-inspiration.html
```

## Outputs

Running the scripts creates:

- `vibe-coding-inspiration.html` — Chinese inspiration report
- `github_fast_growing_web_repos.json` — structured data
- `github_fast_growing_web_repos.csv` — spreadsheet-friendly data
- `github_fast_growing_web_repos.md` — Markdown summary

## Optional GitHub Token

By default, the fetch script uses public HTML pages to avoid GitHub API rate limits.

For more stable metadata, set `GITHUB_TOKEN` and use API mode:

```powershell
$env:GITHUB_TOKEN = "your_token"
python .\scripts\github_fast_growing_web_repos.py --out-dir . --limit 50 --metadata-source api
```

Use a token with read access to public repositories. Do not commit your token.

## Customize Sources

You can change the GitHub Trending language buckets:

```powershell
python .\scripts\github_fast_growing_web_repos.py --languages "TypeScript,JavaScript,Python,Rust" --limit 100
```

The current version focuses on GitHub growth signals. Future versions can add Product Hunt, Hacker News, Reddit, Chrome extensions, App Store, or AI tool directories as additional inspiration sources.

## How To Think About The Signals

- Weekly stars show momentum, not guaranteed demand.
- Issues reveal usage, friction, and feature requests.
- Forks suggest reuse, self-hosting, or integration interest.
- The best idea is usually not copying a popular project directly.
- Look for narrower audiences, simpler workflows, Chinese-localized versions, browser plugins, templates, or vertical tools.

## Repository Layout

```text
vibe-coding-inspiration/
├─ SKILL.md
├─ scripts/
│  ├─ github_fast_growing_web_repos.py
│  └─ build_github_growth_html.py
└─ assets/
   └─ github_growth_radar_zh_summaries.json
```

## License

MIT
