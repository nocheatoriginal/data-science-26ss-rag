# Minecraft Wiki Crafting Scraper

Der Scraper liegt in `web_scraper/scraper.py` und extrahiert die Rezepttabellen von `minecraft.wiki`.

## Aufbau

- `scraper.py` enthaelt die Scraper-Logik und den CLI-Einstiegspunkt.
- `tests/test_scraper.py` testet die Parser-Logik mit statischen HTML-Beispielen.

## Installation

Abhaengigkeiten installieren:

```bash
python3 -m pip install -r web_scraper/requirements.txt
```

Standardverhalten:

- entdeckt automatisch die aktuellen `Crafting/...`-Unterseiten ueber die Uebersichtsseite `https://minecraft.wiki/w/Crafting`
- extrahiert `name`, `ingredients_text`, `ingredient_links`, `station`, `shapeless`, `grid`, `output_items`, `output_count` und `description`
- speichert standardmaessig nach `data/minecraft_crafting_recipes.json`

## Nutzung

Alle aktuellen Crafting-Seiten scrapen:

```bash
python3 web_scraper/scraper.py
```

Nur einzelne Unterseiten scrapen:

```bash
python3 web_scraper/scraper.py \
  --page Crafting/Building_blocks \
  --page Crafting/Tools \
  --output data/selected_crafting_recipes.json
```

Auch einzelne Artikelseiten funktionieren, zum Beispiel:

```bash
python3 web_scraper/scraper.py --page Diamond_Sword
```

Legacy-Rezepte einschliessen:

```bash
python3 web_scraper/scraper.py --include-legacy
```

Als JSONL speichern:

```bash
python3 web_scraper/scraper.py --format jsonl
```

## Tests

```bash
python3 -m unittest discover -s web_scraper/tests
```

## Datenformat

Beispiel eines Eintrags:

```json
{
  "name": "Bricks",
  "source_page": "Crafting/Building_blocks",
  "source_url": "https://minecraft.wiki/w/Crafting/Building_blocks",
  "ingredients_text": "Brick",
  "ingredient_links": ["Brick"],
  "station": "Crafting Table",
  "shapeless": false,
  "grid": [
    [null, null, null],
    [["Brick"], ["Brick"], null],
    [["Brick"], ["Brick"], null]
  ],
  "output_items": ["Bricks"],
  "output_count": 4,
  "description": null
}
```
