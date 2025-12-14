"""
Scraper configuration for Nissan UK website.
"""

# Base URLs to scrape
SCRAPE_URLS = [
    # Main vehicle pages
    "https://www.nissan.co.uk/vehicles/new-vehicles.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/electric-vehicles.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/crossovers.html",

    # Individual vehicle models
    "https://www.nissan.co.uk/vehicles/new-vehicles/qashqai.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/juke.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/x-trail.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/ariya.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/leaf.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/townstar.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/navara.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/interstar.html",

    # Specifications pages
    "https://www.nissan.co.uk/vehicles/new-vehicles/qashqai/prices-specifications.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/juke/prices-specifications.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/x-trail/prices-specifications.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/ariya/prices-specifications.html",
    "https://www.nissan.co.uk/vehicles/new-vehicles/leaf/prices-specifications.html",

    # Ownership and services
    "https://www.nissan.co.uk/ownership.html",
    "https://www.nissan.co.uk/ownership/nissan-service.html",
    "https://www.nissan.co.uk/ownership/nissan-warranty.html",
    "https://www.nissan.co.uk/ownership/nissan-assistance.html",

    # Finance and offers
    "https://www.nissan.co.uk/finance.html",
    "https://www.nissan.co.uk/offers.html",

    # Electric vehicles info
    "https://www.nissan.co.uk/electric-vehicles.html",
    "https://www.nissan.co.uk/electric-vehicles/charging.html",
    "https://www.nissan.co.uk/electric-vehicles/range.html",
]

# Crawl configuration
CRAWL_CONFIG = {
    # Set to True to crawl entire site from base URL
    "crawl_mode": False,

    # If crawl_mode is True, start from this URL
    "crawl_base_url": "https://www.nissan.co.uk",

    # Maximum pages to crawl (if crawl_mode is True)
    "max_pages": 100,

    # URL patterns to include (regex)
    "include_patterns": [
        r".*nissan\.co\.uk/vehicles/.*",
        r".*nissan\.co\.uk/ownership/.*",
        r".*nissan\.co\.uk/electric-vehicles/.*",
        r".*nissan\.co\.uk/finance.*",
    ],

    # URL patterns to exclude (regex)
    "exclude_patterns": [
        r".*\.(jpg|jpeg|png|gif|pdf|zip)$",
        r".*/dealer-locator/.*",
        r".*/inventory/.*",
        r".*/configurator/.*",
    ],
}

# Content extraction settings
EXTRACT_CONFIG = {
    # Remove these elements from scraped content
    "remove_selectors": [
        "nav",
        "footer",
        "header",
        ".cookie-banner",
        ".chat-widget",
        "#dealer-locator",
    ],

    # Only extract content from these elements (if specified)
    "main_content_selectors": [
        "main",
        "article",
        ".vehicle-content",
        ".page-content",
    ],
}

# Output configuration
OUTPUT_CONFIG = {
    "raw_dir": "data/raw",
    "processed_dir": "data/processed",
    "file_format": "md",  # md or json
}
