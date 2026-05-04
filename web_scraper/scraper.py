from __future__ import annotations

import argparse
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import json
import re
import time

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://minecraft.wiki"
CRAFTING_INDEX_URL = f"{BASE_URL}/w/Crafting"
DEFAULT_TIMEOUT = 30.0
GENERIC_MCUI_CLASSES = {
    "mcui",
    "mcui-arrow",
    "mcui-icons",
    "mcui-input",
    "mcui-output",
    "mcui-row",
    "mcui-shapeless",
    "pixel-image",
}


def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "minecraft-wiki-crafting-scraper/1.0 "
                "(educational project; contact: local workspace user)"
            )
        }
    )
    return session


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def normalize_header(value: str) -> str:
    return normalize_space(value).casefold()


def humanize_station_class(value: str) -> str:
    value = value.removeprefix("mcui-").replace("_", " ")
    return normalize_space(value)


def unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def page_to_url(page: str) -> str:
    page = page.strip().replace(" ", "_")
    if page.startswith(("http://", "https://")):
        return page
    if page.startswith("/w/"):
        return urljoin(BASE_URL, page)
    return f"{BASE_URL}/w/{page.lstrip('/')}"


def page_slug_from_url(url: str) -> str:
    path = urlparse(url).path
    return path.removeprefix("/w/") or url


def extract_title_candidates(slot: Tag) -> list[str]:
    titles: list[str] = []
    for item in slot.select(".invslot-item"):
        title_node = item.find(attrs={"title": True})
        if title_node is not None:
            title = normalize_space(title_node.get("title", ""))
            if title:
                titles.append(title)
                continue

        title = normalize_space(item.get("data-minetip-title", ""))
        if title:
            titles.append(title)

    return unique(titles)


def parse_grid(mcui: Tag) -> list[list[list[str] | None]]:
    input_root = mcui.select_one(".mcui-input")
    if input_root is None:
        return []

    grid: list[list[list[str] | None]] = []
    for row in input_root.find_all(class_="mcui-row", recursive=False):
        grid_row: list[list[str] | None] = []
        for slot in row.find_all(class_="invslot", recursive=False):
            titles = extract_title_candidates(slot)
            grid_row.append(titles or None)
        if grid_row:
            grid.append(grid_row)
    return grid


def parse_recipe_cell(cell: Tag) -> dict[str, Any]:
    mcui = cell.select_one(".mcui")
    recipe: dict[str, Any] = {
        "station": None,
        "shapeless": False,
        "grid": [],
        "output_items": [],
        "output_count": 1,
    }

    if mcui is None:
        return recipe

    station_class = next(
        (
            class_name
            for class_name in mcui.get("class", [])
            if class_name.startswith("mcui-") and class_name not in GENERIC_MCUI_CLASSES
        ),
        None,
    )
    recipe["station"] = humanize_station_class(station_class) if station_class else None
    recipe["shapeless"] = mcui.select_one(".mcui-shapeless") is not None
    recipe["grid"] = parse_grid(mcui)

    output_slot = mcui.select_one(".mcui-output .invslot")
    if output_slot is not None:
        recipe["output_items"] = extract_title_candidates(output_slot)
        output_count = output_slot.select_one(".invslot-stacksize")
        if output_count is not None:
            count_match = re.search(r"\d+", output_count.get_text(" ", strip=True))
            if count_match:
                recipe["output_count"] = int(count_match.group())

    return recipe


def parse_recipe_table(table: Tag, page_title: str, source_url: str) -> list[dict[str, Any]]:
    header_row = table.find("tr")
    if header_row is None:
        return []

    headers = [
        normalize_header(cell.get_text(" ", strip=True))
        for cell in header_row.find_all(["th", "td"], recursive=False)
    ]
    if "ingredients" not in headers or not any("recipe" in header for header in headers):
        return []

    header_map = {header: index for index, header in enumerate(headers)}
    name_index = header_map.get("name")
    ingredients_index = header_map.get("ingredients")
    recipe_index = next(index for index, header in enumerate(headers) if "recipe" in header)
    description_index = header_map.get("description")

    records: list[dict[str, Any]] = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all(["th", "td"], recursive=False)
        if len(cells) <= recipe_index or ingredients_index is None:
            continue

        name = None
        if name_index is not None and name_index < len(cells):
            name = normalize_space(cells[name_index].get_text(" ", strip=True))

        ingredients_cell = cells[ingredients_index]
        recipe_cell = cells[recipe_index]
        description = None
        if description_index is not None and description_index < len(cells):
            description = normalize_space(cells[description_index].get_text(" ", strip=True)) or None

        recipe_data = parse_recipe_cell(recipe_cell)
        output_name = recipe_data["output_items"][0] if recipe_data["output_items"] else None

        records.append(
            {
                "name": name or output_name or page_title,
                "source_page": page_slug_from_url(source_url),
                "source_url": source_url,
                "ingredients_text": normalize_space(ingredients_cell.get_text(" ", strip=True)),
                "ingredient_links": unique(
                    normalize_space(anchor.get("title", ""))
                    for anchor in ingredients_cell.find_all("a", title=True)
                ),
                "station": recipe_data["station"],
                "shapeless": recipe_data["shapeless"],
                "grid": recipe_data["grid"],
                "output_items": recipe_data["output_items"],
                "output_count": recipe_data["output_count"],
                "description": description,
            }
        )

    return records


def parse_crafting_page_html(html: str, source_url: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.select_one("#firstHeading")
    page_title = normalize_space(heading.get_text(" ", strip=True)) if heading else page_slug_from_url(source_url)

    records: list[dict[str, Any]] = []
    for table in soup.select("table.wikitable"):
        records.extend(parse_recipe_table(table, page_title=page_title, source_url=source_url))
    return records


def discover_crafting_pages(
    session: requests.Session | None = None,
    *,
    include_legacy: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
) -> list[str]:
    owns_session = session is None
    session = session or create_session()
    try:
        response = session.get(CRAFTING_INDEX_URL, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        hrefs = unique(
            anchor.get("href", "")
            for anchor in soup.select('#mw-content-text a[href^="/w/Crafting/"]')
        )

        pages = []
        for href in hrefs:
            slug = page_slug_from_url(href)
            if not include_legacy and slug.startswith("Crafting/Before_"):
                continue
            pages.append(urljoin(BASE_URL, href))
        return pages
    finally:
        if owns_session:
            session.close()


def scrape_crafting_pages(
    pages: Iterable[str] | None = None,
    *,
    include_legacy: bool = False,
    delay_seconds: float = 0.5,
    timeout: float = DEFAULT_TIMEOUT,
) -> list[dict[str, Any]]:
    session = create_session()
    try:
        page_urls = [page_to_url(page) for page in pages] if pages else discover_crafting_pages(
            session, include_legacy=include_legacy, timeout=timeout
        )

        records: list[dict[str, Any]] = []
        for index, page_url in enumerate(page_urls):
            response = session.get(page_url, timeout=timeout)
            response.raise_for_status()
            records.extend(parse_crafting_page_html(response.text, source_url=page_url))

            if delay_seconds > 0 and index < len(page_urls) - 1:
                time.sleep(delay_seconds)

        return records
    finally:
        session.close()


def write_records(records: list[dict[str, Any]], output_path: str | Path, fmt: str = "json") -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return

    if fmt == "jsonl":
        lines = [json.dumps(record, ensure_ascii=False) for record in records]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    raise ValueError(f"Unsupported format: {fmt}")


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

    print(f"Scraped {len(records)} recipes into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
