Data Science RAG

## Minecraft Wiki Crafting Scraper

Der Scraper liegt in `scripts/scrape_minecraft_wiki_crafting.py` und extrahiert die Rezepttabellen von `minecraft.wiki`.

Standardverhalten:

- entdeckt automatisch die aktuellen `Crafting/...`-Unterseiten über die Übersichtsseite `https://minecraft.wiki/w/Crafting`
- extrahiert `name`, `ingredients_text`, `ingredient_links`, `station`, `shapeless`, `grid`, `output_items`, `output_count` und `description`
- speichert standardmäßig nach `data/minecraft_crafting_recipes.json`

### Installation

```bash
python3 -m pip install -r requirements.txt
```

### Nutzung

Alle aktuellen Crafting-Seiten scrapen:

```bash
python3 scripts/scrape_minecraft_wiki_crafting.py
```

Nur einzelne Unterseiten scrapen:

```bash
python3 scripts/scrape_minecraft_wiki_crafting.py \
  --page Crafting/Building_blocks \
  --page Crafting/Tools \
  --output data/selected_crafting_recipes.json
```

Auch einzelne Artikelseiten funktionieren, zum Beispiel:

```bash
python3 scripts/scrape_minecraft_wiki_crafting.py --page Diamond_Sword
```

Legacy-Rezepte einschließen:

```bash
python3 scripts/scrape_minecraft_wiki_crafting.py --include-legacy
```

Als JSONL speichern:

```bash
python3 scripts/scrape_minecraft_wiki_crafting.py --format jsonl
```

### Tests

```bash
python3 -m unittest discover -s tests
```

### Datenformat

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
