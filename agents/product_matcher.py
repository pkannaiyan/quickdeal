"""
Product Matcher Agent - AI-powered product matching across platforms.

Uses a combination of:
1. Exact matching (brand + product name + quantity)
2. Fuzzy matching (for similar names)
3. LLM matching (for complex cases)
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from rapidfuzz import fuzz, process

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.product import Product, ProductMatch, ProductCategory
from models.price import PriceEntry, PriceComparison
from api.config import OLLAMA_URL, MODEL_NAME, PLATFORMS, LOGS_DIR


class ProductMatcherAgent:
    """
    AI Agent for matching products across different platforms.
    
    Products on different platforms may have:
    - Different names for the same product
    - Different package sizes
    - Different brands selling similar items
    
    This agent groups similar products for accurate comparison.
    """
    
    def __init__(self):
        """Initialize the product matcher."""
        self.llm = None  # Lazy load
        
        # Match thresholds
        self.exact_match_threshold = 95  # Fuzzy match score for "exact"
        self.fuzzy_match_threshold = 80  # Minimum for considering a match
        
        # Cache for matched products
        self._match_cache: Dict[str, ProductMatch] = {}
        
        # Statistics
        self._stats = {
            "total_matches": 0,
            "exact_matches": 0,
            "fuzzy_matches": 0,
            "llm_matches": 0,
            "cache_hits": 0
        }
    
    def _get_llm(self):
        """Lazy load LLM."""
        if self.llm is None:
            try:
                from langchain_community.llms import Ollama
                self.llm = Ollama(
                    base_url=OLLAMA_URL,
                    model=MODEL_NAME,
                    temperature=0.1
                )
            except Exception as e:
                self._log("llm_init_error", {"error": str(e)}, level="ERROR")
        return self.llm
    
    def match_products(
        self,
        products_by_platform: Dict[str, List[Product]]
    ) -> List[ProductMatch]:
        """
        Match products across platforms.
        
        Args:
            products_by_platform: Dict mapping platform ID to products
        
        Returns:
            List of ProductMatch groups
        """
        self._log("matching_start", {
            "platforms": list(products_by_platform.keys()),
            "product_counts": {k: len(v) for k, v in products_by_platform.items()}
        })
        
        # Flatten all products
        all_products = []
        for products in products_by_platform.values():
            all_products.extend(products)
        
        if not all_products:
            return []
        
        # Group by canonical name
        match_groups: Dict[str, ProductMatch] = {}
        
        for product in all_products:
            # Generate canonical key for this product
            canonical_key = self._get_canonical_key(product)
            
            # Try to find existing match group
            matched_key = self._find_matching_group(product, match_groups)
            
            if matched_key:
                # Add to existing group
                match_groups[matched_key].products.append(product)
                self._stats["fuzzy_matches"] += 1
            else:
                # Create new group
                match_groups[canonical_key] = ProductMatch(
                    id=f"match-{canonical_key}",
                    canonical_name=self._get_canonical_name(product),
                    brand=product.brand,
                    category=product.category,
                    products=[product],
                    match_confidence=1.0,
                    match_method="exact"
                )
                self._stats["exact_matches"] += 1
        
        # Calculate stats for each group
        matches = list(match_groups.values())
        for match in matches:
            match.calculate_stats()
        
        # Sort by number of platforms (more platforms = better comparison)
        matches.sort(key=lambda m: len(m.products), reverse=True)
        
        self._stats["total_matches"] += len(matches)
        
        self._log("matching_complete", {
            "groups_created": len(matches),
            "total_products": len(all_products)
        })
        
        return matches
    
    def _get_canonical_key(self, product: Product) -> str:
        """
        Generate a canonical key for product matching.
        
        Normalizes product name for consistent matching.
        """
        # Build key from brand, normalized name, and quantity
        parts = []
        
        # Add brand (lowercase)
        if product.brand:
            parts.append(product.brand.lower().strip())
        
        # Normalize product name
        name = product.name.lower()
        # Remove brand from name if present
        if product.brand:
            name = name.replace(product.brand.lower(), "").strip()
        
        # Remove common noise words
        noise_words = ["fresh", "premium", "organic", "natural", "pure"]
        for word in noise_words:
            name = name.replace(word, "").strip()
        
        # Clean up whitespace
        name = " ".join(name.split())
        parts.append(name)
        
        # Add quantity (normalized)
        quantity = product.quantity.lower().replace(" ", "")
        parts.append(quantity)
        
        # Create hash
        key_string = "|".join(parts)
        return hashlib.md5(key_string.encode()).hexdigest()[:12]
    
    def _get_canonical_name(self, product: Product) -> str:
        """Get a clean canonical name for the product."""
        name = product.name
        if product.brand and product.brand.lower() not in name.lower():
            name = f"{product.brand} {name}"
        return name
    
    def _find_matching_group(
        self,
        product: Product,
        existing_groups: Dict[str, ProductMatch]
    ) -> Optional[str]:
        """
        Find if product matches any existing group.
        
        Uses fuzzy matching to handle slight variations.
        
        Returns:
            Key of matching group, or None
        """
        if not existing_groups:
            return None
        
        product_name = self._normalize_for_matching(product)
        
        # Check each existing group
        for key, match in existing_groups.items():
            # Only match within same category
            if match.category != product.category:
                continue
            
            # Check if same brand (if both have brands)
            if product.brand and match.brand:
                if product.brand.lower() != match.brand.lower():
                    continue
            
            # Fuzzy match on canonical name
            existing_name = self._normalize_for_matching(match.products[0])
            
            score = fuzz.token_sort_ratio(product_name, existing_name)
            
            if score >= self.fuzzy_match_threshold:
                # Also verify quantity is similar
                if self._quantities_match(product.quantity, match.products[0].quantity):
                    return key
        
        return None
    
    def _normalize_for_matching(self, product: Product) -> str:
        """Normalize product name for fuzzy matching."""
        name = product.name.lower()
        
        # Remove brand if present (will be matched separately)
        if product.brand:
            name = name.replace(product.brand.lower(), "")
        
        # Remove punctuation and extra spaces
        name = "".join(c if c.isalnum() or c.isspace() else " " for c in name)
        name = " ".join(name.split())
        
        return name
    
    def _quantities_match(self, qty1: str, qty2: str) -> bool:
        """
        Check if two quantities are effectively the same.
        
        Handles variations like "1 L" vs "1 Litre" vs "1000 ml"
        """
        q1 = qty1.lower().replace(" ", "")
        q2 = qty2.lower().replace(" ", "")
        
        # Direct match
        if q1 == q2:
            return True
        
        # Convert common variations
        conversions = {
            "1l": ["1litre", "1liter", "1000ml"],
            "500ml": ["0.5l", "500millilitre"],
            "1kg": ["1000g", "1000gm", "1kilogram"],
            "500g": ["0.5kg", "500gm", "500gram"],
        }
        
        for canonical, variations in conversions.items():
            if q1 == canonical and q2 in variations:
                return True
            if q2 == canonical and q1 in variations:
                return True
            if q1 in variations and q2 in variations:
                return True
        
        return False
    
    def create_price_comparison(
        self,
        match: ProductMatch
    ) -> PriceComparison:
        """
        Create a PriceComparison from a ProductMatch.
        
        Converts matched products into a comparison-friendly format.
        """
        # Get image from first available product
        image_url = None
        for product in match.products:
            if product.image_url:
                image_url = product.image_url
                break
        
        comparison = PriceComparison(
            product_id=match.id,
            product_name=match.canonical_name,
            brand=match.brand,
            category=match.category.value,
            quantity=match.products[0].quantity if match.products else "",
            image_url=image_url,
            prices=[],
            pincode=match.products[0].location_pincode if match.products else None
        )
        
        # Convert each product to a price entry
        for product in match.products:
            platform_info = PLATFORMS.get(product.platform, {})
            
            entry = PriceEntry(
                product_id=match.id,
                platform=product.platform,
                platform_product_id=product.platform_product_id,
                product_name=product.name,
                brand=product.brand,
                quantity=product.quantity,
                image_url=product.image_url,
                price=product.current_price,
                mrp=product.mrp,
                discount_percent=product.discount_percent,
                price_per_unit=product.price_per_unit,
                is_available=product.is_available,
                stock_status=product.stock_status,
                delivery_time=platform_info.get("delivery_time", "Unknown"),
                platform_name=platform_info.get("name", product.platform),
                platform_logo=platform_info.get("logo", "🛒"),
                product_url=product.url,
                scraped_at=product.scraped_at,
                pincode=product.location_pincode
            )
            comparison.prices.append(entry)
        
        # Sort prices by price (cheapest first)
        comparison.prices.sort(key=lambda p: p.price if p.is_available else float('inf'))
        
        # Calculate comparison stats
        comparison.calculate_stats()
        
        return comparison
    
    def get_best_deal(
        self,
        comparisons: List[PriceComparison]
    ) -> Optional[PriceComparison]:
        """
        Find the product with the best savings potential.
        
        Returns the comparison with highest price variation.
        """
        if not comparisons:
            return None
        
        # Filter to comparisons with at least 2 platforms
        multi_platform = [c for c in comparisons if c.available_on >= 2]
        
        if not multi_platform:
            return comparisons[0] if comparisons else None
        
        # Sort by savings potential
        multi_platform.sort(key=lambda c: c.savings_potential, reverse=True)
        
        return multi_platform[0]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            **self._stats,
            "cache_size": len(self._match_cache)
        }
    
    def _log(self, event_type: str, data: Dict = None, level: str = "INFO") -> None:
        """Log an event."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "agent": "product_matcher",
            "event_type": event_type,
            "data": data or {}
        }
        
        log_file = LOGS_DIR / f"agent-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass


# Singleton instance
_product_matcher: Optional[ProductMatcherAgent] = None


def get_product_matcher() -> ProductMatcherAgent:
    """Get the singleton product matcher instance."""
    global _product_matcher
    if _product_matcher is None:
        _product_matcher = ProductMatcherAgent()
    return _product_matcher

