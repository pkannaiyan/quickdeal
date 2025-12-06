"""
QuickDeal Chatbot Service - AI-powered conversational interface.

Compare prices, negotiate deals, and find the best offers across quick commerce platforms.
"""
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import httpx

# LLM Configuration
OLLAMA_URL = "http://host.docker.internal:11434"
MODEL_NAME = "llama3:8b"


class IntentType(Enum):
    """User intent types."""
    SEARCH_PRODUCT = "search_product"
    COMPARE_PRICES = "compare_prices"
    FIND_DEALS = "find_deals"
    CHECK_AVAILABILITY = "check_availability"
    SET_ALERT = "set_alert"
    GET_CHEAPEST = "get_cheapest"
    PLATFORM_INFO = "platform_info"
    CATEGORY_BROWSE = "category_browse"
    ORDER_HELP = "order_help"
    BUY_NOW = "buy_now"
    QUICK_ORDER = "quick_order"
    ONE_CLICK_CHECKOUT = "one_click_checkout"
    NEGOTIATE_PRICE = "negotiate_price"
    CHECK_MY_OFFERS = "check_my_offers"
    CHECK_MY_DEALS = "check_my_deals"
    SELLER_DASHBOARD = "seller_dashboard"
    ADMIN_DASHBOARD = "admin_dashboard"
    GREETING = "greeting"
    HELP = "help"
    UNKNOWN = "unknown"


class ChatbotService:
    """
    AI-powered chatbot for price comparison assistance.
    Enhanced to search for any product.
    """
    
    def __init__(self):
        self.conversation_history: List[Dict] = []
        self.max_history = 10
        
        # Phrases that indicate search intent (NOT product names)
        self.search_phrases = [
            "search", "find", "show", "get", "look for", "looking for",
            "i want", "i need", "give me", "where can i", "price of",
            "cost of", "how much", "cheapest", "lowest", "best price",
            "compare", "comparison"
        ]
        
        # Non-product words to filter out
        self.stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "for", "of", "to", "in", "on", "at", "by", "with", "from",
            "please", "can", "could", "would", "should", "will", "shall",
            "i", "me", "my", "we", "our", "you", "your", "it", "its",
            "this", "that", "these", "those", "what", "which", "who",
            "how", "much", "many", "some", "any", "all", "both", "each",
            "price", "prices", "cost", "costs", "buy", "purchase", "get",
            "find", "search", "show", "give", "want", "need", "looking",
            "cheapest", "lowest", "best", "compare", "comparison", "vs",
            "and", "or", "but", "so", "if", "then", "else", "when", "where",
            "one", "click", "one-click", "oneclick", "quick", "fast", "instant",
            "checkout", "order", "now", "ordering"
        }
        
        # Platform names for detection
        self.platforms = ["blinkit", "zepto", "jiomart", "bigbasket", "instamart", "swiggy"]
        
        # Category keywords
        self.categories = {
            "dairy": "dairy_bread",
            "milk": "dairy_bread", 
            "bread": "dairy_bread",
            "butter": "dairy_bread",
            "cheese": "dairy_bread",
            "paneer": "dairy_bread",
            "curd": "dairy_bread",
            "yogurt": "dairy_bread",
            "snack": "snacks_beverages",
            "snacks": "snacks_beverages",
            "chips": "snacks_beverages",
            "biscuit": "snacks_beverages",
            "biscuits": "snacks_beverages",
            "chocolate": "snacks_beverages",
            "drink": "snacks_beverages",
            "drinks": "snacks_beverages",
            "beverage": "snacks_beverages",
            "beverages": "snacks_beverages",
            "juice": "snacks_beverages",
            "cola": "snacks_beverages",
            "coffee": "snacks_beverages",
            "tea": "snacks_beverages",
            "vegetable": "fruits_vegetables",
            "vegetables": "fruits_vegetables",
            "fruit": "fruits_vegetables",
            "fruits": "fruits_vegetables",
            "onion": "fruits_vegetables",
            "tomato": "fruits_vegetables",
            "potato": "fruits_vegetables",
            "staple": "staples",
            "staples": "staples",
            "rice": "staples",
            "dal": "staples",
            "atta": "staples",
            "flour": "staples",
            "oil": "staples",
            "sugar": "staples",
            "salt": "staples",
            "spice": "staples",
            "spices": "staples",
            "personal": "personal_care",
            "care": "personal_care",
            "shampoo": "personal_care",
            "soap": "personal_care",
            "toothpaste": "personal_care",
            "household": "household",
            "detergent": "household",
            "cleaner": "household",
        }
    
    def _extract_search_query(self, message: str) -> Optional[str]:
        """
        Extract the search query from user message.
        This is the MAIN improvement - extract any product/search term.
        """
        original = message
        message_lower = message.lower().strip()
        
        # Remove common question marks and punctuation
        message_lower = message_lower.rstrip('?!.')
        
        # Common patterns to extract product names
        patterns = [
            # "search for X", "find X", "show me X", "get X"
            r"(?:search|find|show|get|look)\s+(?:for|me)?\s*(.+)",
            # "price of X", "cost of X"
            r"(?:price|cost)\s+(?:of|for)\s+(.+)",
            # "how much is X", "how much does X cost"
            r"how\s+much\s+(?:is|does|for|are)\s+(.+)",
            # "I want X", "I need X"
            r"i\s+(?:want|need|looking for)\s+(.+)",
            # "cheapest X", "lowest price X", "best price for X"
            r"(?:cheapest|lowest\s+price|best\s+price)\s+(?:for|of|on)?\s*(.+)",
            # "compare X", "X comparison", "X vs"
            r"(?:compare|comparing)\s+(.+?)(?:\s+prices?|\s+across)?",
            # "where can I buy X", "where to buy X"
            r"where\s+(?:can\s+i|to)\s+(?:buy|get|find)\s+(.+)",
            # "X price", "X prices"
            r"(.+?)\s+prices?$",
            # "is X available", "do you have X"
            r"(?:is|do\s+you\s+have|any)\s+(.+?)\s+(?:available|in\s+stock)?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                query = match.group(1).strip()
                # Clean up the query
                query = self._clean_query(query)
                if query and len(query) >= 2:
                    return query
        
        # If no pattern matched, try to extract meaningful words
        # Remove stop words and see what's left
        words = message_lower.split()
        meaningful_words = [
            w for w in words 
            if w not in self.stop_words 
            and len(w) > 1
            and not w.isdigit()
        ]
        
        if meaningful_words:
            # Join remaining words as the search query
            query = ' '.join(meaningful_words)
            return self._clean_query(query) if len(query) >= 2 else None
        
        return None
    
    def _clean_query(self, query: str) -> str:
        """Clean up a search query."""
        # Remove leading/trailing whitespace and punctuation
        query = query.strip().strip('?!.,')
        
        # Remove platform names from query
        for platform in self.platforms:
            query = re.sub(rf'\b{platform}\b', '', query, flags=re.IGNORECASE)
        
        # Remove order-related words
        order_words = [
            r'one[\s-]?click', r'quick\s+order', r'fast\s+order', r'instant\s+buy',
            r'buy\s+now', r'purchase', r'order\s+now', r'checkout',
            r'want\s+to\s+buy', r'want\s+to\s+purchase', r'want\s+to\s+order',
            r'i\'ll\s+buy', r'i\s+want', r'i\s+need'
        ]
        for word in order_words:
            query = re.sub(rf'\b{word}\b', '', query, flags=re.IGNORECASE)
        
        # Remove common suffixes that aren't helpful
        query = re.sub(r'\s*(prices?|costs?|available|in\s+stock|on\s+sale)\s*$', '', query, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        query = ' '.join(query.split())
        
        return query
    
    def _detect_intent(self, message: str) -> Tuple[IntentType, Optional[str]]:
        """Detect user intent and extract search query."""
        message_lower = message.lower().strip()
        
        # Check for greetings
        greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon", "howdy", "hola"]
        if any(message_lower.startswith(g) or message_lower == g for g in greetings):
            return IntentType.GREETING, None
        
        # Check for help requests
        help_phrases = ["help", "what can you do", "how to use", "how does this work", "commands", "options"]
        if any(phrase in message_lower for phrase in help_phrases):
            return IntentType.HELP, None
        
        # Check for one-click checkout / quick buy
        one_click_phrases = ["one click", "oneclick", "one-click", "quick checkout", "fast checkout", "instant buy", "instant order"]
        if any(phrase in message_lower for phrase in one_click_phrases):
            query = self._extract_search_query(message)
            return IntentType.ONE_CLICK_CHECKOUT, query
        
        # Check for buy now
        buy_phrases = ["buy now", "purchase", "order now", "buy this", "get this", "i want to buy", "i'll buy", "buy it"]
        if any(phrase in message_lower for phrase in buy_phrases):
            query = self._extract_search_query(message)
            return IntentType.BUY_NOW, query
        
        # Check for quick order
        quick_order_phrases = ["quick order", "fast order", "order quickly", "add to cart"]
        if any(phrase in message_lower for phrase in quick_order_phrases):
            query = self._extract_search_query(message)
            return IntentType.QUICK_ORDER, query
        
        # Check for checking my offers/deals status
        my_offers_phrases = ["my offers", "my negotiations", "offer status", "my pending", "check offers", "pending offers"]
        if any(phrase in message_lower for phrase in my_offers_phrases):
            return IntentType.CHECK_MY_OFFERS, None
        
        # Check for my deals (completed purchases)
        my_deals_phrases = ["my deals", "my purchases", "completed deals", "buy history", "purchase history", "what i bought"]
        if any(phrase in message_lower for phrase in my_deals_phrases):
            return IntentType.CHECK_MY_DEALS, None
        
        # Check for seller dashboard
        seller_phrases = ["seller dashboard", "seller panel", "i am seller", "i'm a seller", "seller mode", "vendor dashboard"]
        if any(phrase in message_lower for phrase in seller_phrases):
            return IntentType.SELLER_DASHBOARD, None
        
        # Check for admin dashboard
        admin_phrases = ["admin dashboard", "admin panel", "admin mode", "admin view", "admin access"]
        if any(phrase in message_lower for phrase in admin_phrases):
            return IntentType.ADMIN_DASHBOARD, None
        
        # Check for negotiate price
        negotiate_phrases = [
            "negotiate", "bargain", "haggle", "make offer", "make an offer",
            "lower price", "better price", "discount please", "can you reduce",
            "reduce price", "less price", "offer price", "my price", "i offer",
            "willing to pay", "counter offer", "best offer", "negotiate price"
        ]
        if any(phrase in message_lower for phrase in negotiate_phrases):
            query = self._extract_search_query(message)
            return IntentType.NEGOTIATE_PRICE, query
        
        # Check for deals/offers
        deal_phrases = ["deals", "offers", "discounts", "sale", "on sale", "best deals", "today's deals"]
        if any(phrase in message_lower for phrase in deal_phrases):
            return IntentType.FIND_DEALS, None
        
        # Check for platform info
        for platform in self.platforms:
            if platform in message_lower and any(w in message_lower for w in ["about", "tell", "info", "information", "what is", "how is"]):
                return IntentType.PLATFORM_INFO, platform
        
        # Check for order/buy help
        order_phrases = ["how to order", "how to buy", "how do i order", "place order", "checkout"]
        if any(phrase in message_lower for phrase in order_phrases):
            return IntentType.ORDER_HELP, None
        
        # Check for price alert
        if "alert" in message_lower or "notify" in message_lower or "remind" in message_lower:
            query = self._extract_search_query(message)
            return IntentType.SET_ALERT, query
        
        # Check for cheapest/lowest price
        if any(word in message_lower for word in ["cheapest", "lowest", "minimum", "min price"]):
            query = self._extract_search_query(message)
            if query:
                return IntentType.GET_CHEAPEST, query
        
        # Check for comparison
        if any(word in message_lower for word in ["compare", "comparison", "versus", "vs", "difference"]):
            query = self._extract_search_query(message)
            if query:
                return IntentType.COMPARE_PRICES, query
        
        # Default: try to extract any product search
        query = self._extract_search_query(message)
        if query:
            return IntentType.SEARCH_PRODUCT, query
        
        # If message is very short (1-3 words), treat it as a search
        words = message_lower.split()
        if 1 <= len(words) <= 4:
            # Just use the message as search query
            clean_msg = self._clean_query(message_lower)
            if clean_msg and len(clean_msg) >= 2:
                return IntentType.SEARCH_PRODUCT, clean_msg
        
        return IntentType.UNKNOWN, None
    
    async def process_message(
        self, 
        message: str, 
        user_id: Optional[str] = None,
        location: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process a user message and return a response."""
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep history manageable
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        # Detect intent
        intent, query = self._detect_intent(message)
        
        # Generate response
        response = await self._generate_response(intent, query, message, location)
        
        # Add bot response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response["response"],
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    async def _generate_response(
        self, 
        intent: IntentType, 
        query: Optional[str],
        original_message: str,
        location: Optional[Dict]
    ) -> Dict[str, Any]:
        """Generate response based on intent."""
        
        if intent == IntentType.GREETING:
            return {
                "response": "👋 Hi! I'm your **Price Comparison Assistant**!\n\n"
                           "Just tell me what you want to find and I'll search across "
                           "**Blinkit, Zepto, Instamart, BigBasket & JioMart**.\n\n"
                           "**Try saying:**\n"
                           "• \"Amul milk\" or \"Maggi noodles\"\n"
                           "• \"cheapest bread\"\n"
                           "• \"compare rice prices\"\n"
                           "• \"show deals\"\n\n"
                           "What would you like to search for? 🛒",
                "intent": intent.value,
                "action": None,
                "data": None,
                "suggestions": ["Amul milk", "Maggi noodles", "Lays chips", "Show deals"]
            }
        
        elif intent == IntentType.HELP:
            return {
                "response": "⚡ **Welcome to QuickDeal!**\n\n"
                           "I help you **compare prices** & **negotiate deals** across 5 platforms.\n\n"
                           "**🔍 Search Products:**\n"
                           "• `Amul butter`, `Maggi`, `eggs`\n"
                           "• `cheapest milk`, `compare chips`\n\n"
                           "**🤝 Negotiate & Buy:**\n"
                           "• `negotiate milk` - Make an offer\n"
                           "• `bargain bread` - Haggle for discount\n"
                           "• `one-click eggs` - Instant checkout\n"
                           "• `buy now milk` - Quick purchase\n\n"
                           "**📋 Track Orders:**\n"
                           "• `my offers` - Check negotiation status\n"
                           "• `my deals` - View completed deals + One-Click Buy\n\n"
                           "**📊 Dashboards:**\n"
                           "• `seller dashboard` - Seller panel\n"
                           "• `admin dashboard` - Admin access\n\n"
                           "**🎁 Deals:**\n"
                           "• `show deals` - Today's best offers\n\n"
                           "💡 Just type any product name!",
                "intent": intent.value,
                "action": None,
                "data": None,
                "suggestions": ["My deals", "My offers", "Show deals", "Help"]
            }
        
        elif intent == IntentType.SEARCH_PRODUCT:
            if query:
                return {
                    "response": f"🔍 **Searching for \"{query}\"**\n\n"
                               f"Looking across Blinkit, Zepto, Instamart, BigBasket & JioMart...",
                    "intent": intent.value,
                    "action": "search",
                    "data": {"query": query},
                    "suggestions": [f"Cheapest {query}", f"Compare {query}", "More options"]
                }
            else:
                return {
                    "response": "🛒 What product would you like me to search for?\n\n"
                               "Just type any product name like:\n"
                               "• `Amul milk`\n"
                               "• `Maggi noodles`\n"
                               "• `Head & Shoulders shampoo`",
                    "intent": intent.value,
                    "action": None,
                    "data": None,
                    "suggestions": ["Milk", "Bread", "Rice", "Eggs", "Chips"]
                }
        
        elif intent == IntentType.COMPARE_PRICES:
            if query:
                return {
                    "response": f"📊 **Comparing \"{query}\" across platforms...**\n\n"
                               f"I'll find which platform has the best price!",
                    "intent": intent.value,
                    "action": "search",
                    "data": {"query": query, "compare": True},
                    "suggestions": [f"Buy {query}", f"Cheapest {query}", "Set price alert"]
                }
            else:
                return {
                    "response": "📊 Which product would you like to compare?\n\n"
                               "Example: `compare rice prices`",
                    "intent": intent.value,
                    "action": None,
                    "data": None,
                    "suggestions": ["Compare milk", "Compare bread", "Compare chips"]
                }
        
        elif intent == IntentType.FIND_DEALS:
            return {
                "response": "🔥 **Loading today's best deals...**\n\n"
                           "Finding products with the biggest discounts!",
                "intent": intent.value,
                "action": "deals",
                "data": None,
                "suggestions": ["Dairy deals", "Snacks deals", "Search specific product"]
            }
        
        elif intent == IntentType.ONE_CLICK_CHECKOUT:
            if query:
                return {
                    "response": f"⚡ **One-Click Checkout for \"{query}\"**\n\n"
                               f"Searching for the product and opening checkout...",
                    "intent": intent.value,
                    "action": "one_click_checkout",
                    "data": {"query": query},
                    "suggestions": ["Change quantity", "Pick platform", "Cancel"]
                }
            else:
                return {
                    "response": "⚡ **One-Click Checkout**\n\n"
                               "What would you like to buy?\n\n"
                               "Say something like:\n"
                               "• `One-click buy Amul milk`\n"
                               "• `Quick checkout bread`",
                    "intent": intent.value,
                    "action": None,
                    "data": None,
                    "suggestions": ["One-click milk", "One-click bread", "Show deals"]
                }
        
        elif intent == IntentType.BUY_NOW:
            if query:
                return {
                    "response": f"🛒 **Buy Now: \"{query}\"**\n\n"
                               f"Opening the best platform to purchase...",
                    "intent": intent.value,
                    "action": "buy_now",
                    "data": {"query": query},
                    "suggestions": ["Compare prices first", "Show more options"]
                }
            else:
                return {
                    "response": "🛒 **Ready to buy!**\n\n"
                               "What would you like to purchase?\n\n"
                               "Say: `Buy milk` or `Purchase bread`",
                    "intent": intent.value,
                    "action": None,
                    "data": None,
                    "suggestions": ["Buy milk", "Buy bread", "Buy eggs"]
                }
        
        elif intent == IntentType.QUICK_ORDER:
            if query:
                return {
                    "response": f"⚡ **Quick Order: \"{query}\"**\n\n"
                               f"Finding the best deal and preparing your order...",
                    "intent": intent.value,
                    "action": "quick_order",
                    "data": {"query": query},
                    "suggestions": ["Change platform", "Add more items"]
                }
            else:
                return {
                    "response": "⚡ **Quick Order**\n\n"
                               "What would you like to order?\n\n"
                               "Say: `Quick order Maggi` or `Fast order chips`",
                    "intent": intent.value,
                    "action": None,
                    "data": None,
                    "suggestions": ["Quick order milk", "Quick order Maggi"]
                }
        
        elif intent == IntentType.NEGOTIATE_PRICE:
            if query:
                return {
                    "response": f"🤝 **Negotiate Price: \"{query}\"**\n\n"
                               f"Opening negotiation for this product...\n\n"
                               f"You can make an offer below the listed price!\n"
                               f"• Suggest a discount (5-20% typically accepted)\n"
                               f"• Seller has 5 mins to respond\n"
                               f"• If no response, auto-rules apply",
                    "intent": intent.value,
                    "action": "negotiate",
                    "data": {"query": query},
                    "suggestions": ["Offer 10% off", "Offer 15% off", "Skip negotiation"]
                }
            else:
                return {
                    "response": "🤝 **Negotiate a Better Price!**\n\n"
                               "Want a better deal? I can help you negotiate!\n\n"
                               "Tell me what product you want to negotiate for:\n"
                               "• `Negotiate price for milk`\n"
                               "• `Make offer on bread`\n"
                               "• `Bargain for rice`",
                    "intent": intent.value,
                    "action": None,
                    "data": None,
                    "suggestions": ["Negotiate milk", "Negotiate eggs", "Negotiate bread"]
                }
        
        elif intent == IntentType.CHECK_MY_OFFERS:
            return {
                "response": "📋 **Your Offers & Negotiations**\n\n"
                           "Opening your buyer dashboard...\n\n"
                           "You'll see:\n"
                           "• ⏳ Pending offers waiting for seller\n"
                           "• 🔄 Counter-offers from sellers\n"
                           "• ✅ Accepted offers ready to buy\n"
                           "• ❌ Rejected offers",
                "intent": intent.value,
                "action": "open_buyer_dashboard",
                "data": {"tab": "offers"},
                "suggestions": ["Check my deals", "Make new offer", "Search products"]
            }
        
        elif intent == IntentType.CHECK_MY_DEALS:
            return {
                "response": "🎉 **Your Completed Deals**\n\n"
                           "Opening your deals dashboard...\n\n"
                           "Here you can:\n"
                           "• View negotiated deals with savings\n"
                           "• ⚡ **One-Click Buy** at your agreed price\n"
                           "• Track your purchase history",
                "intent": intent.value,
                "action": "open_buyer_dashboard",
                "data": {"tab": "deals"},
                "suggestions": ["One-click buy", "Check offers", "Search more"]
            }
        
        elif intent == IntentType.SELLER_DASHBOARD:
            return {
                "response": "🏪 **Seller Dashboard**\n\n"
                           "Opening seller panel...\n\n"
                           "As a seller you can:\n"
                           "• View pending offers\n"
                           "• Accept, reject, or counter offers\n"
                           "• Set auto-accept/reject rules\n"
                           "• Track your deals & revenue",
                "intent": intent.value,
                "action": "open_seller_dashboard",
                "data": None,
                "suggestions": ["View pending", "Check stats", "Settings"]
            }
        
        elif intent == IntentType.ADMIN_DASHBOARD:
            return {
                "response": "👑 **Admin Dashboard**\n\n"
                           "Opening admin panel...\n\n"
                           "Admin access includes:\n"
                           "• View ALL offers across platforms\n"
                           "• Accept/reject on behalf of sellers\n"
                           "• Platform-wise statistics\n"
                           "• Complete system overview",
                "intent": intent.value,
                "action": "open_admin_dashboard",
                "data": None,
                "suggestions": ["View all offers", "Platform stats", "Recent deals"]
            }
        
        elif intent == IntentType.GET_CHEAPEST:
            if query:
                return {
                    "response": f"💰 **Finding cheapest \"{query}\"...**\n\n"
                               f"Checking all platforms for the lowest price!",
                    "intent": intent.value,
                    "action": "search",
                    "data": {"query": query, "sort": "price"},
                    "suggestions": [f"Buy {query} now", f"Compare {query}", "Set alert"]
                }
            else:
                return {
                    "response": "💰 What product do you want the cheapest price for?\n\n"
                               "Example: `cheapest eggs`",
                    "intent": intent.value,
                    "action": None,
                    "data": None,
                    "suggestions": ["Cheapest milk", "Cheapest bread", "Cheapest rice"]
                }
        
        elif intent == IntentType.PLATFORM_INFO:
            platform_info = self._get_platform_info(query)
            return {
                "response": platform_info,
                "intent": intent.value,
                "action": None,
                "data": {"platform": query},
                "suggestions": ["Compare platforms", "Fastest delivery?", "Search product"]
            }
        
        elif intent == IntentType.SET_ALERT:
            if query:
                return {
                    "response": f"🔔 **Setting price alert for \"{query}\"**\n\n"
                               f"What price would you like to be notified at?",
                    "intent": intent.value,
                    "action": "set_alert",
                    "data": {"product": query},
                    "suggestions": ["Under ₹50", "Under ₹100", "20% off or more"]
                }
            else:
                return {
                    "response": "🔔 Which product would you like alerts for?\n\n"
                               "Example: `alert me when rice is under ₹100`",
                    "intent": intent.value,
                    "action": None,
                    "data": None,
                    "suggestions": ["Alert for milk", "Alert for eggs"]
                }
        
        elif intent == IntentType.ORDER_HELP:
            return {
                "response": "🛒 **How to order:**\n\n"
                           "1️⃣ Search for your product\n"
                           "2️⃣ I'll show prices from all platforms\n"
                           "3️⃣ Click **'Quick Order'** or **'Buy Now'**\n"
                           "4️⃣ Complete purchase on the platform\n\n"
                           "What would you like to buy?",
                "intent": intent.value,
                "action": None,
                "data": None,
                "suggestions": ["Search milk", "Search bread", "Show deals"]
            }
        
        else:  # UNKNOWN - try to treat as search anyway
            # Last attempt: use the entire message as a search query
            clean_msg = self._clean_query(original_message.lower())
            if clean_msg and len(clean_msg) >= 2:
                return {
                    "response": f"🔍 **Searching for \"{clean_msg}\"...**\n\n"
                               f"Looking across all platforms!",
                    "intent": "search_product",
                    "action": "search",
                    "data": {"query": clean_msg},
                    "suggestions": [f"Cheapest {clean_msg}", "Show deals", "Help"]
                }
            
            return {
                "response": "🤔 I can search for any product!\n\n"
                           "Just type what you're looking for:\n"
                           "• `Amul milk`\n"
                           "• `Maggi noodles`\n"
                           "• `Dove soap`\n"
                           "• `cheapest eggs`\n"
                           "• `show deals`\n\n"
                           "Or click a suggestion below! 👇",
                "intent": intent.value,
                "action": None,
                "data": None,
                "suggestions": ["Amul milk", "Maggi", "Chips", "Show deals"]
            }
    
    def _get_platform_info(self, platform: Optional[str]) -> str:
        """Get information about a platform."""
        info = {
            "blinkit": (
                "🟢 **Blinkit** (formerly Grofers)\n\n"
                "⏱️ **Delivery:** 10-20 minutes\n"
                "📍 **Coverage:** Major cities\n"
                "💰 **Prices:** Mid to High\n"
                "✨ **Best for:** Ultra-fast delivery\n\n"
                "Owned by Zomato!"
            ),
            "zepto": (
                "🟣 **Zepto**\n\n"
                "⏱️ **Delivery:** 10 minutes\n"
                "📍 **Coverage:** Metro cities\n"
                "💰 **Prices:** Competitive\n"
                "✨ **Best for:** Fastest delivery in India!\n\n"
                "India's 10-minute delivery pioneer."
            ),
            "jiomart": (
                "🔵 **JioMart**\n\n"
                "⏱️ **Delivery:** Same/Next day\n"
                "📍 **Coverage:** Pan India\n"
                "💰 **Prices:** Often the lowest!\n"
                "✨ **Best for:** Best prices & bulk buying\n\n"
                "By Reliance - great discounts!"
            ),
            "bigbasket": (
                "🟢 **BigBasket**\n\n"
                "⏱️ **Delivery:** Same day / Scheduled\n"
                "📍 **Coverage:** Pan India\n"
                "💰 **Prices:** Competitive, bulk discounts\n"
                "✨ **Best for:** Wide selection\n\n"
                "Owned by Tata - India's largest!"
            ),
            "instamart": (
                "🟠 **Swiggy Instamart**\n\n"
                "⏱️ **Delivery:** 15-30 minutes\n"
                "📍 **Coverage:** 500+ cities\n"
                "💰 **Prices:** Mid-range\n"
                "✨ **Best for:** Good variety + speed\n\n"
                "From the Swiggy food delivery app!"
            ),
        }
        
        if platform and platform in info:
            return info[platform]
        
        return (
            "📱 **Quick Commerce Platforms:**\n\n"
            "🟢 **Blinkit** - 10-20 min\n"
            "🟣 **Zepto** - 10 min (fastest!)\n"
            "🟠 **Instamart** - 15-30 min\n"
            "🟢 **BigBasket** - Same day\n"
            "🔵 **JioMart** - Lowest prices!\n\n"
            "Ask about any specific platform!"
        )
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


# Singleton instance
_chatbot_service: Optional[ChatbotService] = None


def get_chatbot_service() -> ChatbotService:
    """Get the singleton chatbot service instance."""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    return _chatbot_service
