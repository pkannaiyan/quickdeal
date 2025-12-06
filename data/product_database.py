"""
Expanded Product Database for Demo Mode.

Contains a comprehensive list of products across categories
to enable realistic search functionality.
"""

# Category-based placeholder images (using picsum.photos with seed for consistency)
CATEGORY_IMAGES = {
    "dairy_bread": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=200&h=200&fit=crop",  # Milk
    "snacks_beverages": "https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=200&h=200&fit=crop",  # Snacks
    "fruits_vegetables": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=200&h=200&fit=crop",  # Fruits
    "staples": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=200&h=200&fit=crop",  # Rice
    "personal_care": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=200&h=200&fit=crop",  # Personal care
    "household": "https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=200&h=200&fit=crop",  # Cleaning
}

# Product-specific images (for popular items)
PRODUCT_IMAGES = {
    "amul": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=200&h=200&fit=crop",
    "milk": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=200&h=200&fit=crop",
    "bread": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=200&h=200&fit=crop",
    "butter": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=200&h=200&fit=crop",
    "cheese": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=200&h=200&fit=crop",
    "paneer": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=200&h=200&fit=crop",
    "curd": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=200&h=200&fit=crop",
    "ghee": "https://images.unsplash.com/photo-1631452180539-96aca4d03fc1?w=200&h=200&fit=crop",
    "chips": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=200&h=200&fit=crop",
    "lays": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=200&h=200&fit=crop",
    "biscuit": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=200&h=200&fit=crop",
    "cookie": "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=200&h=200&fit=crop",
    "chocolate": "https://images.unsplash.com/photo-1511381939415-e44015466834?w=200&h=200&fit=crop",
    "coca-cola": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=200&h=200&fit=crop",
    "pepsi": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=200&h=200&fit=crop",
    "sprite": "https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?w=200&h=200&fit=crop",
    "maggi": "https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=200&h=200&fit=crop",
    "noodles": "https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=200&h=200&fit=crop",
    "coffee": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=200&h=200&fit=crop",
    "tea": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=200&h=200&fit=crop",
    "juice": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=200&h=200&fit=crop",
    "water": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=200&h=200&fit=crop",
    "rice": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=200&h=200&fit=crop",
    "atta": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=200&h=200&fit=crop",
    "flour": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=200&h=200&fit=crop",
    "oil": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=200&h=200&fit=crop",
    "sugar": "https://images.unsplash.com/photo-1581268378852-8b7dd9b5aa42?w=200&h=200&fit=crop",
    "salt": "https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=200&h=200&fit=crop",
    "dal": "https://images.unsplash.com/photo-1596097635121-14b63b7a0c29?w=200&h=200&fit=crop",
    "onion": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=200&h=200&fit=crop",
    "tomato": "https://images.unsplash.com/photo-1546470427-e26264be0b0c?w=200&h=200&fit=crop",
    "potato": "https://images.unsplash.com/photo-1518977676601-b53f82ber53f?w=200&h=200&fit=crop",
    "banana": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=200&h=200&fit=crop",
    "apple": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=200&h=200&fit=crop",
    "orange": "https://images.unsplash.com/photo-1547514701-42782101795e?w=200&h=200&fit=crop",
    "mango": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=200&h=200&fit=crop",
    "grapes": "https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=200&h=200&fit=crop",
    "egg": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=200&h=200&fit=crop",
    "eggs": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=200&h=200&fit=crop",
    "shampoo": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=200&h=200&fit=crop",
    "soap": "https://images.unsplash.com/photo-1584305574647-0cc949a2bb9f?w=200&h=200&fit=crop",
    "toothpaste": "https://images.unsplash.com/photo-1609840114035-3c981b782dfe?w=200&h=200&fit=crop",
    "detergent": "https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=200&h=200&fit=crop",
    "cleaner": "https://images.unsplash.com/photo-1563453392212-326f5e854473?w=200&h=200&fit=crop",
}

def get_product_image(product_name: str, category: str = None) -> str:
    """Get an appropriate image URL for a product."""
    name_lower = product_name.lower()
    
    # Check for product-specific images
    for keyword, url in PRODUCT_IMAGES.items():
        if keyword in name_lower:
            return url
    
    # Fall back to category image
    if category and category in CATEGORY_IMAGES:
        return CATEGORY_IMAGES[category]
    
    # Default placeholder
    return f"https://via.placeholder.com/200x200.png?text={product_name[:10]}"

# Comprehensive product database
PRODUCT_DATABASE = [
    # === DAIRY & BREAD ===
    {"name": "Amul Taaza Toned Fresh Milk", "brand": "Amul", "category": "dairy_bread", "quantity": "1 L", "base_price": 64, "mrp": 68},
    {"name": "Amul Gold Full Cream Milk", "brand": "Amul", "category": "dairy_bread", "quantity": "1 L", "base_price": 72, "mrp": 74},
    {"name": "Mother Dairy Milk", "brand": "Mother Dairy", "category": "dairy_bread", "quantity": "1 L", "base_price": 63, "mrp": 66},
    {"name": "Amul Butter", "brand": "Amul", "category": "dairy_bread", "quantity": "500 g", "base_price": 265, "mrp": 280},
    {"name": "Amul Cheese Slices", "brand": "Amul", "category": "dairy_bread", "quantity": "200 g", "base_price": 125, "mrp": 135},
    {"name": "Britannia Brown Bread", "brand": "Britannia", "category": "dairy_bread", "quantity": "400 g", "base_price": 42, "mrp": 48},
    {"name": "Britannia White Bread", "brand": "Britannia", "category": "dairy_bread", "quantity": "400 g", "base_price": 38, "mrp": 42},
    {"name": "Amul Paneer", "brand": "Amul", "category": "dairy_bread", "quantity": "200 g", "base_price": 90, "mrp": 95},
    {"name": "Mother Dairy Curd", "brand": "Mother Dairy", "category": "dairy_bread", "quantity": "400 g", "base_price": 40, "mrp": 45},
    {"name": "Amul Fresh Cream", "brand": "Amul", "category": "dairy_bread", "quantity": "200 ml", "base_price": 55, "mrp": 60},
    {"name": "Amul Ghee", "brand": "Amul", "category": "dairy_bread", "quantity": "1 L", "base_price": 560, "mrp": 595},
    {"name": "Nestle A+ Slim Milk", "brand": "Nestle", "category": "dairy_bread", "quantity": "1 L", "base_price": 68, "mrp": 72},
    {"name": "Epigamia Greek Yogurt", "brand": "Epigamia", "category": "dairy_bread", "quantity": "90 g", "base_price": 45, "mrp": 50},
    {"name": "Harvest Gold Bread", "brand": "Harvest Gold", "category": "dairy_bread", "quantity": "450 g", "base_price": 45, "mrp": 50},
    
    # === SNACKS & BEVERAGES ===
    {"name": "Parle-G Gold Biscuits", "brand": "Parle", "category": "snacks_beverages", "quantity": "1 kg", "base_price": 95, "mrp": 110},
    {"name": "Britannia Good Day Butter Cookies", "brand": "Britannia", "category": "snacks_beverages", "quantity": "600 g", "base_price": 130, "mrp": 145},
    {"name": "Lays Classic Salted Chips", "brand": "Lays", "category": "snacks_beverages", "quantity": "177 g", "base_price": 38, "mrp": 40},
    {"name": "Lays India's Magic Masala", "brand": "Lays", "category": "snacks_beverages", "quantity": "177 g", "base_price": 38, "mrp": 40},
    {"name": "Kurkure Masala Munch", "brand": "Kurkure", "category": "snacks_beverages", "quantity": "115 g", "base_price": 28, "mrp": 30},
    {"name": "Coca-Cola Soft Drink", "brand": "Coca-Cola", "category": "snacks_beverages", "quantity": "2.25 L", "base_price": 95, "mrp": 100},
    {"name": "Pepsi Soft Drink", "brand": "Pepsi", "category": "snacks_beverages", "quantity": "2.25 L", "base_price": 95, "mrp": 100},
    {"name": "Sprite Soft Drink", "brand": "Sprite", "category": "snacks_beverages", "quantity": "2.25 L", "base_price": 95, "mrp": 100},
    {"name": "Thumbs Up Soft Drink", "brand": "Thumbs Up", "category": "snacks_beverages", "quantity": "2.25 L", "base_price": 95, "mrp": 100},
    {"name": "Maggi 2-Minute Noodles", "brand": "Maggi", "category": "snacks_beverages", "quantity": "560 g (Pack of 8)", "base_price": 94, "mrp": 104},
    {"name": "Maggi Masala Noodles Family Pack", "brand": "Maggi", "category": "snacks_beverages", "quantity": "840 g", "base_price": 150, "mrp": 165},
    {"name": "Red Bull Energy Drink", "brand": "Red Bull", "category": "snacks_beverages", "quantity": "250 ml", "base_price": 110, "mrp": 125},
    {"name": "Monster Energy Drink", "brand": "Monster", "category": "snacks_beverages", "quantity": "350 ml", "base_price": 125, "mrp": 135},
    {"name": "Haldiram's Aloo Bhujia", "brand": "Haldiram's", "category": "snacks_beverages", "quantity": "400 g", "base_price": 130, "mrp": 150},
    {"name": "Haldiram's Namkeen Mix", "brand": "Haldiram's", "category": "snacks_beverages", "quantity": "350 g", "base_price": 95, "mrp": 110},
    {"name": "Paper Boat Aam Panna", "brand": "Paper Boat", "category": "snacks_beverages", "quantity": "1 L", "base_price": 85, "mrp": 99},
    {"name": "Tropicana Orange Juice", "brand": "Tropicana", "category": "snacks_beverages", "quantity": "1 L", "base_price": 110, "mrp": 125},
    {"name": "Real Fruit Juice Mixed Fruit", "brand": "Real", "category": "snacks_beverages", "quantity": "1 L", "base_price": 99, "mrp": 115},
    {"name": "Bingo Mad Angles", "brand": "Bingo", "category": "snacks_beverages", "quantity": "130 g", "base_price": 28, "mrp": 30},
    {"name": "Uncle Chipps", "brand": "Uncle Chipps", "category": "snacks_beverages", "quantity": "150 g", "base_price": 35, "mrp": 40},
    {"name": "Oreo Biscuits", "brand": "Oreo", "category": "snacks_beverages", "quantity": "300 g", "base_price": 65, "mrp": 75},
    {"name": "Dairy Milk Silk Chocolate", "brand": "Cadbury", "category": "snacks_beverages", "quantity": "150 g", "base_price": 160, "mrp": 175},
    {"name": "Dairy Milk Chocolate", "brand": "Cadbury", "category": "snacks_beverages", "quantity": "110 g", "base_price": 80, "mrp": 90},
    {"name": "KitKat Chocolate", "brand": "Nestle", "category": "snacks_beverages", "quantity": "36.5 g (Pack of 4)", "base_price": 90, "mrp": 100},
    {"name": "5 Star Chocolate", "brand": "Cadbury", "category": "snacks_beverages", "quantity": "40 g (Pack of 6)", "base_price": 90, "mrp": 100},
    {"name": "Ferrero Rocher", "brand": "Ferrero", "category": "snacks_beverages", "quantity": "16 pieces", "base_price": 540, "mrp": 599},
    {"name": "Bournvita Health Drink", "brand": "Cadbury", "category": "snacks_beverages", "quantity": "500 g", "base_price": 245, "mrp": 270},
    {"name": "Horlicks Health Drink", "brand": "Horlicks", "category": "snacks_beverages", "quantity": "500 g", "base_price": 265, "mrp": 285},
    {"name": "Nescafe Classic Coffee", "brand": "Nescafe", "category": "snacks_beverages", "quantity": "200 g", "base_price": 450, "mrp": 499},
    {"name": "Bru Instant Coffee", "brand": "Bru", "category": "snacks_beverages", "quantity": "200 g", "base_price": 420, "mrp": 460},
    {"name": "Tata Tea Premium", "brand": "Tata", "category": "snacks_beverages", "quantity": "500 g", "base_price": 235, "mrp": 260},
    {"name": "Red Label Tea", "brand": "Brooke Bond", "category": "snacks_beverages", "quantity": "500 g", "base_price": 240, "mrp": 265},
    {"name": "Lipton Green Tea", "brand": "Lipton", "category": "snacks_beverages", "quantity": "25 bags", "base_price": 135, "mrp": 150},
    {"name": "Bisleri Mineral Water", "brand": "Bisleri", "category": "snacks_beverages", "quantity": "1 L", "base_price": 20, "mrp": 22},
    {"name": "Kinley Water", "brand": "Kinley", "category": "snacks_beverages", "quantity": "1 L", "base_price": 18, "mrp": 20},
    
    # === FRUITS & VEGETABLES ===
    {"name": "Fresh Onion", "brand": None, "category": "fruits_vegetables", "quantity": "1 kg", "base_price": 32, "mrp": 40},
    {"name": "Fresh Tomato", "brand": None, "category": "fruits_vegetables", "quantity": "1 kg", "base_price": 38, "mrp": 45},
    {"name": "Fresh Potato", "brand": None, "category": "fruits_vegetables", "quantity": "1 kg", "base_price": 28, "mrp": 35},
    {"name": "Fresh Banana", "brand": None, "category": "fruits_vegetables", "quantity": "1 dozen", "base_price": 52, "mrp": 60},
    {"name": "Fresh Apple", "brand": None, "category": "fruits_vegetables", "quantity": "1 kg", "base_price": 180, "mrp": 200},
    {"name": "Fresh Orange", "brand": None, "category": "fruits_vegetables", "quantity": "1 kg", "base_price": 120, "mrp": 140},
    {"name": "Fresh Mango", "brand": None, "category": "fruits_vegetables", "quantity": "1 kg", "base_price": 150, "mrp": 180},
    {"name": "Fresh Grapes", "brand": None, "category": "fruits_vegetables", "quantity": "500 g", "base_price": 85, "mrp": 100},
    {"name": "Fresh Watermelon", "brand": None, "category": "fruits_vegetables", "quantity": "1 kg", "base_price": 35, "mrp": 40},
    {"name": "Fresh Papaya", "brand": None, "category": "fruits_vegetables", "quantity": "1 kg", "base_price": 45, "mrp": 55},
    {"name": "Green Capsicum", "brand": None, "category": "fruits_vegetables", "quantity": "500 g", "base_price": 55, "mrp": 65},
    {"name": "Fresh Carrot", "brand": None, "category": "fruits_vegetables", "quantity": "500 g", "base_price": 35, "mrp": 42},
    {"name": "Fresh Cucumber", "brand": None, "category": "fruits_vegetables", "quantity": "500 g", "base_price": 25, "mrp": 30},
    {"name": "Fresh Spinach", "brand": None, "category": "fruits_vegetables", "quantity": "250 g", "base_price": 22, "mrp": 28},
    {"name": "Fresh Coriander", "brand": None, "category": "fruits_vegetables", "quantity": "100 g", "base_price": 15, "mrp": 20},
    {"name": "Fresh Ginger", "brand": None, "category": "fruits_vegetables", "quantity": "100 g", "base_price": 25, "mrp": 30},
    {"name": "Fresh Garlic", "brand": None, "category": "fruits_vegetables", "quantity": "250 g", "base_price": 65, "mrp": 75},
    {"name": "Fresh Lemon", "brand": None, "category": "fruits_vegetables", "quantity": "500 g", "base_price": 60, "mrp": 70},
    {"name": "Fresh Green Chilli", "brand": None, "category": "fruits_vegetables", "quantity": "100 g", "base_price": 15, "mrp": 20},
    {"name": "Fresh Lady Finger", "brand": None, "category": "fruits_vegetables", "quantity": "500 g", "base_price": 45, "mrp": 55},
    {"name": "Fresh Brinjal", "brand": None, "category": "fruits_vegetables", "quantity": "500 g", "base_price": 35, "mrp": 42},
    {"name": "Fresh Cauliflower", "brand": None, "category": "fruits_vegetables", "quantity": "1 pc", "base_price": 38, "mrp": 45},
    {"name": "Fresh Cabbage", "brand": None, "category": "fruits_vegetables", "quantity": "1 pc", "base_price": 32, "mrp": 38},
    {"name": "Fresh Pomegranate", "brand": None, "category": "fruits_vegetables", "quantity": "500 g", "base_price": 130, "mrp": 150},
    {"name": "Fresh Kiwi", "brand": None, "category": "fruits_vegetables", "quantity": "3 pcs", "base_price": 140, "mrp": 160},
    
    # === STAPLES ===
    {"name": "Aashirvaad Atta", "brand": "Aashirvaad", "category": "staples", "quantity": "5 kg", "base_price": 280, "mrp": 305},
    {"name": "Aashirvaad Multigrain Atta", "brand": "Aashirvaad", "category": "staples", "quantity": "5 kg", "base_price": 310, "mrp": 340},
    {"name": "Fortune Chakki Fresh Atta", "brand": "Fortune", "category": "staples", "quantity": "5 kg", "base_price": 265, "mrp": 290},
    {"name": "Fortune Rice Bran Oil", "brand": "Fortune", "category": "staples", "quantity": "5 L", "base_price": 780, "mrp": 845},
    {"name": "Saffola Gold Oil", "brand": "Saffola", "category": "staples", "quantity": "5 L", "base_price": 950, "mrp": 1025},
    {"name": "Fortune Sunflower Oil", "brand": "Fortune", "category": "staples", "quantity": "5 L", "base_price": 720, "mrp": 785},
    {"name": "Tata Salt", "brand": "Tata", "category": "staples", "quantity": "1 kg", "base_price": 26, "mrp": 28},
    {"name": "Tata Salt Lite", "brand": "Tata", "category": "staples", "quantity": "1 kg", "base_price": 38, "mrp": 42},
    {"name": "India Gate Basmati Rice", "brand": "India Gate", "category": "staples", "quantity": "5 kg", "base_price": 650, "mrp": 720},
    {"name": "Daawat Basmati Rice", "brand": "Daawat", "category": "staples", "quantity": "5 kg", "base_price": 580, "mrp": 650},
    {"name": "Tata Sampann Toor Dal", "brand": "Tata", "category": "staples", "quantity": "1 kg", "base_price": 175, "mrp": 195},
    {"name": "Tata Sampann Chana Dal", "brand": "Tata", "category": "staples", "quantity": "1 kg", "base_price": 135, "mrp": 150},
    {"name": "Tata Sampann Moong Dal", "brand": "Tata", "category": "staples", "quantity": "1 kg", "base_price": 165, "mrp": 185},
    {"name": "Tata Sampann Masoor Dal", "brand": "Tata", "category": "staples", "quantity": "1 kg", "base_price": 125, "mrp": 140},
    {"name": "Sugar", "brand": None, "category": "staples", "quantity": "1 kg", "base_price": 45, "mrp": 50},
    {"name": "MDH Garam Masala", "brand": "MDH", "category": "staples", "quantity": "100 g", "base_price": 75, "mrp": 85},
    {"name": "MDH Chana Masala", "brand": "MDH", "category": "staples", "quantity": "100 g", "base_price": 62, "mrp": 70},
    {"name": "Everest Meat Masala", "brand": "Everest", "category": "staples", "quantity": "100 g", "base_price": 70, "mrp": 80},
    {"name": "Catch Turmeric Powder", "brand": "Catch", "category": "staples", "quantity": "200 g", "base_price": 58, "mrp": 65},
    {"name": "Catch Red Chilli Powder", "brand": "Catch", "category": "staples", "quantity": "200 g", "base_price": 75, "mrp": 85},
    {"name": "Catch Coriander Powder", "brand": "Catch", "category": "staples", "quantity": "200 g", "base_price": 68, "mrp": 78},
    {"name": "Besan (Gram Flour)", "brand": None, "category": "staples", "quantity": "1 kg", "base_price": 95, "mrp": 110},
    {"name": "Maida (Refined Flour)", "brand": None, "category": "staples", "quantity": "1 kg", "base_price": 48, "mrp": 55},
    {"name": "Sooji (Semolina)", "brand": None, "category": "staples", "quantity": "1 kg", "base_price": 52, "mrp": 60},
    {"name": "Poha (Flattened Rice)", "brand": None, "category": "staples", "quantity": "500 g", "base_price": 42, "mrp": 48},
    
    # === PERSONAL CARE ===
    {"name": "Colgate MaxFresh Toothpaste", "brand": "Colgate", "category": "personal_care", "quantity": "300 g", "base_price": 189, "mrp": 220},
    {"name": "Pepsodent Toothpaste", "brand": "Pepsodent", "category": "personal_care", "quantity": "200 g", "base_price": 95, "mrp": 110},
    {"name": "Dettol Antiseptic Liquid", "brand": "Dettol", "category": "personal_care", "quantity": "550 ml", "base_price": 175, "mrp": 199},
    {"name": "Dettol Soap", "brand": "Dettol", "category": "personal_care", "quantity": "125 g (Pack of 4)", "base_price": 145, "mrp": 165},
    {"name": "Dove Soap", "brand": "Dove", "category": "personal_care", "quantity": "100 g (Pack of 3)", "base_price": 185, "mrp": 210},
    {"name": "Lux Soap", "brand": "Lux", "category": "personal_care", "quantity": "150 g (Pack of 4)", "base_price": 185, "mrp": 200},
    {"name": "Head & Shoulders Shampoo", "brand": "Head & Shoulders", "category": "personal_care", "quantity": "340 ml", "base_price": 340, "mrp": 380},
    {"name": "Clinic Plus Shampoo", "brand": "Clinic Plus", "category": "personal_care", "quantity": "340 ml", "base_price": 240, "mrp": 270},
    {"name": "Dove Shampoo", "brand": "Dove", "category": "personal_care", "quantity": "340 ml", "base_price": 295, "mrp": 330},
    {"name": "Pantene Shampoo", "brand": "Pantene", "category": "personal_care", "quantity": "340 ml", "base_price": 285, "mrp": 320},
    {"name": "Nivea Body Lotion", "brand": "Nivea", "category": "personal_care", "quantity": "400 ml", "base_price": 320, "mrp": 360},
    {"name": "Vaseline Body Lotion", "brand": "Vaseline", "category": "personal_care", "quantity": "400 ml", "base_price": 295, "mrp": 330},
    {"name": "Himalaya Face Wash", "brand": "Himalaya", "category": "personal_care", "quantity": "150 ml", "base_price": 155, "mrp": 175},
    {"name": "Pond's Face Wash", "brand": "Pond's", "category": "personal_care", "quantity": "150 ml", "base_price": 170, "mrp": 195},
    {"name": "Fair & Lovely Cream", "brand": "Fair & Lovely", "category": "personal_care", "quantity": "80 g", "base_price": 155, "mrp": 180},
    {"name": "Gillette Mach3 Razor", "brand": "Gillette", "category": "personal_care", "quantity": "1 pc", "base_price": 350, "mrp": 399},
    {"name": "Whisper Sanitary Pads", "brand": "Whisper", "category": "personal_care", "quantity": "20 pads", "base_price": 165, "mrp": 185},
    {"name": "Stayfree Sanitary Pads", "brand": "Stayfree", "category": "personal_care", "quantity": "20 pads", "base_price": 155, "mrp": 175},
    
    # === HOUSEHOLD ===
    {"name": "Surf Excel Easy Wash", "brand": "Surf Excel", "category": "household", "quantity": "1.5 kg", "base_price": 225, "mrp": 260},
    {"name": "Surf Excel Matic", "brand": "Surf Excel", "category": "household", "quantity": "2 kg", "base_price": 450, "mrp": 495},
    {"name": "Ariel Matic", "brand": "Ariel", "category": "household", "quantity": "2 kg", "base_price": 475, "mrp": 520},
    {"name": "Tide Plus", "brand": "Tide", "category": "household", "quantity": "2 kg", "base_price": 240, "mrp": 270},
    {"name": "Vim Dishwash Liquid", "brand": "Vim", "category": "household", "quantity": "750 ml", "base_price": 125, "mrp": 140},
    {"name": "Pril Dishwash Liquid", "brand": "Pril", "category": "household", "quantity": "750 ml", "base_price": 165, "mrp": 185},
    {"name": "Harpic Toilet Cleaner", "brand": "Harpic", "category": "household", "quantity": "1 L", "base_price": 165, "mrp": 185},
    {"name": "Lizol Floor Cleaner", "brand": "Lizol", "category": "household", "quantity": "975 ml", "base_price": 195, "mrp": 220},
    {"name": "Colin Glass Cleaner", "brand": "Colin", "category": "household", "quantity": "500 ml", "base_price": 135, "mrp": 155},
    {"name": "Odonil Room Freshener", "brand": "Odonil", "category": "household", "quantity": "300 ml", "base_price": 175, "mrp": 199},
    {"name": "Good Knight Liquid Refill", "brand": "Good Knight", "category": "household", "quantity": "45 ml (Pack of 2)", "base_price": 145, "mrp": 165},
    {"name": "All Out Refill", "brand": "All Out", "category": "household", "quantity": "45 ml (Pack of 2)", "base_price": 125, "mrp": 145},
    {"name": "Scotch Brite Scrub Pad", "brand": "Scotch Brite", "category": "household", "quantity": "3 pcs", "base_price": 65, "mrp": 75},
    {"name": "Garbage Bags", "brand": None, "category": "household", "quantity": "30 bags", "base_price": 85, "mrp": 99},
    {"name": "Tissue Paper Roll", "brand": None, "category": "household", "quantity": "4 rolls", "base_price": 145, "mrp": 165},
    {"name": "Kitchen Towel", "brand": None, "category": "household", "quantity": "2 rolls", "base_price": 115, "mrp": 130},
    
    # === BABY CARE ===
    {"name": "Pampers Diapers", "brand": "Pampers", "category": "baby_care", "quantity": "66 pcs (L)", "base_price": 1050, "mrp": 1199},
    {"name": "Huggies Diapers", "brand": "Huggies", "category": "baby_care", "quantity": "72 pcs (L)", "base_price": 1150, "mrp": 1299},
    {"name": "Johnson's Baby Powder", "brand": "Johnson's", "category": "baby_care", "quantity": "400 g", "base_price": 295, "mrp": 335},
    {"name": "Johnson's Baby Soap", "brand": "Johnson's", "category": "baby_care", "quantity": "150 g (Pack of 3)", "base_price": 215, "mrp": 240},
    {"name": "Johnson's Baby Oil", "brand": "Johnson's", "category": "baby_care", "quantity": "500 ml", "base_price": 375, "mrp": 420},
    {"name": "Cerelac Baby Food", "brand": "Nestle", "category": "baby_care", "quantity": "300 g", "base_price": 285, "mrp": 320},
    {"name": "Himalaya Baby Lotion", "brand": "Himalaya", "category": "baby_care", "quantity": "400 ml", "base_price": 295, "mrp": 330},
    {"name": "MamyPoko Pants", "brand": "MamyPoko", "category": "baby_care", "quantity": "54 pcs (L)", "base_price": 1020, "mrp": 1149},
    
    # === PET CARE ===
    {"name": "Pedigree Dog Food Chicken", "brand": "Pedigree", "category": "pet_care", "quantity": "3 kg", "base_price": 680, "mrp": 750},
    {"name": "Pedigree Puppy Food", "brand": "Pedigree", "category": "pet_care", "quantity": "3 kg", "base_price": 720, "mrp": 799},
    {"name": "Royal Canin Dog Food", "brand": "Royal Canin", "category": "pet_care", "quantity": "3 kg", "base_price": 1650, "mrp": 1850},
    {"name": "Whiskas Cat Food", "brand": "Whiskas", "category": "pet_care", "quantity": "1.2 kg", "base_price": 520, "mrp": 580},
    {"name": "Drools Dog Food", "brand": "Drools", "category": "pet_care", "quantity": "3 kg", "base_price": 580, "mrp": 650},
    
    # === FROZEN ===
    {"name": "Amul Ice Cream Vanilla", "brand": "Amul", "category": "frozen", "quantity": "750 ml", "base_price": 210, "mrp": 240},
    {"name": "Kwality Walls Ice Cream", "brand": "Kwality Walls", "category": "frozen", "quantity": "700 ml", "base_price": 225, "mrp": 260},
    {"name": "McCain French Fries", "brand": "McCain", "category": "frozen", "quantity": "450 g", "base_price": 175, "mrp": 199},
    {"name": "ITC Master Chef Frozen Parathas", "brand": "ITC", "category": "frozen", "quantity": "400 g", "base_price": 110, "mrp": 125},
    {"name": "Haldiram's Frozen Samosa", "brand": "Haldiram's", "category": "frozen", "quantity": "300 g", "base_price": 145, "mrp": 165},
    
    # === MEAT & SEAFOOD ===
    {"name": "Fresh Chicken Breast", "brand": None, "category": "meat_seafood", "quantity": "500 g", "base_price": 240, "mrp": 275},
    {"name": "Fresh Chicken Curry Cut", "brand": None, "category": "meat_seafood", "quantity": "500 g", "base_price": 180, "mrp": 210},
    {"name": "Fresh Mutton Curry Cut", "brand": None, "category": "meat_seafood", "quantity": "500 g", "base_price": 580, "mrp": 650},
    {"name": "Fresh Fish Rohu", "brand": None, "category": "meat_seafood", "quantity": "500 g", "base_price": 220, "mrp": 260},
    {"name": "Fresh Prawns", "brand": None, "category": "meat_seafood", "quantity": "500 g", "base_price": 450, "mrp": 520},
    {"name": "Fresh Eggs", "brand": None, "category": "meat_seafood", "quantity": "12 pcs", "base_price": 85, "mrp": 96},
    {"name": "Licious Chicken Sausages", "brand": "Licious", "category": "meat_seafood", "quantity": "250 g", "base_price": 185, "mrp": 210},
]

def get_products_by_query(query: str, limit: int = 50) -> list:
    """
    Search products by query.
    Returns products matching the search query.
    """
    query_lower = query.lower().strip()
    results = []
    
    for product in PRODUCT_DATABASE:
        name = product["name"].lower()
        brand = (product.get("brand") or "").lower()
        category = product.get("category", "").lower()
        
        # Match by name, brand, or category
        if (query_lower in name or 
            query_lower in brand or 
            query_lower in category or
            any(word in name for word in query_lower.split())):
            results.append(product)
            
            if len(results) >= limit:
                break
    
    return results

def get_all_products() -> list:
    """Return all products."""
    return PRODUCT_DATABASE

