# ⚡ QuickDeal - Compare. Negotiate. Save.

An AI-powered marketplace that compares prices across Indian quick commerce platforms AND lets you negotiate for better deals directly with sellers.

> **Built during AI Technology Workshop (Dec 4-6, 2025) using Cursor AI**

## ✨ What Makes QuickDeal Special?

| Feature | Description |
|---------|-------------|
| 🔍 **Smart Search** | Compare 150+ products across 5 platforms with images |
| 🤝 **Price Negotiation** | Make offers to sellers and get accepted deals |
| 📊 **Analytics Dashboard** | Comprehensive insights on searches, negotiations & savings |
| 🎤 **Voice Search** | Speak in 10 Indian languages |
| 🤖 **AI Chatbot** | Conversational assistant for search, compare, negotiate & buy |
| ⚡ **One-Click Buy** | Purchase at negotiated prices instantly |
| 🔥 **Live Deals** | Auto-refreshing deals every 5 minutes |
| 👤 **Role-Based Access** | Separate dashboards for Buyers, Sellers & Admin |

## 🎯 Core Features

### 🤝 Price Negotiation System

The flagship feature that sets QuickDeal apart:

```
┌─────────────────────────────────────────────────────────────────┐
│  🤝 NEGOTIATION FLOW                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  BUYER                          SELLER                          │
│    │                              │                             │
│    │  1. Makes Offer (₹85)        │                             │
│    │  ────────────────────────►   │                             │
│    │                              │  2. Reviews (5 min window)  │
│    │                              │                             │
│    │  ◄────────────────────────   │  3. Accept/Reject/Counter   │
│    │                              │                             │
│    │  4. Order at Deal Price      │                             │
│    │  ════════════════════════►   │                             │
│    │                              │                             │
│    │  💰 Buyer saves ₹15!         │                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Seller Options:**
- ✅ **Accept** - Approve the offered price
- ❌ **Reject** - Decline the offer  
- 🔄 **Counter** - Propose a different price
- ⏱️ **Auto-Process** - Rules-based handling after 5 min

### 📊 Analytics Dashboard

Access at **http://localhost:3002/dashboard**

| Tab | Metrics |
|-----|---------|
| **Overview** | Total searches, negotiations, savings, platform wins, top searches |
| **Negotiations** | Offers made/accepted/rejected, discount distribution, success by platform |
| **Platforms** | Real-time status, latency, best price wins, savings by platform |
| **Conversions** | Full funnel: Search → Order → Negotiate → Deal with conversion rates |

### 🛒 Role-Based Dashboards

| Role | URL | Features |
|------|-----|----------|
| **Buyer** | `/buyer` | My offers, my deals, savings stats, one-click buy at deal price |
| **Seller** | `/seller` | Pending offers, accept/reject/counter, auto-accept settings |
| **Admin** | `/admin` | All offers, all deals, system stats, manage all platforms |

### 🤖 AI Chatbot (Voice + Text)

The chatbot handles EVERYTHING:

```
┌─────────────────────────────────────────────────────────────┐
│ ⚡ QuickDeal Assistant                              🎤 🔊   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ You: "Find cheapest milk"                                   │
│ Bot: 🔍 Found Mother Dairy @ ₹57 on JioMart                │
│      [Buy Now] [Negotiate] [Compare]                        │
│                                                             │
│ You: "Negotiate for ₹50"                                    │
│ Bot: 🤝 Opening negotiation modal...                        │
│                                                             │
│ You: "Show my deals"                                        │
│ Bot: 📋 You have 3 completed deals. Opening dashboard...    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ 💬 Type or speak...                                    ➤   │
└─────────────────────────────────────────────────────────────┘
```

**Chatbot Commands:**
| Intent | Examples |
|--------|----------|
| Search | `milk`, `find bread`, `show chips` |
| Compare | `compare rice prices`, `cheapest eggs` |
| Negotiate | `negotiate milk`, `bargain for bread`, `make offer on rice` |
| Buy | `buy now milk`, `one-click eggs`, `quick order bread` |
| Track | `my offers`, `my deals`, `show negotiations` |
| Dashboard | `seller dashboard`, `admin panel`, `analytics` |
| Deals | `show deals`, `today's best offers` |

## 🏪 Supported Platforms

| Platform | Logo | Delivery | Best For |
|----------|------|----------|----------|
| **Blinkit** | 🟡 | 10-20 min | Urban quick delivery |
| **Zepto** | 🟣 | 10 min | Fastest delivery |
| **Swiggy Instamart** | 🟠 | 15-30 min | Wide selection |
| **BigBasket** | 🟢 | Same day | Bulk purchases |
| **JioMart** | 🔵 | Same/Next day | Lowest prices |

## 🚀 Quick Start

### Docker (Recommended)

```bash
cd price-comparison-agent
docker-compose up --build
```

Then open:
- **App**: http://localhost:3002
- **Analytics**: http://localhost:3002/dashboard
- **Buyer Dashboard**: http://localhost:3002/buyer
- **Seller Dashboard**: http://localhost:3002/seller
- **Admin Dashboard**: http://localhost:3002/admin
- **API Docs**: http://localhost:8002/docs

### Demo Login

| Role | User ID | Password |
|------|---------|----------|
| Admin | `admin` | `admin` |
| Buyer | `test_buyer` | `password` |
| Seller (Blinkit) | `user_blinkit` | `password` |
| Seller (Zepto) | `user_zepto` | `password` |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ⚡ QuickDeal Platform                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────┐   ┌────────────────┐   ┌────────────────┐          │
│  │   COMPARISON   │   │  NEGOTIATION   │   │   ANALYTICS    │          │
│  │    ENGINE      │   │    ENGINE      │   │    ENGINE      │          │
│  └───────┬────────┘   └───────┬────────┘   └───────┬────────┘          │
│          │                    │                    │                    │
│  ┌───────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐          │
│  │   5 Platform   │   │  Buyer/Seller  │   │  Search, Order │          │
│  │   Scrapers     │   │  Matching      │   │  Conversion    │          │
│  │   + Matcher    │   │  + Auto-Rules  │   │  + Savings     │          │
│  └────────────────┘   └────────────────┘   └────────────────┘          │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                     FastAPI Backend (8002)                      │    │
│  │  /api/search  /api/negotiate  /api/analytics  /api/chat        │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                   Next.js Frontend (3002)                       │    │
│  │  Home | Buyer Dashboard | Seller Dashboard | Admin | Analytics  │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📊 API Endpoints

### Search & Compare
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search?q={query}` | Search products with images |
| GET | `/api/search/deals` | Get auto-refreshing deals |
| GET | `/api/compare/{product}` | Compare prices across platforms |

### Negotiation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/negotiate/offers` | Create new offer |
| GET | `/api/negotiate/offers/my` | Get buyer's offers |
| GET | `/api/negotiate/seller/pending` | Get seller's pending offers |
| POST | `/api/negotiate/seller/offers/{id}/respond` | Accept/Reject/Counter |
| POST | `/api/negotiate/deals/{id}/order` | Order at deal price |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | Complete dashboard data |
| GET | `/api/analytics/negotiations` | Negotiation analytics |
| GET | `/api/analytics/savings` | Savings by platform, daily trend |
| GET | `/api/analytics/conversions` | Conversion funnel |
| GET | `/api/analytics/realtime` | Live metrics |

### Chatbot
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message to chatbot |
| GET | `/api/chat/suggestions` | Get quick suggestions |

## 🎤 Voice Features

### Voice Search (10 Languages)
| Language | Code | Example |
|----------|------|---------|
| 🇮🇳 English | en-IN | "milk", "bread" |
| 🇮🇳 हिंदी | hi-IN | "दूध", "ब्रेड" |
| 🇮🇳 தமிழ் | ta-IN | "பால்" |
| 🇮🇳 తెలుగు | te-IN | "పాలు" |
| 🇮🇳 मराठी | mr-IN | "दूध" |
| 🇮🇳 বাংলা | bn-IN | "দুধ" |
| + 4 more... | | |

### Voice Chatbot
- 🎤 Click microphone in chat
- 🌐 Select language
- 🗣️ Speak your query
- ⚡ Auto-sends when done

## 📁 Project Structure

```
price-comparison-agent/
├── agents/                    # AI Agents
│   ├── scraper_agent.py      # Orchestrates scraping
│   ├── product_matcher.py    # AI-powered product matching
│   └── deal_finder.py        # Finds best deals
│
├── scrapers/                  # Platform scrapers (5 platforms)
│   ├── blinkit_scraper.py
│   ├── zepto_scraper.py
│   ├── instamart_scraper.py
│   ├── bigbasket_scraper.py
│   └── jiomart_scraper.py
│
├── services/                  # Business logic
│   ├── negotiation_service.py   # Offer management
│   ├── analytics_service.py     # Comprehensive analytics
│   ├── chatbot_service.py       # AI chatbot logic
│   └── auth_service.py          # Authentication
│
├── models/                    # Data models
│   ├── negotiation.py        # Offer, Deal, SellerProfile
│   └── product.py            # Product with images
│
├── api/                       # FastAPI backend
│   ├── main.py
│   └── routes/
│       ├── search.py         # Search & deals
│       ├── negotiation.py    # Buyer/Seller/Admin endpoints
│       ├── analytics.py      # Dashboard data
│       └── chat.py           # Chatbot API
│
├── data/
│   ├── product_database.py   # 150+ products with images
│   └── negotiations/         # Offers & deals storage
│
└── frontend/                  # Next.js frontend
    ├── app/
    │   ├── page.tsx          # Home with search
    │   ├── buyer/page.tsx    # Buyer dashboard
    │   ├── seller/page.tsx   # Seller dashboard
    │   ├── admin/page.tsx    # Admin dashboard
    │   ├── dashboard/page.tsx # Analytics
    │   └── components/
    │       ├── SearchBar.tsx        # Voice search
    │       ├── ComparisonCard.tsx   # Product with image
    │       ├── NegotiateModal.tsx   # Make offers
    │       ├── Chatbot.tsx          # AI assistant
    │       └── ...
    └── package.json
```

## 📈 Sample Analytics Data

```
📊 QuickDeal Analytics Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Searches (24h):        156
🤝 Negotiations:          40
✅ Success Rate:          57.5%
💰 Total Savings:         ₹359
📦 Completed Deals:       13

🏆 Platform Performance:
   Blinkit    ████████░░ 66.7% success
   BigBasket  ████████░░ 66.7% success
   JioMart    ████░░░░░░ 50.0% success

📊 Discount Distribution:
   0-10%      ██████████ 45%
   10-20%     ████████░░ 40%
   20-30%     ████░░░░░░ 15%
```

## 🛠️ Technologies Used

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, React, Tailwind CSS |
| **Backend** | FastAPI, Python 3.11 |
| **AI/ML** | Ollama (LLM), Custom product matching |
| **Database** | JSONL files (demo), PostgreSQL ready |
| **Voice** | Web Speech API |
| **Container** | Docker, Docker Compose |

## 🎓 Built With Cursor AI

This entire project was built during a 3-day workshop using **Cursor AI**:

- **Day 1**: Price comparison engine, platform scrapers
- **Day 2**: Negotiation system, buyer/seller dashboards
- **Day 3**: Analytics, chatbot, UI redesign, branding

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - For educational purposes.

---

<div align="center">

**⚡ QuickDeal - Compare. Negotiate. Save.**

Built with ❤️ during AI Technology Workshop (Dec 4-6, 2025)

[Demo](http://localhost:3002) • [API Docs](http://localhost:8002/docs) • [Analytics](http://localhost:3002/dashboard)

</div>
