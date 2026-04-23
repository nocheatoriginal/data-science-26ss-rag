#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from minecraft_wiki_scraper.crafting import scrape_crafting_pages, write_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scrape crafting recipe tables from minecraft.wiki and save them as JSON."
    )
    parser.add_argument(
        "--page",
        action="append",
        default=[],
        help="Crafting slug, /w/... path, or full URL. May be passed multiple times.",
    )
    parser.add_argument(
        "--output",
        default="data/minecraft_crafting_recipes.json",
        help="Target file for the scraped recipes.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "jsonl"),
        default="json",
        help="Output format. Use json for nested data or jsonl for streaming pipelines.",
    )
    parser.add_argument(
        "--include-legacy",
        action="store_true",
        help="Also include legacy recipe pages such as Before_Pocket_Edition_v0.9.0_alpha.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay in seconds between page requests.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="HTTP timeout per request in seconds.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    records = scrape_crafting_pages(
        args.page or None,
        include_legacy=args.include_legacy,
        delay_seconds=args.delay,
        timeout=args.timeout,
    )
    write_records(records, args.output, fmt=args.format)

    print(f"Scraped {len(records)} recipes into {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
