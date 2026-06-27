#!/usr/bin/env python3
"""Build a standalone HTML report from GitHub growth JSON data."""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path


def fmt_number(value: int | None) -> str:
    if value is None:
        return "-"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 10_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,}"


def clean_text(value: str | None) -> str:
    if not value:
        return "No project description provided."
    return " ".join(value.split())


def metric_value(repo: dict, key: str) -> int:
    value = repo.get(key)
    return value if isinstance(value, int) else -1


def build_cards(repos: list[dict]) -> str:
    cards: list[str] = []
    for repo in repos:
        full_name = html.escape(repo.get("full_name", "Unknown repo"))
        owner = html.escape(repo.get("owner", ""))
        description = html.escape(clean_text(repo.get("description_zh") or repo.get("description")))
        url = html.escape(repo.get("url", "#"))
        bucket = html.escape(repo.get("language_bucket", "All"))
        stars_week = fmt_number(repo.get("stars_this_week"))
        issues = fmt_number(repo.get("open_issues_count"))
        forks = fmt_number(repo.get("forks_count"))
        total_stars = fmt_number(repo.get("total_stars"))
        rank = repo.get("rank", "")

        cards.append(
            f"""
      <article class="repo-card" data-name="{full_name.lower()}" data-owner="{owner.lower()}" data-bucket="{bucket.lower()}" data-growth="{metric_value(repo, 'stars_this_week')}" data-issues="{metric_value(repo, 'open_issues_count')}" data-forks="{metric_value(repo, 'forks_count')}">
        <div class="rank">#{rank}</div>
        <div class="repo-main">
          <div class="repo-heading">
            <div>
              <p class="owner">GitHub 项目</p>
              <h2>{full_name}</h2>
            </div>
            <span class="bucket">{bucket}</span>
          </div>
          <p class="description">{description}</p>
          <div class="metrics" aria-label="Repository metrics">
            <div class="metric primary">
              <span class="metric-label">本周新增</span>
              <strong>{stars_week}</strong>
            </div>
            <div class="metric">
              <span class="metric-label">Issues</span>
              <strong>{issues}</strong>
            </div>
            <div class="metric">
              <span class="metric-label">Forks</span>
              <strong>{forks}</strong>
            </div>
            <div class="metric">
              <span class="metric-label">总 Stars</span>
              <strong>{total_stars}</strong>
            </div>
          </div>
          <a class="repo-link" href="{url}" target="_blank" rel="noreferrer">打开 GitHub 项目</a>
        </div>
      </article>"""
        )
    return "\n".join(cards)


def build_html(repos: list[dict]) -> str:
    repos = sorted(repos, key=lambda item: metric_value(item, "stars_this_week"), reverse=True)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_growth = sum(max(metric_value(repo, "stars_this_week"), 0) for repo in repos)
    top_repo = repos[0] if repos else {}
    buckets = sorted({repo.get("language_bucket", "All") for repo in repos})
    cards = build_cards(repos)
    bucket_options = "\n".join(
        f'<option value="{html.escape(bucket.lower())}">{html.escape(bucket)}</option>'
        for bucket in buckets
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>vibe coding inspiration</title>
  <style>
    :root {{
      --ink: #1d2328;
      --muted: #66717c;
      --paper: #f7f4ee;
      --panel: #fffdf8;
      --line: #ded7cc;
      --accent: #0e7c66;
      --accent-dark: #075a4b;
      --warm: #d75f2a;
      --cool: #2f6f9f;
      --shadow: 0 18px 45px rgba(48, 38, 23, .11);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background:
        linear-gradient(90deg, rgba(14,124,102,.08) 1px, transparent 1px),
        linear-gradient(0deg, rgba(14,124,102,.06) 1px, transparent 1px),
        var(--paper);
      background-size: 28px 28px;
      color: var(--ink);
      font-family: "Aptos", "Segoe UI", sans-serif;
      line-height: 1.5;
    }}

    .page {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 42px 0 56px;
    }}

    header {{
      display: grid;
      grid-template-columns: minmax(0, 1.25fr) minmax(280px, .75fr);
      gap: 24px;
      align-items: end;
      margin-bottom: 24px;
    }}

    h1 {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(42px, 7vw, 92px);
      line-height: .9;
      letter-spacing: 0;
      max-width: 760px;
    }}

    .subtitle {{
      margin: 18px 0 0;
      max-width: 660px;
      color: var(--muted);
      font-size: 17px;
    }}

    .summary {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
    }}

    .summary-item {{
      min-height: 92px;
      border: 1px solid var(--line);
      background: rgba(255, 253, 248, .86);
      padding: 15px;
      border-radius: 8px;
      box-shadow: 0 8px 25px rgba(48, 38, 23, .06);
    }}

    .summary-item span,
    .metric-label,
    .owner,
    .control label {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .08em;
      font-weight: 700;
    }}

    .summary-item strong {{
      display: block;
      margin-top: 5px;
      font-size: 24px;
      line-height: 1.1;
    }}

    .toolbar {{
      position: sticky;
      top: 0;
      z-index: 5;
      display: grid;
      grid-template-columns: minmax(220px, 1fr) 180px 180px;
      gap: 12px;
      margin: 24px 0;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(247, 244, 238, .92);
      backdrop-filter: blur(14px);
      box-shadow: 0 12px 28px rgba(48, 38, 23, .08);
    }}

    .control input,
    .control select {{
      width: 100%;
      margin-top: 6px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--ink);
      padding: 11px 12px;
      font: inherit;
      outline: none;
    }}

    .control input:focus,
    .control select:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(14, 124, 102, .16);
    }}

    .repo-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}

    .repo-card {{
      display: grid;
      grid-template-columns: 62px minmax(0, 1fr);
      gap: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      overflow: hidden;
      box-shadow: var(--shadow);
    }}

    .rank {{
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--ink);
      color: #fff7e8;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 20px;
      min-height: 100%;
    }}

    .repo-main {{
      min-width: 0;
      padding: 18px;
    }}

    .repo-heading {{
      display: flex;
      gap: 12px;
      justify-content: space-between;
      align-items: flex-start;
    }}

    .owner {{
      margin: 0 0 2px;
    }}

    h2 {{
      margin: 0;
      overflow-wrap: anywhere;
      font-size: 23px;
      line-height: 1.05;
      letter-spacing: 0;
    }}

    .bucket {{
      flex: 0 0 auto;
      border: 1px solid rgba(47, 111, 159, .28);
      border-radius: 999px;
      color: var(--cool);
      background: rgba(47, 111, 159, .08);
      padding: 5px 9px;
      font-size: 12px;
      font-weight: 700;
    }}

    .description {{
      min-height: 70px;
      margin: 14px 0 16px;
      color: #3e464c;
      font-size: 14px;
      overflow-wrap: anywhere;
    }}

    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 15px;
    }}

    .metric {{
      border-top: 3px solid var(--line);
      background: #f8f1e7;
      padding: 9px 8px;
      border-radius: 6px;
      min-width: 0;
    }}

    .metric.primary {{
      border-color: var(--warm);
      background: #fff0e5;
    }}

    .metric strong {{
      display: block;
      margin-top: 3px;
      font-size: 18px;
      white-space: nowrap;
    }}

    .repo-link {{
      display: inline-flex;
      align-items: center;
      min-height: 38px;
      border-radius: 6px;
      background: var(--accent);
      color: white;
      text-decoration: none;
      padding: 8px 12px;
      font-weight: 800;
    }}

    .repo-link:hover {{
      background: var(--accent-dark);
    }}

    .empty {{
      display: none;
      border: 1px dashed var(--line);
      border-radius: 8px;
      padding: 28px;
      background: rgba(255, 253, 248, .8);
      color: var(--muted);
    }}

    body.no-results .empty {{
      display: block;
    }}

    body.no-results .repo-grid {{
      display: none;
    }}

    @media (max-width: 900px) {{
      header,
      .repo-grid,
      .toolbar {{
        grid-template-columns: 1fr;
      }}

      .summary {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 620px) {{
      .page {{
        width: min(100% - 22px, 1180px);
        padding-top: 24px;
      }}

      .summary,
      .metrics {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}

      .repo-card {{
        grid-template-columns: 48px minmax(0, 1fr);
      }}

      .repo-main {{
        padding: 14px;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <header>
      <div>
        <h1>vibe coding inspiration</h1>
        <p class="subtitle">面向中文开发者的 vibe coding 灵感情报系统。当前版本先追踪 GitHub 上增长最快的 vibe coding 项目，并用 issues 与 forks 辅助判断真实使用信号。</p>
      </div>
      <section class="summary" aria-label="Report summary">
        <div class="summary-item">
          <span>项目数</span>
          <strong>{len(repos)}</strong>
        </div>
        <div class="summary-item">
          <span>本周新增 Stars</span>
          <strong>{fmt_number(total_growth)}</strong>
        </div>
        <div class="summary-item">
          <span>增长第一名</span>
          <strong>{html.escape(top_repo.get("full_name", "-"))}</strong>
        </div>
        <div class="summary-item">
          <span>生成时间</span>
          <strong>{generated_at}</strong>
        </div>
      </section>
    </header>

    <section class="toolbar" aria-label="Filters">
      <div class="control">
        <label for="search">搜索</label>
        <input id="search" type="search" placeholder="项目名、作者、简介">
      </div>
      <div class="control">
        <label for="bucket">分类</label>
        <select id="bucket">
          <option value="all">全部分类</option>
          {bucket_options}
        </select>
      </div>
      <div class="control">
        <label for="sort">排序</label>
        <select id="sort">
          <option value="growth">本周增速</option>
          <option value="forks">Forks</option>
          <option value="issues">Issues</option>
        </select>
      </div>
    </section>

    <p class="empty">没有匹配的项目。</p>
    <section class="repo-grid" id="repoGrid" aria-label="Repository cards">
{cards}
    </section>
  </main>

  <script>
    const grid = document.querySelector("#repoGrid");
    const cards = Array.from(document.querySelectorAll(".repo-card"));
    const search = document.querySelector("#search");
    const bucket = document.querySelector("#bucket");
    const sort = document.querySelector("#sort");

    function applyView() {{
      const term = search.value.trim().toLowerCase();
      const selectedBucket = bucket.value;
      let visible = 0;

      cards.forEach((card) => {{
        const matchesText = !term || card.textContent.toLowerCase().includes(term);
        const matchesBucket = selectedBucket === "all" || card.dataset.bucket === selectedBucket;
        const show = matchesText && matchesBucket;
        card.hidden = !show;
        if (show) visible += 1;
      }});

      const sortKey = sort.value;
      const dataKey = sortKey === "forks" ? "forks" : sortKey === "issues" ? "issues" : "growth";
      cards
        .slice()
        .sort((a, b) => Number(b.dataset[dataKey]) - Number(a.dataset[dataKey]))
        .forEach((card) => grid.appendChild(card));

      document.body.classList.toggle("no-results", visible === 0);
    }}

    search.addEventListener("input", applyView);
    bucket.addEventListener("change", applyView);
    sort.addEventListener("change", applyView);
  </script>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an HTML report for GitHub growth data.")
    parser.add_argument("--input", default="github_fast_growing_web_repos.json")
    parser.add_argument("--output", default="webcalling-information.html")
    parser.add_argument(
        "--zh-summaries",
        default="github_growth_radar_zh_summaries.json",
        help="Optional JSON object mapping full repo names to Chinese summaries.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    repos = json.loads(input_path.read_text(encoding="utf-8"))
    zh_path = Path(args.zh_summaries)
    if zh_path.exists():
        summaries = json.loads(zh_path.read_text(encoding="utf-8"))
        for repo in repos:
            summary = summaries.get(repo.get("full_name"))
            if summary:
                repo["description_zh"] = summary
    output_path.write_text(build_html(repos), encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
