# Shopify AI Chatbot 🤖🛍️

A focused prototype that lets a merchant **ask natural-language questions** about their Shopify store and get instant answers (e.g., _“Top-selling product today?”_, _“Abandoned carts this week?”_).

**Why it matters:** Merchants lose time hopping across dashboards. This project shows a faster path from **question → decision** using Shopify data + AI.

---

## TL;DR (60s)

- **What I built:** A minimal Shopify-aware chatbot.
- **What it does:** Answers a few high-value ops questions using live store data.
- **How:** Next.js (App Router) UI → FastAPI backend → Shopify Admin API + OpenAI.
- **Why Shopify APM:** Demonstrates merchant empathy + bias for action + technical fluency.

🎥 **Demo (90 sec):** _link coming soon_  
📂 **Repo structure:** `frontend/` (Next.js) + `backend/` (FastAPI)

---

## Screenshots

_they will be
added soon_

---

## Architecture (at a glance)

Next.js (App Router, TS)
|
| fetch(question)
v
FastAPI (Python)
|-- calls Shopify Admin API (orders/products/carts)
|-- calls OpenAI (GPT model) with retrieved data
v
Natural-language answer → back to UI

---

## Key Use Cases

- **“Top-selling product today?”** → product title + units + revenue
- **“Orders today?”** → count + quick summary
- **“Abandoned carts this week?”** → count + trend hint

> Scope is intentionally small to highlight PM tradeoffs: pick a few valuable, auditable insights and make them fast to access.

---

## Tech Stack

- **Frontend:** Next.js 14 (TypeScript, App Router)
- **Backend:** FastAPI (Python)
- **APIs:** Shopify Admin API, OpenAI
- **Deploy (planned):** Vercel (frontend), Render/Railway (backend)

---

## Quickstart

### 1) Clone

```bash
git clone https://github.com/ABay23/shopify-ai-chatbot.git
cd shopify-ai-chatbot

2) Environment variables
Copy templates and fill in values (no secrets are committed):

bash

# Backend
cp backend/.env.example backend/.env
# Frontend
cp frontend/.env.local.example frontend/.env.local
backend/.env required


env
SHOPIFY_API_KEY=your_key
SHOPIFY_API_SECRET=your_secret
SHOPIFY_ACCESS_TOKEN=your_store_access_token
OPENAI_API_KEY=your_openai_key
frontend/.env.local required

env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

3) Run backend (FastAPI)

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt    # or: pip install fastapi uvicorn requests openai python-dotenv
uvicorn main:app --reload --port 8000
Test: http://localhost:8000/ping → { "message": "Backend is running!" }

4) Run frontend (Next.js)

cd ../frontend
npm install
npm run dev
Open: http://localhost:3000

Project Structure
lua
Copy code
shopify-ai-chatbot/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   ├── package.json
│   └── .env.local.example
└── README.md
```

---

## Roadmap (APM-friendly)

- [x] Scaffold FE/BE + CORS + repo hygiene
- [x] Shopify Admin API integration (products, orders)
- [ ] `/chat` endpoint: retrieve data → compose NL answer with OpenAI
- [ ] Chat UI polish (typing indicator, error states)
- [ ] Metrics: simple latency + success counter
- [ ] Deployment (Vercel + Render) + live demo link
- [ ] Short product write-up (Problem → Approach → Result → Next steps)

## Product Thinking Notes

- **Merchant empathy:** Focused on questions that reduce time-to-answer during daily operations (e.g., top-selling product, orders today, abandoned carts).
- **Tradeoffs:** Kept scope intentionally tight (3 queries) to ensure speed and reliability within one week.
- **Next steps:** Extend beyond Q&A to proactive insights, such as alerts for unusual changes (_“abandoned carts spiked 20% vs. last 7 days”_).

### Author

Alejandro Bay — Brooklyn, NY
🔗 LinkedIn: https://www.linkedin.com/in/alejandrobay/
💻 GitHub: https://github.com/ABay23

---
