from tqdm import tqdm

from config import OUTPUT_DIR, PAGES
from extract import extract_structured_data, save_markdown
from fetch import fetch_and_cache_page


def main() -> None:
    for title in tqdm(PAGES, desc="Building knowledge base"):
        payload = fetch_and_cache_page(title)

        parse = payload["parse"]
        html = parse["text"]["*"]
        page_title = parse["title"]
        url = f"https://minecraft.wiki/w/{page_title.replace(' ', '_')}"

        markdown = extract_structured_data(
            html=html,
            title=page_title,
            url=url,
        )

        out_path = save_markdown(OUTPUT_DIR, page_title, markdown)
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()