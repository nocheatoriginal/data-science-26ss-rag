import hashlib
import json
import re
from pathlib import Path

INPUT_FILE = "data/minecraft_crafting_recipes.json"
OUTPUT_DIR = Path("data/minecraft_recipe_docs")

OUTPUT_DIR.mkdir(exist_ok=True)

def safe_filename(name, max_len=80):
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")

    digest = hashlib.md5(name.encode("utf-8")).hexdigest()[:8]

    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("_")

    return f"{slug}_{digest}.md"

def cell_to_text(cell):
    if cell is None:
        return "Empty"
    if isinstance(cell, list):
        return " / ".join(cell) if cell else "Empty"
    return str(cell)


def grid_to_markdown(grid):
    if not grid:
        return "N/A"

    rows = []
    for row in grid:
        cells = [cell_to_text(cell) for cell in row]
        rows.append("| " + " | ".join(cells) + " |")

    return "\n".join([
        "| Slot 1 | Slot 2 | Slot 3 |",
        "|---|---|---|",
        *rows
    ])


def recipe_to_markdown(recipe):
    name = recipe.get("name", "Unknown Recipe")
    output_items = recipe.get("output_items") or [name]
    output_count = recipe.get("output_count", 1)
    output = ", ".join(output_items)

    station = recipe.get("station") or "Unknown"
    shape = "Shapeless" if recipe.get("shapeless") else "Shaped"
    ingredients = recipe.get("ingredients_text") or ", ".join(recipe.get("ingredient_links", []))
    source_url = recipe.get("source_url") or ""
    description = recipe.get("description")

    md = f"""# Recipe: {name}

| Property | Value |
|---|---|
| Name | {name} |
| Output | {output_count} {output} |
| Station | {station} |
| Shape | {shape} |
| Ingredients | {ingredients} |

## Crafting Grid

{grid_to_markdown(recipe.get("grid"))}
"""

    if description:
        md += f"\n## Notes\n\n{description}\n"

    if source_url:
        md += f"\nSource: {source_url}\n"

    return md


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        recipes = json.load(f)

    for recipe in recipes:
        name = recipe.get("name", "unknown_recipe")
        path = OUTPUT_DIR / safe_filename(name)
        path.write_text(recipe_to_markdown(recipe), encoding="utf-8")

    print(f"Created {len(recipes)} markdown files in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()