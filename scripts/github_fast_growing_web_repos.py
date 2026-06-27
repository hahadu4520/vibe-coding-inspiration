#!/usr/bin/env python3
"""
Fetch fast-growing web/coding repositories from GitHub Trending.

Metrics collected:
- stars_this_week: growth signal parsed from GitHub Trending weekly pages
- open_issues_count: usage/friction signal from the GitHub REST API
- forks_count: reuse/adoption signal from the GitHub REST API

Optional:
  set GITHUB_TOKEN to raise GitHub API rate limits.
"""

from __future__ import annotations

import argparse
import csv
import http.client
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed


DEFAULT_LANGUAGES = [
    "",
    "TypeScript",
    "JavaScript",
    "CSS",
    "HTML",
    "Vue",
    "Svelte",
    "Astro",
]

USER_AGENT = "github-fast-growing-repos/1.0"


@dataclass
class Repo:
    rank: int
    full_name: str
    owner: str
    name: str
    language_bucket: str
    description: str
    url: str
    stars_this_week: int
    total_stars: int | None = None
    open_issues_count: int | None = None
    forks_count: int | None = None
    api_updated_at: str | None = None


def request_text(url: str, token: str | None = None, timeout: int = 20) -> str:
    headers = {
        "Accept": "text/html,application/json",
        "User-Agent": USER_AGENT,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            try:
                body = response.read()
            except http.client.IncompleteRead as exc:
                body = exc.partial
            return body.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body[:300]}") from exc


def strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def parse_count(value: str) -> int:
    return int(value.replace(",", "").strip())


def parse_human_count(value: str) -> int:
    clean = value.replace(",", "").strip().lower()
    if not re.search(r"\d", clean):
        raise ValueError(f"Could not parse count: {value!r}")
    multiplier = 1
    if clean.endswith("k"):
        multiplier = 1_000
        clean = clean[:-1]
    elif clean.endswith("m"):
        multiplier = 1_000_000
        clean = clean[:-1]
    return int(float(clean) * multiplier)


def parse_trending_page(page: str, language_bucket: str) -> list[Repo]:
    repos: list[Repo] = []
    articles = re.findall(
        r'<article class="Box-row"[^>]*>(.*?)</article>',
        page,
        flags=re.DOTALL | re.IGNORECASE,
    )

    for article in articles:
        link_match = re.search(r'<h2[^>]*>.*?<a[^>]+href="/([^"]+)"', article, re.DOTALL)
        if not link_match:
            continue

        full_name = strip_tags(link_match.group(1)).replace(" ", "")
        if full_name.count("/") != 1:
            continue

        owner, name = full_name.split("/", 1)
        description_match = re.search(
            r'<p[^>]+class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>',
            article,
            flags=re.DOTALL,
        )
        description = strip_tags(description_match.group(1)) if description_match else ""

        stars_match = re.search(r"([\d,]+)\s+stars?\s+this\s+week", strip_tags(article), re.I)
        stars_this_week = parse_count(stars_match.group(1)) if stars_match else 0

        repos.append(
            Repo(
                rank=0,
                full_name=f"{owner}/{name}",
                owner=owner,
                name=name,
                language_bucket=language_bucket or "All",
                description=description,
                url=f"https://github.com/{owner}/{name}",
                stars_this_week=stars_this_week,
            )
        )

    return repos


def fetch_trending(language: str, token: str | None = None) -> list[Repo]:
    if language:
        encoded_language = urllib.parse.quote(language.lower().replace(" ", "-"))
        url = f"https://github.com/trending/{encoded_language}?since=weekly"
    else:
        url = "https://github.com/trending?since=weekly"

    page = request_text(url, token=None, timeout=12)
    return parse_trending_page(page, language)


def fetch_repo_metadata(repo: Repo, token: str | None) -> Repo:
    api_url = f"https://api.github.com/repos/{repo.owner}/{repo.name}"
    data = json.loads(request_text(api_url, token=token, timeout=15))
    repo.total_stars = data.get("stargazers_count")
    repo.open_issues_count = data.get("open_issues_count")
    repo.forks_count = data.get("forks_count")
    repo.api_updated_at = data.get("updated_at")
    return repo


def fetch_repo_html_metadata(repo: Repo) -> Repo:
    page = request_text(repo.url, token=None, timeout=8)

    def count_near_href(path: str, label: str) -> int | None:
        marker = f'href="{path}"'
        index = page.find(marker)
        if index == -1:
            return None
        text = strip_tags(page[index : index + 1500])
        patterns = [
            rf"(\d[\d,.]*[kmKM]?)\s+{label}s?",
            rf"{label}\s+(\d[\d,.]*[kmKM]?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.I)
            if match:
                return parse_human_count(match.group(1))
        return None

    issues_match = re.search(
        r'id="issues-repo-tab-count"[^>]*>\s*(\d[\d,.]*[kmKM]?)\s*</span>',
        page,
        flags=re.DOTALL,
    )

    repo.total_stars = count_near_href(f"/{repo.owner}/{repo.name}/stargazers", "star")
    repo.forks_count = count_near_href(f"/{repo.owner}/{repo.name}/forks", "fork")

    if issues_match:
        repo.open_issues_count = parse_human_count(issues_match.group(1))

    return repo


def enrich_repo(repo: Repo, token: str | None, source: str) -> Repo:
    if source == "api":
        return fetch_repo_metadata(repo, token=token)
    if source == "html":
        return fetch_repo_html_metadata(repo)

    if token:
        try:
            return fetch_repo_metadata(repo, token=token)
        except Exception:
            return fetch_repo_html_metadata(repo)

    try:
        return fetch_repo_html_metadata(repo)
    except Exception:
        return fetch_repo_metadata(repo, token=token)


def dedupe_keep_highest_growth(repos: Iterable[Repo]) -> list[Repo]:
    seen: dict[str, Repo] = {}
    for repo in repos:
        current = seen.get(repo.full_name)
        if current is None or repo.stars_this_week > current.stars_this_week:
            seen[repo.full_name] = repo
    return list(seen.values())


def write_csv(path: Path, repos: list[Repo]) -> None:
    fields = [
        "rank",
        "full_name",
        "url",
        "stars_this_week",
        "open_issues_count",
        "forks_count",
        "total_stars",
        "language_bucket",
        "api_updated_at",
        "description",
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for repo in repos:
            row = asdict(repo)
            writer.writerow({field: row.get(field) for field in fields})


def write_markdown(path: Path, repos: list[Repo], languages: list[str]) -> None:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# GitHub Fast-Growing Web Repos",
        "",
        f"Generated at: {generated_at}",
        f"Language buckets: {', '.join(lang or 'All' for lang in languages)}",
        "",
        "| Rank | Repo | Stars this week | Open issues | Forks | Total stars | Bucket |",
        "|---:|---|---:|---:|---:|---:|---|",
    ]
    for repo in repos:
        lines.append(
            "| "
            f"{repo.rank} | "
            f"[{repo.full_name}]({repo.url}) | "
            f"{repo.stars_this_week} | "
            f"{repo.open_issues_count if repo.open_issues_count is not None else ''} | "
            f"{repo.forks_count if repo.forks_count is not None else ''} | "
            f"{repo.total_stars if repo.total_stars is not None else ''} | "
            f"{repo.language_bucket} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch top fast-growing GitHub web/coding repositories."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Number of repositories to keep after sorting by weekly star growth.",
    )
    parser.add_argument(
        "--languages",
        default=",".join(DEFAULT_LANGUAGES),
        help=(
            "Comma-separated GitHub Trending language buckets. "
            "Use an empty item for the overall Trending page."
        ),
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Directory for CSV, JSON, and Markdown outputs.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0,
        help="Seconds to sleep after each completed GitHub API request.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=6,
        help="Concurrent workers for GitHub API metadata requests.",
    )
    parser.add_argument(
        "--metadata-source",
        choices=["auto", "api", "html"],
        default="auto",
        help="Where to collect total stars, open issues, and forks from.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    token = os.getenv("GITHUB_TOKEN")
    languages = [item.strip() for item in args.languages.split(",")]

    print("Fetching GitHub Trending weekly pages...", file=sys.stderr)
    trending_repos: list[Repo] = []
    for language in languages:
        try:
            repos = fetch_trending(language)
            trending_repos.extend(repos)
            label = language or "All"
            print(f"  {label}: {len(repos)} repos", file=sys.stderr)
        except Exception as exc:
            print(f"  warning: failed to fetch {language or 'All'}: {exc}", file=sys.stderr)

    repos = dedupe_keep_highest_growth(trending_repos)
    repos.sort(key=lambda repo: repo.stars_this_week, reverse=True)
    repos = repos[: args.limit]

    for index, repo in enumerate(repos, start=1):
        repo.rank = index

    source_label = args.metadata_source
    if source_label == "auto":
        source_label = "api" if token else "html"
    print(f"Fetching repository metadata via {source_label}...", file=sys.stderr)
    enriched_by_name: dict[str, Repo] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(enrich_repo, repo, token, args.metadata_source): repo
            for repo in repos
        }
        for future in as_completed(futures):
            repo = futures[future]
            try:
                enriched_by_name[repo.full_name] = future.result()
            except Exception as exc:
                print(f"  warning: failed to enrich {repo.full_name}: {exc}", file=sys.stderr)
                enriched_by_name[repo.full_name] = repo
            if args.sleep:
                time.sleep(args.sleep)

    enriched = [enriched_by_name[repo.full_name] for repo in repos]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "github_fast_growing_web_repos.json"
    csv_path = out_dir / "github_fast_growing_web_repos.csv"
    md_path = out_dir / "github_fast_growing_web_repos.md"

    json_path.write_text(
        json.dumps([asdict(repo) for repo in enriched], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(csv_path, enriched)
    write_markdown(md_path, enriched, languages)

    print(f"Wrote {json_path}", file=sys.stderr)
    print(f"Wrote {csv_path}", file=sys.stderr)
    print(f"Wrote {md_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
