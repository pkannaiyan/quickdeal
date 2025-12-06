# ⚡ QuickDeal - System Workflows

Complete workflow documentation for the QuickDeal price comparison and negotiation platform.

---

## 📋 Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [User Journey Flow](#user-journey-flow)
3. [Search & Compare Workflow](#search--compare-workflow)
4. [Negotiation Workflow](#negotiation-workflow)
5. [Order & Checkout Workflow](#order--checkout-workflow)
6. [Analytics Workflow](#analytics-workflow)
7. [Chatbot Workflow](#chatbot-workflow)
8. [Data Flow Diagram](#data-flow-diagram)

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              QUICKDEAL PLATFORM                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         FRONTEND (Next.js)                           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │   Home   │ │  Buyer   │ │  Seller  │ │  Admin   │ │Analytics │  │   │
│  │  │  Search  │ │Dashboard │ │Dashboard │ │Dashboard │ │Dashboard │  │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │   │
│  └───────┼────────────┼────────────┼────────────┼────────────┼────────┘   │
│          │            │            │            │            │             │
│          └────────────┴────────────┴────────────┴────────────┘             │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         BACKEND (FastAPI)                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │  Search  │ │Negotiate │ │   Auth   │ │ Analytics│ │  Chat    │  │   │
│  │  │   API    │ │   API    │ │   API    │ │   API    │ │   API    │  │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │   │
│  └───────┼────────────┼────────────┼────────────┼────────────┼────────┘   │
│          │            │            │            │            │             │
│          ▼            ▼            ▼            ▼            ▼             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           SERVICES                                   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ Scraper  │ │Negotia-  │ │   Auth   │ │ Analytics│ │ Chatbot  │  │   │
│  │  │  Agent   │ │  tion    │ │ Service  │ │ Service  │ │ Service  │  │   │
│  │  └────┬─────┘ └────┬─────┘ └──────────┘ └────┬─────┘ └──────────┘  │   │
│  └───────┼────────────┼─────────────────────────┼─────────────────────┘   │
│          │            │                         │                          │
│          ▼            ▼                         ▼                          │
│  ┌──────────────┐ ┌──────────────┐      ┌──────────────┐                  │
│  │   Platform   │ │    JSONL     │      │    JSONL     │                  │
│  │   Scrapers   │ │   Storage    │      │   Storage    │                  │
│  │  (5 sites)   │ │(offers/deals)│      │ (analytics)  │                  │
│  └──────────────┘ └──────────────┘      └──────────────┘                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 👤 User Journey Flow

```
                                    ┌─────────────┐
                                    │    USER     │
                                    └──────┬──────┘
                                           │
                         ┌─────────────────┼─────────────────┐
                         ▼                 ▼                 ▼
                   ┌───────────┐    ┌───────────┐    ┌───────────┐
                   │   BUYER   │    │  SELLER   │    │   ADMIN   │
                   └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
                         │                │                │
         ┌───────────────┼───────────┐    │                │
         ▼               ▼           ▼    ▼                ▼
    ┌─────────┐    ┌─────────┐  ┌─────────┐          ┌─────────┐
    │ Search  │    │Negotiate│  │ Accept/ │          │ Monitor │
    │Products │    │  Price  │  │ Reject  │          │   All   │
    └────┬────┘    └────┬────┘  └────┬────┘          └────┬────┘
         │              │            │                    │
         ▼              ▼            ▼                    ▼
    ┌─────────┐    ┌─────────┐  ┌─────────┐          ┌─────────┐
    │ Compare │    │  Deal   │  │ Counter │          │Override │
    │ Prices  │    │ Created │  │  Offer  │          │ Offers  │
    └────┬────┘    └────┬────┘  └─────────┘          └─────────┘
         │              │
         ▼              ▼
    ┌─────────┐    ┌─────────┐
    │  Buy @  │    │  Buy @  │
    │Best Deal│    │Deal Rate│
    └─────────┘    └─────────┘
```

---

## 🔍 Search & Compare Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SEARCH & COMPARE WORKFLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐                                                           │
│  │ User enters  │  "milk" / 🎤 "दूध" (voice)                                │
│  │ search query │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         ▼                                                                    │
│  ┌──────────────┐                                                           │
│  │  Frontend    │  POST /api/search?q=milk                                  │
│  │  SearchBar   │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         SCRAPER AGENT                                 │  │
│  │                                                                       │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │  │
│  │  │ Blinkit │ │  Zepto  │ │Instamart│ │BigBasket│ │ JioMart │        │  │
│  │  │ Scraper │ │ Scraper │ │ Scraper │ │ Scraper │ │ Scraper │        │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘        │  │
│  │       │           │           │           │           │              │  │
│  │       └───────────┴───────────┴───────────┴───────────┘              │  │
│  │                               │                                       │  │
│  │                               ▼                                       │  │
│  │                    ┌──────────────────┐                              │  │
│  │                    │  Product Matcher │  AI-powered matching         │  │
│  │                    │  (FuzzyWuzzy +   │  across platforms            │  │
│  │                    │   LLM fallback)  │                              │  │
│  │                    └────────┬─────────┘                              │  │
│  └─────────────────────────────┼────────────────────────────────────────┘  │
│                                │                                            │
│                                ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      PRICE COMPARISON                                 │  │
│  │                                                                       │  │
│  │   Product: Amul Taaza Milk 1L                                        │  │
│  │   ┌─────────────────────────────────────────────────────────────┐   │  │
│  │   │ Platform    │ Price │ Delivery │ Available │ Image         │   │  │
│  │   ├─────────────┼───────┼──────────┼───────────┼───────────────┤   │  │
│  │   │ 🔵 JioMart  │ ₹58   │ 2 hrs    │ ✅        │ [img_url]     │   │  │
│  │   │ 🟣 Zepto    │ ₹60   │ 10 min   │ ✅        │ [img_url]     │   │  │
│  │   │ 🟢 BigBasket│ ₹62   │ Same day │ ✅        │ [img_url]     │   │  │
│  │   │ 🟠 Instamart│ ₹65   │ 15 min   │ ✅        │ [img_url]     │   │  │
│  │   │ 🟡 Blinkit  │ ₹68   │ 10 min   │ ✅        │ [img_url]     │   │  │
│  │   └─────────────────────────────────────────────────────────────┘   │  │
│  │                                                                       │  │
│  │   Best Deal: JioMart @ ₹58 (Save 15%)                                │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                │                                            │
│                                ▼                                            │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                   │
│  │  Quick Order │   │  Negotiate   │   │   Compare    │                   │
│  │   @ ₹58      │   │    Price     │   │   Details    │                   │
│  └──────────────┘   └──────────────┘   └──────────────┘                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤝 Negotiation Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          NEGOTIATION WORKFLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  BUYER SIDE                           SELLER SIDE                           │
│  ══════════                           ═══════════                           │
│                                                                              │
│  ┌──────────────┐                                                           │
│  │ Click        │                                                           │
│  │ "Negotiate"  │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         ▼                                                                    │
│  ┌──────────────────────────┐                                               │
│  │   NEGOTIATE MODAL        │                                               │
│  │   ┌────────────────────┐ │                                               │
│  │   │ Product: Milk      │ │                                               │
│  │   │ Platform: JioMart  │ │                                               │
│  │   │ Current: ₹58       │ │                                               │
│  │   │ Your Offer: ₹50    │ │                                               │
│  │   │ Quantity: 2        │ │                                               │
│  │   │ [10%] [15%] [20%]  │ │  Quick discount buttons                      │
│  │   │ [Submit Offer]     │ │                                               │
│  │   └────────────────────┘ │                                               │
│  └──────────┬───────────────┘                                               │
│             │                                                                │
│             │  POST /api/negotiate/offers                                   │
│             │  {product, platform, offer_price, quantity}                   │
│             │                                                                │
│             ▼                                                                │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        NEGOTIATION SERVICE                            │  │
│  │                                                                       │  │
│  │  1. Create Offer (status: pending)                                   │  │
│  │  2. Set manual_review_deadline = now + 5 minutes                     │  │
│  │  3. Save to offers.jsonl                                             │  │
│  │  4. Notify seller (if webhook configured)                            │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│                                       │                                      │
│                                       ▼                                      │
│                           ┌──────────────────────┐                          │
│                           │   SELLER DASHBOARD   │                          │
│                           │                      │                          │
│                           │  Pending Offers: 1   │                          │
│                           │  ┌────────────────┐  │                          │
│                           │  │ Milk - ₹50     │  │                          │
│                           │  │ Original: ₹58  │  │                          │
│                           │  │ Discount: 14%  │  │                          │
│                           │  │ ⏱️ 4:32 left   │  │                          │
│                           │  │               │  │                          │
│                           │  │ [✅] [❌] [🔄]│  │                          │
│                           │  └────────────────┘  │                          │
│                           └──────────┬───────────┘                          │
│                                      │                                       │
│              ┌───────────────────────┼───────────────────────┐              │
│              ▼                       ▼                       ▼              │
│       ┌────────────┐          ┌────────────┐          ┌────────────┐       │
│       │   ACCEPT   │          │   REJECT   │          │  COUNTER   │       │
│       └─────┬──────┘          └─────┬──────┘          └─────┬──────┘       │
│             │                       │                       │               │
│             ▼                       ▼                       ▼               │
│       ┌────────────┐          ┌────────────┐          ┌────────────┐       │
│       │Create Deal │          │ Offer      │          │ New offer  │       │
│       │@ ₹50       │          │ Rejected   │          │ @ ₹54      │       │
│       └─────┬──────┘          └────────────┘          └─────┬──────┘       │
│             │                                               │               │
│             ▼                                               ▼               │
│  ┌──────────────────┐                            ┌──────────────────┐      │
│  │  BUYER DASHBOARD │                            │  Buyer reviews   │      │
│  │  ┌──────────────┐│                            │  counter offer   │      │
│  │  │ Deal Ready!  ││                            │  [Accept] [Reject│      │
│  │  │ Milk @ ₹50   ││                            └──────────────────┘      │
│  │  │ [Buy Now]    ││                                                       │
│  │  │ [One-Click]  ││                                                       │
│  │  └──────────────┘│                                                       │
│  └──────────────────┘                                                       │
│                                                                              │
│  ════════════════════════════════════════════════════════════════════════  │
│                         AUTO-PROCESSING (after 5 min)                       │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                                              │
│  If seller doesn't respond within 5 minutes:                                │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  SELLER SETTINGS                                                      │  │
│  │  ├── auto_accept_discount: 15%   → Discount ≤ 15%? AUTO ACCEPT       │  │
│  │  ├── auto_reject_discount: 30%   → Discount > 30%? AUTO REJECT       │  │
│  │  └── auto_counter_offer: true    → Else? COUNTER at avg price        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛒 Order & Checkout Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ORDER & CHECKOUT WORKFLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                    ┌─────────────────────────────────┐                      │
│                    │      THREE CHECKOUT OPTIONS      │                      │
│                    └─────────────────────────────────┘                      │
│                                    │                                         │
│         ┌──────────────────────────┼──────────────────────────┐             │
│         ▼                          ▼                          ▼             │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐     │
│  │   QUICK ORDER   │      │  ONE-CLICK BUY  │      │  SMART CHECKOUT │     │
│  │                 │      │                 │      │                 │     │
│  │  Select from    │      │  Fastest path   │      │  Guided flow    │     │
│  │  all platforms  │      │  to checkout    │      │  with steps     │     │
│  └────────┬────────┘      └────────┬────────┘      └────────┬────────┘     │
│           │                        │                        │               │
│           ▼                        ▼                        ▼               │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐     │
│  │  QUICK ORDER    │      │  ONE-CLICK      │      │  SMART CHECKOUT │     │
│  │    MODAL        │      │    MODAL        │      │    MODAL        │     │
│  │                 │      │                 │      │                 │     │
│  │  Platform List: │      │  ┌───────────┐  │      │  Step 1: Copy   │     │
│  │  🔵 JioMart ₹58 │      │  │Product    │  │      │  product name   │     │
│  │  🟣 Zepto  ₹60 │      │  │Milk @ ₹50 │  │      │                 │     │
│  │  🟢 BBask  ₹62 │      │  │(Deal Price)│  │      │  Step 2: Open   │     │
│  │                 │      │  └───────────┘  │      │  platform app   │     │
│  │  Qty: [1] [+][-]│      │                 │      │                 │     │
│  │  Total: ₹58     │      │  [Copy & Open]  │      │  Step 3: Paste  │     │
│  │                 │      │  [Direct Link]  │      │  & checkout     │     │
│  │  [Proceed]      │      │                 │      │                 │     │
│  └────────┬────────┘      └────────┬────────┘      └────────┬────────┘     │
│           │                        │                        │               │
│           ▼                        ▼                        ▼               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PLATFORM REDIRECT                                 │   │
│  │                                                                      │   │
│  │  Opens platform with search:                                        │   │
│  │  • JioMart:  https://www.jiomart.com/search?q=amul+milk            │   │
│  │  • Blinkit:  blinkit://search?q=amul+milk (app deep link)          │   │
│  │  • Zepto:    https://www.zeptonow.com/search?q=amul+milk           │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                │                                            │
│                                ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    ANALYTICS TRACKING                                │   │
│  │                                                                      │   │
│  │  Track: product_id, product_name, selected_platform, price,         │   │
│  │         quantity, user_id, timestamp                                 │   │
│  │                                                                      │   │
│  │  POST /api/analytics/track/order                                    │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Analytics Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ANALYTICS WORKFLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                        DATA COLLECTION                                       │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Searches  │  │   Orders   │  │Negotiations│  │   Deals    │           │
│  │  Tracked   │  │  Tracked   │  │  Tracked   │  │  Tracked   │           │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘           │
│        │               │               │               │                    │
│        └───────────────┴───────────────┴───────────────┘                    │
│                               │                                              │
│                               ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      ANALYTICS SERVICE                                │  │
│  │                                                                       │  │
│  │  Stores in JSONL files:                                              │  │
│  │  • data/analytics.json     (searches, orders)                        │  │
│  │  • data/negotiations/      (offers, deals)                           │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                               │                                              │
│                               ▼                                              │
│                                                                              │
│                      DASHBOARD DISPLAY                                       │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  📊 OVERVIEW TAB                                                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐               │   │
│  │  │ Searches │ │ Orders   │ │ Savings  │ │ Success  │               │   │
│  │  │   156    │ │   42     │ │  ₹359    │ │  57.5%   │               │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘               │   │
│  │                                                                      │   │
│  │  Platform Wins          Top Searches                                │   │
│  │  ├── JioMart 45%        ├── milk (28)                               │   │
│  │  ├── Zepto 25%          ├── bread (21)                              │   │
│  │  └── BigBasket 15%      └── chips (15)                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  🤝 NEGOTIATIONS TAB                                                 │   │
│  │                                                                      │   │
│  │  Discount Distribution:        Platform Success:                     │   │
│  │  0-10%  ████████░░ 45%        Blinkit   66.7%                       │   │
│  │  10-20% ██████░░░░ 35%        BigBasket 66.7%                       │   │
│  │  20-30% ████░░░░░░ 15%        JioMart   50.0%                       │   │
│  │  30%+   ██░░░░░░░░  5%                                              │   │
│  │                                                                      │   │
│  │  Total Savings: ₹359         Avg per Deal: ₹27.62                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  📈 CONVERSIONS TAB                                                  │   │
│  │                                                                      │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │   │
│  │  │ Searches │ ─► │  Orders  │ ─► │ Negotiate│ ─► │  Deals   │      │   │
│  │  │   156    │    │    42    │    │    40    │    │    13    │      │   │
│  │  │  100%    │    │   27%    │    │   26%    │    │   33%    │      │   │
│  │  └──────────┘    └──────────┘    └──────────┘    └──────────┘      │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Chatbot Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CHATBOT WORKFLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         USER INPUT                                    │  │
│  │                                                                       │  │
│  │   💬 Text: "find cheapest milk"                                      │  │
│  │   🎤 Voice: [🔴 Recording in Hindi] → "सबसे सस्ता दूध दिखाओ"         │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      INTENT DETECTION                                 │  │
│  │                                                                       │  │
│  │  Keywords → Intent Mapping:                                          │  │
│  │  ├── "find", "search", "show" → SEARCH_PRODUCT                       │  │
│  │  ├── "cheapest", "lowest" → GET_CHEAPEST                             │  │
│  │  ├── "compare" → COMPARE_PRICES                                      │  │
│  │  ├── "deal", "offer" → FIND_DEALS                                    │  │
│  │  ├── "negotiate", "bargain" → NEGOTIATE_PRICE                        │  │
│  │  ├── "buy", "order", "quick order" → QUICK_ORDER / ONE_CLICK         │  │
│  │  ├── "my offers", "my deals" → MY_OFFERS / MY_DEALS                  │  │
│  │  └── "seller dashboard", "admin" → OPEN_DASHBOARD                    │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      QUERY EXTRACTION                                 │  │
│  │                                                                       │  │
│  │  Input: "find cheapest milk near me"                                 │  │
│  │  Extracted: "milk"                                                   │  │
│  │                                                                       │  │
│  │  Clean: Remove stop words, normalize                                 │  │
│  │  Result: { intent: "GET_CHEAPEST", query: "milk" }                   │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      RESPONSE GENERATION                              │  │
│  │                                                                       │  │
│  │  {                                                                   │  │
│  │    "response": "💰 Found Mother Dairy @ ₹57 on JioMart!",           │  │
│  │    "intent": "get_cheapest",                                         │  │
│  │    "action": "search",                                               │  │
│  │    "data": { "query": "milk", "sort": "price" },                    │  │
│  │    "suggestions": ["Buy Now", "Negotiate", "Compare All"]            │  │
│  │  }                                                                   │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      FRONTEND ACTION                                  │  │
│  │                                                                       │  │
│  │  Based on action type:                                               │  │
│  │  ├── "search" → Trigger search with query                           │  │
│  │  ├── "show_deals" → Open deals section                              │  │
│  │  ├── "negotiate_price" → Open NegotiateModal                        │  │
│  │  ├── "one_click_checkout" → Open OneClickCheckout                   │  │
│  │  ├── "quick_order" → Open QuickOrderModal                           │  │
│  │  ├── "open_buyer_dashboard" → Navigate to /buyer                    │  │
│  │  ├── "open_seller_dashboard" → Navigate to /seller                  │  │
│  │  └── "open_admin_dashboard" → Navigate to /admin                    │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW DIAGRAM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              EXTERNAL                                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│  │ Blinkit │ │  Zepto  │ │Instamart│ │BigBasket│ │ JioMart │              │
│  │   API   │ │   API   │ │   API   │ │   API   │ │   API   │              │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘              │
│       │           │           │           │           │                    │
│       └───────────┴───────────┴───────────┴───────────┘                    │
│                               │                                              │
│                               ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         SCRAPERS                                      │  │
│  │                    (Real + Demo Fallback)                             │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
│                               │                                              │
│                               ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      PRODUCT DATABASE                                 │  │
│  │                   data/product_database.py                            │  │
│  │                     (150+ products)                                   │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
│                               │                                              │
│          ┌────────────────────┼────────────────────┐                        │
│          ▼                    ▼                    ▼                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   SEARCH     │    │ NEGOTIATION  │    │  ANALYTICS   │                  │
│  │   SERVICE    │    │   SERVICE    │    │   SERVICE    │                  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                  │
│         │                   │                   │                           │
│         ▼                   ▼                   ▼                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   In-Memory  │    │ offers.jsonl │    │analytics.json│                  │
│  │    Cache     │    │ deals.jsonl  │    │              │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│                                                                              │
│                               │                                              │
│                               ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         FASTAPI BACKEND                               │  │
│  │                                                                       │  │
│  │  /api/search ─── /api/negotiate ─── /api/analytics ─── /api/chat    │  │
│  │                                                                       │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
│                               │                                              │
│                               ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                       NEXT.JS FRONTEND                                │  │
│  │                                                                       │  │
│  │  /         /buyer      /seller     /admin      /dashboard            │  │
│  │  Home      Dashboard   Dashboard   Dashboard   Analytics             │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 API Flow Summary

| Flow | Endpoint | Method | Description |
|------|----------|--------|-------------|
| Search | `/api/search?q=milk` | GET | Search products |
| Deals | `/api/search/deals` | GET | Get best deals |
| Compare | `/api/compare/{product}` | GET | Compare prices |
| Create Offer | `/api/negotiate/offers` | POST | Make negotiation offer |
| My Offers | `/api/negotiate/offers/my` | GET | Get buyer's offers |
| Seller Offers | `/api/negotiate/seller/pending` | GET | Get pending offers |
| Respond | `/api/negotiate/seller/offers/{id}/respond` | POST | Accept/Reject/Counter |
| Order at Deal | `/api/negotiate/deals/{id}/order` | POST | Order at deal price |
| Chat | `/api/chat` | POST | Chatbot interaction |
| Analytics | `/api/analytics/dashboard` | GET | Get all analytics |

---

## 🔐 Authentication Flow

```
Register → Login → Get Token → Use Token in Headers → Access Protected Routes
```

| Role | Access |
|------|--------|
| **Buyer** | Search, Compare, Negotiate, View own offers/deals |
| **Seller** | View offers for own platform, Accept/Reject/Counter |
| **Admin** | View all data, Override offers, System statistics |

---

*Built with ❤️ during AI Technology Workshop (Dec 4-6, 2025)*

