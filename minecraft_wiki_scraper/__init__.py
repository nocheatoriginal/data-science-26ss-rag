"""Utilities for scraping crafting recipes from minecraft.wiki."""

from .crafting import discover_crafting_pages, parse_crafting_page_html, scrape_crafting_pages

__all__ = [
    "discover_crafting_pages",
    "parse_crafting_page_html",
    "scrape_crafting_pages",
]
