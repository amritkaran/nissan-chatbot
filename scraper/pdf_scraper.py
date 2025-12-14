"""
PDF Brochure scraper for Nissan UK website.
Downloads PDFs and extracts text for RAG ingestion.
"""

import os
import json
import httpx
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

try:
    import pymupdf  # PyMuPDF
except ImportError:
    pymupdf = None
    print("PyMuPDF not installed. Run: pip install pymupdf")

load_dotenv()

# PDF brochure URLs from nissan.co.uk/vehicles/brochures.html
PDF_BROCHURES = [
    # Car Brochures
    {
        "name": "All New Nissan MICRA",
        "vehicle_model": "Micra",
        "category": "brochure",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/All-New_MICRA_Info_Pack_v2.pdf",
    },
    {
        "name": "Nissan MICRA Technical Specs",
        "vehicle_model": "Micra",
        "category": "specifications",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/nissan_europe/vehicles/micra/Micra2025/PDFTechSpecs/UK%20-%20Technical%20Specifications.pdf",
    },
    {
        "name": "Nissan Juke Brochure",
        "vehicle_model": "Juke",
        "category": "brochure",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Juke_UK.pdf",
    },
    {
        "name": "Nissan Juke Accessories",
        "vehicle_model": "Juke",
        "category": "accessories",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicle-accessories/Nissan_Juke_MY19_accessories_UK.pdf",
    },
    {
        "name": "Nissan Qashqai Brochure",
        "vehicle_model": "Qashqai",
        "category": "brochure",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Qashqai_UK.pdf",
    },
    {
        "name": "Nissan Qashqai Accessories",
        "vehicle_model": "Qashqai",
        "category": "accessories",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicle-accessories/All-New_Nissan_Qashqai_accessories_UK.pdf",
    },
    {
        "name": "Nissan X-Trail Brochure",
        "vehicle_model": "X-Trail",
        "category": "brochure",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_X-Trail_UK.pdf",
    },
    {
        "name": "Nissan X-Trail Accessories",
        "vehicle_model": "X-Trail",
        "category": "accessories",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicle-accessories/Nissan_X-Trail_accessories_UK.pdf",
    },
    {
        "name": "Nissan ARIYA Brochure",
        "vehicle_model": "Ariya",
        "category": "brochure",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Ariya_UK.pdf",
    },
    {
        "name": "Nissan ARIYA Accessories",
        "vehicle_model": "Ariya",
        "category": "accessories",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicle-accessories/Nissan_Ariya_accessories_UK.pdf",
    },
    # Van Brochures
    {
        "name": "Nissan Townstar Brochure",
        "vehicle_model": "Townstar",
        "category": "brochure",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Townstar_UK.pdf",
    },
    {
        "name": "Nissan Townstar Accessories",
        "vehicle_model": "Townstar",
        "category": "accessories",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicle-accessories/Nissan_Townstar_Van_accessories_UK.pdf",
    },
    {
        "name": "Nissan Primastar Brochure",
        "vehicle_model": "Primastar",
        "category": "brochure",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_Primastar_UK.pdf",
    },
    {
        "name": "Nissan Interstar Brochure",
        "vehicle_model": "Interstar",
        "category": "brochure",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/INTERSTAR_BROCHURE.pdf",
    },
    {
        "name": "Nissan Interstar Accessories",
        "vehicle_model": "Interstar",
        "category": "accessories",
        "url": "https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicle-accessories/BROCHURES_DIGITAL_InterstarAccessoriesBrochure.pdf",
    },
]


class PDFScraper:
    def __init__(self):
        self.pdf_dir = Path("data/pdfs")
        self.processed_dir = Path("data/processed")
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Create output directories if they don't exist."""
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """Convert name to safe filename."""
        return "".join(c if c.isalnum() or c in "- " else "_" for c in name).strip().replace(" ", "_")

    def download_pdf(self, url: str, filename: str) -> Path | None:
        """Download PDF from URL."""
        filepath = self.pdf_dir / f"{filename}.pdf"

        if filepath.exists():
            print(f"  Already downloaded: {filename}")
            return filepath

        try:
            print(f"  Downloading: {url}")
            with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()

                with open(filepath, "wb") as f:
                    f.write(response.content)

                print(f"  Saved: {filepath}")
                return filepath
        except Exception as e:
            print(f"  Error downloading {url}: {e}")
            return None

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using PyMuPDF."""
        if pymupdf is None:
            raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

        text_parts = []
        try:
            doc = pymupdf.open(pdf_path)
            for page_num, page in enumerate(doc, 1):
                text = page.get_text()
                if text.strip():
                    text_parts.append(f"--- Page {page_num} ---\n{text}")
            doc.close()
        except Exception as e:
            print(f"  Error extracting text from {pdf_path}: {e}")
            return ""

        return "\n\n".join(text_parts)

    def process_brochure(self, brochure: dict) -> dict | None:
        """Download and process a single brochure."""
        filename = self._sanitize_filename(brochure["name"])

        # Download PDF
        pdf_path = self.download_pdf(brochure["url"], filename)
        if not pdf_path:
            return None

        # Extract text
        print(f"  Extracting text...")
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print(f"  No text extracted from {filename}")
            return None

        # Create processed document
        return {
            "title": brochure["name"],
            "url": brochure["url"],
            "content": text,
            "metadata": {
                "source": "nissan.co.uk",
                "vehicle_model": brochure["vehicle_model"],
                "category": brochure["category"],
                "document_type": "pdf_brochure",
                "scraped_at": datetime.now().isoformat(),
            }
        }

    def save_processed(self, content: dict, filename: str):
        """Save processed content."""
        # Save as markdown
        md_filepath = self.processed_dir / f"pdf_{filename}.md"
        md_content = f"""---
title: {content['title']}
url: {content['url']}
vehicle_model: {content['metadata'].get('vehicle_model', 'N/A')}
category: {content['metadata']['category']}
document_type: pdf_brochure
scraped_at: {content['metadata']['scraped_at']}
---

# {content['title']}

{content['content']}
"""
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Also save as JSON
        json_filepath = self.processed_dir / f"pdf_{filename}.json"
        with open(json_filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

        print(f"  Saved: {md_filepath.name}")

    def run(self, brochures: list[dict] | None = None):
        """Run the PDF scraping pipeline."""
        brochures = brochures or PDF_BROCHURES

        print(f"Processing {len(brochures)} PDF brochures...\n")

        successful = 0
        for brochure in brochures:
            print(f"Processing: {brochure['name']}")

            processed = self.process_brochure(brochure)
            if processed:
                filename = self._sanitize_filename(brochure["name"])
                self.save_processed(processed, filename)
                successful += 1
            print()

        print(f"\nPDF scraping complete!")
        print(f"Successfully processed: {successful}/{len(brochures)} brochures")
        print(f"PDFs saved to: {self.pdf_dir}")
        print(f"Processed files saved to: {self.processed_dir}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scrape Nissan PDF brochures")
    parser.add_argument("--url", type=str, help="Scrape single PDF URL")
    parser.add_argument("--name", type=str, default="custom_brochure", help="Name for single PDF")
    args = parser.parse_args()

    scraper = PDFScraper()

    if args.url:
        brochure = {
            "name": args.name,
            "vehicle_model": "Unknown",
            "category": "brochure",
            "url": args.url,
        }
        scraper.run(brochures=[brochure])
    else:
        scraper.run()


if __name__ == "__main__":
    main()
