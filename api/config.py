"""
Configuration module for Price Comparison Agent.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Paths
# =============================================================================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# =============================================================================
# LLM Configuration
# =============================================================================
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3:8b")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))

# =============================================================================
# Scraping Configuration
# =============================================================================
SCRAPE_INTERVAL_MINUTES = int(os.getenv("SCRAPE_INTERVAL_MINUTES", "30"))
MAX_CONCURRENT_SCRAPERS = int(os.getenv("MAX_CONCURRENT_SCRAPERS", "3"))
RESPECT_ROBOTS_TXT = os.getenv("RESPECT_ROBOTS_TXT", "true").lower() == "true"
RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "30"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# =============================================================================
# Location (for accurate pricing)
# =============================================================================
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Mumbai")
DEFAULT_PINCODE = os.getenv("DEFAULT_PINCODE", "400001")

# =============================================================================
# Database
# =============================================================================
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/prices.db")

# =============================================================================
# API Configuration
# =============================================================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8002"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# =============================================================================
# Supported Platforms
# =============================================================================
PLATFORMS = {
    "blinkit": {
        "name": "Blinkit",
        "base_url": "https://blinkit.com",
        "logo": "🟢",
        "delivery_time": "10-20 min",
        "cities": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata"]
    },
    "zepto": {
        "name": "Zepto",
        "base_url": "https://www.zeptonow.com",
        "logo": "🟣",
        "delivery_time": "10 min",
        "cities": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"]
    },
    "instamart": {
        "name": "Swiggy Instamart",
        "base_url": "https://www.swiggy.com/instamart",
        "logo": "🟠",
        "delivery_time": "15-30 min",
        "cities": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad"]
    },
    "bigbasket": {
        "name": "BigBasket",
        "base_url": "https://www.bigbasket.com",
        "logo": "🟢",
        "delivery_time": "Same day",
        "cities": ["Pan India"]
    },
    "jiomart": {
        "name": "JioMart",
        "base_url": "https://www.jiomart.com",
        "logo": "🔵",
        "delivery_time": "Same/Next day",
        "cities": ["Pan India"]
    },
    "amazon_fresh": {
        "name": "Amazon Fresh",
        "base_url": "https://www.amazon.in/fresh",
        "logo": "🟡",
        "delivery_time": "2 hours",
        "cities": ["Mumbai", "Delhi", "Bangalore", "Hyderabad"]
    },
    "flipkart_minutes": {
        "name": "Flipkart Minutes",
        "base_url": "https://www.flipkart.com/grocery",
        "logo": "🔵",
        "delivery_time": "10-30 min",
        "cities": ["Bangalore", "Delhi", "Mumbai"]
    },
    "dmart": {
        "name": "DMart Ready",
        "base_url": "https://www.dmart.in",
        "logo": "🟢",
        "delivery_time": "Same day",
        "cities": ["Mumbai", "Pune", "Bangalore", "Hyderabad", "Ahmedabad"]
    }
}

# =============================================================================
# Product Categories
# =============================================================================
CATEGORIES = [
    {"id": "fruits_vegetables", "name": "Fruits & Vegetables", "icon": "🥬"},
    {"id": "dairy_bread", "name": "Dairy & Bread", "icon": "🥛"},
    {"id": "snacks_beverages", "name": "Snacks & Beverages", "icon": "🍿"},
    {"id": "staples", "name": "Staples & Cooking", "icon": "🍚"},
    {"id": "personal_care", "name": "Personal Care", "icon": "🧴"},
    {"id": "household", "name": "Household Items", "icon": "🧹"},
    {"id": "baby_care", "name": "Baby Care", "icon": "👶"},
    {"id": "pet_care", "name": "Pet Care", "icon": "🐕"},
    {"id": "meat_seafood", "name": "Meat & Seafood", "icon": "🍗"},
    {"id": "frozen", "name": "Frozen & Ice Cream", "icon": "🍦"}
]


def get_config():
    """Return all configuration as a dictionary."""
    return {
        "llm": {
            "ollama_url": OLLAMA_URL,
            "model_name": MODEL_NAME,
            "temperature": LLM_TEMPERATURE
        },
        "scraping": {
            "interval_minutes": SCRAPE_INTERVAL_MINUTES,
            "max_concurrent": MAX_CONCURRENT_SCRAPERS,
            "respect_robots": RESPECT_ROBOTS_TXT,
            "rate_limit_rpm": RATE_LIMIT_RPM
        },
        "location": {
            "city": DEFAULT_CITY,
            "pincode": DEFAULT_PINCODE
        },
        "platforms": PLATFORMS,
        "categories": CATEGORIES
    }

