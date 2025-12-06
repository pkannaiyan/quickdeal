"""Platform scrapers for quick commerce websites."""
from .base_scraper import BaseScraper

# Demo scrapers (with sample data)
from .blinkit_scraper import BlinkitScraper
from .zepto_scraper import ZeptoScraper
from .instamart_scraper import InstamartScraper
from .bigbasket_scraper import BigBasketScraper
from .jiomart_scraper import JioMartScraper

# Real scrapers (actual web scraping)
from .real_blinkit_scraper import RealBlinkitScraper
from .real_zepto_scraper import RealZeptoScraper
from .real_bigbasket_scraper import RealBigBasketScraper

__all__ = [
    "BaseScraper",
    # Demo scrapers
    "BlinkitScraper",
    "ZeptoScraper", 
    "InstamartScraper",
    "BigBasketScraper",
    "JioMartScraper",
    # Real scrapers
    "RealBlinkitScraper",
    "RealZeptoScraper",
    "RealBigBasketScraper",
]

