"""
Firecrawl-based web scraper for Nissan website.
Extracts content and converts to clean markdown for RAG ingestion.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from tqdm import tqdm

from config import SCRAPE_URLS, CRAWL_CONFIG, OUTPUT_CONFIG

load_dotenv()


class NissanScraper:
    def __init__(self):
        self.firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
        self.raw_dir = Path(OUTPUT_CONFIG["raw_dir"])
        self.processed_dir = Path(OUTPUT_CONFIG["processed_dir"])
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Create output directories if they don't exist."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, url: str) -> str:
        """Convert URL to safe filename."""
        # Remove protocol and domain
        name = re.sub(r"https?://[^/]+", "", url)
        # Replace special chars
        name = re.sub(r"[^\w\-]", "_", name)
        # Remove leading/trailing underscores
        name = name.strip("_")
        # Limit length
        return name[:100] if name else "index"

    def scrape_single_url(self, url: str) -> dict | None:
        """Scrape a single URL and return content."""
        try:
            result = self.firecrawl.scrape(
                url,
                formats=["markdown", "html"],
                only_main_content=True,
                wait_for=2000,  # Wait for JS rendering
            )
            return result
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def crawl_site(self, base_url: str, max_pages: int = 100) -> list[dict]:
        """Crawl entire site from base URL."""
        try:
            result = self.firecrawl.crawl(
                base_url,
                limit=max_pages,
                scrape_options={
                    "formats": ["markdown"],
                    "onlyMainContent": True,
                },
                include_paths=CRAWL_CONFIG.get("include_patterns", []),
                exclude_paths=CRAWL_CONFIG.get("exclude_patterns", []),
                poll_interval=5,
            )
            return result.get("data", [])
        except Exception as e:
            print(f"Error crawling {base_url}: {e}")
            return []

    def process_content(self, raw_content, url: str) -> dict:
        """Process raw scraped content into structured format."""
        # Handle both dict and Document object responses
        if hasattr(raw_content, 'markdown'):
            markdown = raw_content.markdown or ""
            metadata = raw_content.metadata
            metadata_dict = {
                "title": getattr(metadata, 'title', ''),
                "description": getattr(metadata, 'description', ''),
                "url": getattr(metadata, 'url', url),
            } if metadata else {}
        else:
            markdown = raw_content.get("markdown", "")
            metadata_dict = raw_content.get("metadata", {})

        # Extract title
        title = metadata_dict.get("title", "")
        if not title:
            # Try to extract from first H1
            h1_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
            title = h1_match.group(1) if h1_match else "Untitled"

        # Clean up markdown
        cleaned_markdown = self._clean_markdown(markdown)

        # Extract vehicle model if present
        vehicle_model = self._extract_vehicle_model(url, title)

        return {
            "title": title,
            "url": url,
            "content": cleaned_markdown,
            "metadata": {
                "source": "nissanusa.com",
                "vehicle_model": vehicle_model,
                "category": self._categorize_content(url),
                "scraped_at": datetime.now().isoformat(),
                "description": metadata_dict.get("description", ""),
            }
        }

    def _clean_markdown(self, markdown: str) -> str:
        """Clean up markdown content."""
        # Remove excessive newlines
        cleaned = re.sub(r"\n{3,}", "\n\n", markdown)
        # Remove empty links
        cleaned = re.sub(r"\[]\([^)]*\)", "", cleaned)
        # Remove image references without alt text
        cleaned = re.sub(r"!\[]\([^)]*\)", "", cleaned)
        return cleaned.strip()

    def _extract_vehicle_model(self, url: str, title: str) -> str | None:
        """Extract vehicle model name from URL or title."""
        # UK and US models
        models = [
            # UK models
            "qashqai", "juke", "x-trail", "xtrail", "ariya", "leaf",
            "townstar", "navara", "interstar", "micra", "note",
            # US models (for compatibility)
            "altima", "sentra", "versa", "maxima",
            "frontier", "titan",
            "rogue", "pathfinder", "murano", "kicks", "armada", "z"
        ]
        url_lower = url.lower()
        title_lower = title.lower()

        for model in models:
            if model in url_lower or model in title_lower:
                return model.replace("-", " ").title()
        return None

    def _categorize_content(self, url: str) -> str:
        """Categorize content based on URL."""
        url_lower = url.lower()
        if "/vehicles/cars" in url_lower:
            return "sedan"
        elif "/vehicles/trucks" in url_lower or "/navara" in url_lower:
            return "truck"
        elif "/vehicles/crossovers" in url_lower or "/crossovers-suvs" in url_lower:
            return "suv"
        elif "/vehicles/electric" in url_lower or "/electric-vehicles" in url_lower:
            return "electric"
        elif "/owners" in url_lower or "/ownership" in url_lower:
            return "ownership"
        elif "/shopping-tools" in url_lower or "/finance" in url_lower:
            return "shopping"
        elif "/prices-specifications" in url_lower:
            return "specifications"
        return "general"

    def save_raw(self, content, filename: str):
        """Save raw scraped content."""
        filepath = self.raw_dir / f"{filename}.json"
        # Convert Document object to dict if needed
        if hasattr(content, 'model_dump'):
            content_dict = content.model_dump()
        elif hasattr(content, 'dict'):
            content_dict = content.dict()
        else:
            content_dict = content
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(content_dict, f, indent=2, ensure_ascii=False, default=str)

    def save_processed(self, content: dict, filename: str):
        """Save processed content as markdown."""
        # Save as markdown
        md_filepath = self.processed_dir / f"{filename}.md"
        md_content = f"""---
title: {content['title']}
url: {content['url']}
vehicle_model: {content['metadata'].get('vehicle_model', 'N/A')}
category: {content['metadata']['category']}
scraped_at: {content['metadata']['scraped_at']}
---

# {content['title']}

{content['content']}
"""
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Also save as JSON for programmatic access
        json_filepath = self.processed_dir / f"{filename}.json"
        with open(json_filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

    def run(self, urls: list[str] | None = None, crawl: bool = False):
        """Run the scraping pipeline."""
        if crawl and CRAWL_CONFIG["crawl_mode"]:
            print(f"Crawling site from {CRAWL_CONFIG['crawl_base_url']}...")
            results = self.crawl_site(
                CRAWL_CONFIG["crawl_base_url"],
                CRAWL_CONFIG["max_pages"]
            )
            for result in tqdm(results, desc="Processing crawled pages"):
                url = result.get("metadata", {}).get("sourceURL", "unknown")
                filename = self._sanitize_filename(url)
                self.save_raw(result, filename)
                processed = self.process_content(result, url)
                self.save_processed(processed, filename)
        else:
            urls = urls or SCRAPE_URLS
            print(f"Scraping {len(urls)} URLs...")

            for url in tqdm(urls, desc="Scraping"):
                raw_content = self.scrape_single_url(url)
                if raw_content:
                    filename = self._sanitize_filename(url)
                    self.save_raw(raw_content, filename)
                    processed = self.process_content(raw_content, url)
                    self.save_processed(processed, filename)

        print(f"\nScraping complete!")
        print(f"Raw files saved to: {self.raw_dir}")
        print(f"Processed files saved to: {self.processed_dir}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scrape Nissan website")
    parser.add_argument("--crawl", action="store_true", help="Crawl entire site")
    parser.add_argument("--url", type=str, help="Scrape single URL")
    args = parser.parse_args()

    scraper = NissanScraper()

    if args.url:
        scraper.run(urls=[args.url])
    else:
        scraper.run(crawl=args.crawl)


if __name__ == "__main__":
    main()
