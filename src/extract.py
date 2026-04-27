import os
import re
from typing import Iterable

from bs4 import BeautifulSoup, Tag, NavigableString


CRAFTING_SECTION_HINTS = {
    "crafting",
    "crafting ingredient",
    "recipes",
}

ACQUISITION_SECTION_HINTS = {
    "obtaining",
    "mining",
    "generated loot",
    "loot",
    "mob loot",
    "natural generation",
    "trading",
    "bartering",
}

PROCESSING_SECTION_HINTS = {
    "smelting",
    "blasting",
    "smoking",
    "campfire cooking",
    "stonecutting",
    "smithing",
}

STOP_SECTION_HINTS = {
    "history",
    "development",
    "data values",
    "id",
    "achievements",
    "advancements",
    "videos",
    "issues",
    "trivia",
    "gallery",
    "screenshots",
    "external links",
    "navigation",
    "references",
    "see also",
    "notes",
    "sounds",
}


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\[\s*edit\s*\|\s*edit source\s*\]", "", text, flags=re.I)
    text = re.sub(r"\[\s*edit\s*\]", "", text, flags=re.I)
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"\s+([,.:;!?])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_heading(text: str) -> str:
    return clean_text(text).lower()


def safe_filename(name: str) -> str:
    return (
        name.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace(":", "_")
        + ".md"
    )


def is_jsonish(line: str) -> bool:
    s = line.strip()
    return (
        (s.startswith("{") and s.endswith("}"))
        or '"title":' in s
        or '"rows":' in s
        or '"item":' in s
        or '"chance":' in s
    )


def is_noise_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False

    bad_exact = {
        "Java Edition:",
        "Bedrock Edition:",
        "Java Edition :",
        "Bedrock Edition :",
        "Contents",
    }
    if s in bad_exact:
        return True

    bad_contains = [
        "Issues relating to",
        "bug tracker",
        "Minecraft.net",
        "Taking Inventory:",
    ]
    if any(x in s for x in bad_contains):
        return True

    if is_jsonish(s):
        return True

    if s in {"[", "]", "|", "v", "t", "e"}:
        return True

    return False


def section_kind(heading: str) -> str | None:
    h = normalize_heading(heading)
    if h in CRAFTING_SECTION_HINTS:
        return "crafting"
    if h in ACQUISITION_SECTION_HINTS:
        return "acquisition"
    if h in PROCESSING_SECTION_HINTS:
        return "processing"
    if h in STOP_SECTION_HINTS:
        return "stop"
    return None


def remove_noise_nodes(root: Tag) -> None:
    selectors = [
        "style",
        "script",
        "sup.reference",
        ".mw-editsection",
        ".navbox",
        ".vertical-navbox",
        ".toc",
        ".gallery",
        ".thumb",
        ".error",
        ".metadata",
        ".nomobile",
        ".noprint",
    ]
    for sel in selectors:
        for tag in root.select(sel):
            tag.decompose()


def iter_top_level_content(root: Tag) -> Iterable[Tag]:
    for child in root.children:
        if isinstance(child, NavigableString):
            continue
        if isinstance(child, Tag):
            yield child


def extract_paragraph_text(tag: Tag) -> str | None:
    text = clean_text(tag.get_text(" ", strip=True))
    if not text or is_noise_line(text):
        return None
    return text


def extract_list_items(tag: Tag) -> list[str]:
    items: list[str] = []
    for li in tag.find_all("li", recursive=False):
        text = clean_text(li.get_text(" ", strip=True))
        if text and not is_noise_line(text):
            items.append(text)
    return items


def table_to_rows(table: Tag) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        row = [clean_text(c.get_text(" ", strip=True)) for c in cells]
        row = [c for c in row if c and not is_noise_line(c)]
        if row:
            rows.append(row)
    return rows


def parse_crafting_table(rows: list[list[str]]) -> list[dict]:
    parsed: list[dict] = []

    for row in rows:
        joined = " | ".join(row).lower()

        if "ingredients" in joined and "crafting recipe" in joined:
            continue

        if len(row) >= 2:
            output_name = row[0]
            ingredients = row[1]

            pattern = None
            description = None

            if len(row) >= 3:
                pattern = row[2]
            if len(row) >= 4:
                description = row[3]

            parsed.append(
                {
                    "output": output_name,
                    "ingredients": ingredients,
                    "pattern": pattern,
                    "description": description,
                }
            )

    return parsed


def parse_processing_table(rows: list[list[str]], process_type: str) -> list[dict]:
    parsed: list[dict] = []

    for row in rows:
        joined = " | ".join(row).lower()

        if process_type.lower() in joined and ("ingredients" in joined or "recipe" in joined):
            continue

        if len(row) >= 2:
            output_name = row[0]
            inputs = row[1]
            parsed.append(
                {
                    "type": process_type,
                    "input": inputs,
                    "output": output_name,
                }
            )

    return parsed


def parse_loot_table(rows: list[list[str]]) -> list[dict]:
    parsed: list[dict] = []

    headerish = {"item", "structure", "container", "quantity", "chance", "name", "probability"}

    for row in rows:
        lowered = [c.lower() for c in row]
        if any(c in headerish for c in lowered):
            continue

        if len(row) >= 2:
            entry = {
                "type": "loot",
                "source": row[0],
                "details": row[1:],
            }
            parsed.append(entry)

    return parsed


def collapse_blank_lines(lines: list[str]) -> str:
    out: list[str] = []
    prev_blank = False
    for line in lines:
        blank = line.strip() == ""
        if blank and prev_blank:
            continue
        out.append(line)
        prev_blank = blank
    return "\n".join(out).strip() + "\n"


def extract_structured_data(html: str, title: str, url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one(".mw-parser-output")
    if root is None:
        root = soup

    remove_noise_nodes(root)

    crafting_entries: list[dict] = []
    acquisition_entries: list[dict] = []
    processing_entries: list[dict] = []

    current_kind: str | None = None

    for elem in iter_top_level_content(root):
        if elem.name in {"h2", "h3", "h4"}:
            heading = clean_text(elem.get_text(" ", strip=True))
            kind = section_kind(heading)

            if kind == "stop":
                current_kind = None
            elif kind in {"crafting", "acquisition", "processing"}:
                current_kind = kind
            else:
                # keep previous subsection context unless this is a hard stop
                pass
            continue

        if current_kind is None:
            continue

        if elem.name == "p":
            text = extract_paragraph_text(elem)
            if not text:
                continue

            if current_kind == "acquisition":
                acquisition_entries.append(
                    {
                        "type": "text",
                        "text": text,
                    }
                )
            elif current_kind == "processing":
                processing_entries.append(
                    {
                        "type": "text",
                        "text": text,
                    }
                )
            elif current_kind == "crafting":
                crafting_entries.append(
                    {
                        "output": title,
                        "ingredients": text,
                        "pattern": None,
                        "description": "Free-text crafting-related paragraph",
                    }
                )
            continue

        if elem.name in {"ul", "ol"}:
            items = extract_list_items(elem)
            if not items:
                continue

            if current_kind == "acquisition":
                for item in items:
                    acquisition_entries.append(
                        {
                            "type": "list_item",
                            "text": item,
                        }
                    )
            elif current_kind == "processing":
                for item in items:
                    processing_entries.append(
                        {
                            "type": "list_item",
                            "text": item,
                        }
                    )
            elif current_kind == "crafting":
                for item in items:
                    crafting_entries.append(
                        {
                            "output": title,
                            "ingredients": item,
                            "pattern": None,
                            "description": "List item",
                        }
                    )
            continue

        if elem.name == "table":
            rows = table_to_rows(elem)
            if not rows:
                continue

            if current_kind == "crafting":
                crafting_entries.extend(parse_crafting_table(rows))
            elif current_kind == "processing":
                # We do not know exact process subtype at DOM level, so use generic label.
                processing_entries.extend(parse_processing_table(rows, "Processing"))
            elif current_kind == "acquisition":
                acquisition_entries.extend(parse_loot_table(rows))
            continue

    return build_markdown(
        title=title,
        url=url,
        crafting_entries=crafting_entries,
        acquisition_entries=acquisition_entries,
        processing_entries=processing_entries,
    )


def dedupe_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def build_markdown(
    title: str,
    url: str,
    crafting_entries: list[dict],
    acquisition_entries: list[dict],
    processing_entries: list[dict],
) -> str:
    lines: list[str] = [f"# {title}", "", f"Source: {url}", ""]

    lines.append("## Crafting Recipes")
    lines.append("")
    if crafting_entries:
        for entry in crafting_entries:
            output = entry.get("output")
            ingredients = entry.get("ingredients")
            pattern = entry.get("pattern")
            description = entry.get("description")

            if output:
                lines.append(f"- Output: {output}")
            if ingredients:
                lines.append(f"  - Ingredients: {ingredients}")
            if pattern:
                lines.append(f"  - Pattern: {pattern}")
            if description:
                lines.append(f"  - Notes: {description}")
            lines.append("")
    else:
        lines.append("- None found")
        lines.append("")

    lines.append("## Acquisition")
    lines.append("")
    if acquisition_entries:
        text_lines = []
        for entry in acquisition_entries:
            if "text" in entry:
                text_lines.append(entry["text"])
            elif entry.get("type") == "loot":
                source = entry.get("source", "")
                details = entry.get("details", [])
                detail_text = "; ".join(details) if details else ""
                if detail_text:
                    text_lines.append(f"Loot source: {source} — {detail_text}")
                else:
                    text_lines.append(f"Loot source: {source}")

        for item in dedupe_preserve_order(text_lines):
            lines.append(f"- {item}")
        lines.append("")
    else:
        lines.append("- None found")
        lines.append("")

    lines.append("## Processing")
    lines.append("")
    if processing_entries:
        for entry in processing_entries:
            if "input" in entry and "output" in entry:
                process_type = entry.get("type", "Processing")
                lines.append(f"- Type: {process_type}")
                lines.append(f"  - Input: {entry['input']}")
                lines.append(f"  - Output: {entry['output']}")
                lines.append("")
            elif "text" in entry:
                lines.append(f"- {entry['text']}")
            else:
                text = entry.get("text")
                if text:
                    lines.append(f"- {text}")
        lines.append("")
    else:
        lines.append("- None found")
        lines.append("")

    return collapse_blank_lines(lines)


def save_markdown(output_dir: str, title: str, markdown: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, safe_filename(title))
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown)
    return path