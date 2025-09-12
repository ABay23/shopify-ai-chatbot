from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from collections import Counter
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo  # pip install tzdata if needed
from dotenv import load_dotenv
from pathlib import Path
import os, requests, json

# ---------- ENV ----------
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

app = FastAPI(title="Shopify AI Chatbot Backend")

# Allow your Next dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shopify ENV
STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")                 # e.g. "your-store.myshopify.com"
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-07")        # configurable, sensible default

# OpenAI ENV
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
oai = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# ---------- Shopify helper ----------
def shopify_get(path: str, params: dict | None = None):
    if not STORE_DOMAIN or not ACCESS_TOKEN:
        raise RuntimeError("Missing SHOPIFY_STORE_DOMAIN or SHOPIFY_ACCESS_TOKEN in .env")
    url = f"https://{STORE_DOMAIN}/admin/api/{API_VERSION}/{path}"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    r = requests.get(url, headers=headers, params=params, timeout=20)
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()


# ---------- Time & ranges ----------
def get_shop_timezone() -> str:
    data = shopify_get("shop.json", params={"fields": "iana_timezone"})
    tz = (data.get("shop") or {}).get("iana_timezone")
    if not tz:
        raise HTTPException(status_code=500, detail="Cannot read shop timezone")
    return tz

def start_of_today_utc_from_shop_tz() -> str:
    tzname = get_shop_timezone()
    tz = ZoneInfo(tzname)
    now_local = datetime.now(tz)
    start_local = datetime(now_local.year, now_local.month, now_local.day, tzinfo=tz)
    return start_local.astimezone(timezone.utc).isoformat()

def range_to_utc(range_days: int) -> tuple[str, str]:
    tz = ZoneInfo(get_shop_timezone())
    now_local = datetime.now(tz)
    end_local = now_local
    start_local = now_local - timedelta(days=range_days)
    return (
        start_local.astimezone(timezone.utc).isoformat(),
        end_local.astimezone(timezone.utc).isoformat(),
    )


# ---------- Analytics helpers ----------
def fetch_orders_between(start_iso: str, end_iso: str) -> list[dict]:
    data = shopify_get(
        "orders.json",
        params={
            "status": "any",
            "created_at_min": start_iso,
            "created_at_max": end_iso,
            "fields": "id,created_at,total_price,line_items",
            "limit": 250,
        },
    )
    return data.get("orders", [])

def summarize_orders(orders: list[dict], top_n: int = 3) -> dict:
    revenue = sum(float(o.get("total_price") or 0) for o in orders)
    count = len(orders)
    aov = (revenue / count) if count else 0.0

    units = Counter()
    rev_by_title = Counter()
    for o in orders:
        for li in (o.get("line_items") or []):
            title = li.get("title", "Unknown")
            q = int(li.get("quantity") or 0)
            price_each = float(li.get("price") or 0)
            units[title] += q
            rev_by_title[title] += q * price_each

    top = []
    for title, qty in units.most_common(top_n):
        top.append({"title": title, "units": qty, "revenue": round(rev_by_title[title], 2)})

    return {
        "orders_count": count,
        "revenue": round(revenue, 2),
        "aov": round(aov, 2),
        "top_products": top,
    }

def sales_overview(range_days: int = 7) -> dict:
    # current
    cur_start, cur_end = range_to_utc(range_days)
    cur = summarize_orders(fetch_orders_between(cur_start, cur_end))

    # previous: same-length window immediately before
    prev_start_dt = datetime.fromisoformat(cur_start.replace("Z", "+00:00")) - timedelta(days=range_days)
    prev_end_dt = datetime.fromisoformat(cur_start.replace("Z", "+00:00"))
    prev = summarize_orders(fetch_orders_between(prev_start_dt.isoformat(), prev_end_dt.isoformat()))

    def pct_change(cur_val: float, prev_val: float) -> float | None:
        if prev_val == 0:
            return None
        return round(((cur_val - prev_val) / prev_val) * 100.0, 1)

    return {
        "range_days": range_days,
        "current": cur,
        "previous": prev,
        "wow_orders_pct": pct_change(cur["orders_count"], prev["orders_count"]),
        "wow_revenue_pct": pct_change(cur["revenue"], prev["revenue"]),
    }


# ---------- Models ----------
class ChatIn(BaseModel):
    question: str


# ---------- Endpoints ----------
@app.get("/ping")
def ping():
    return {"message": "Backend is running!!!"}

@app.get("/products")
def products(limit: int = 5):
    return shopify_get("products.json", params={"limit": limit})

@app.get("/products_simple")
def products_simple(limit: int = 10):
    data = shopify_get(
        "products.json",
        params={
            "limit": limit,
            # include BOTH so we always have a URL
            "fields": "id,title,image,images,variants",
        },
    )
    products = []
    for p in data.get("products", []):
        price = (p.get("variants") or [{}])[0].get("price")
        img = None
        if p.get("image") and p["image"].get("src"):
            img = p["image"]["src"]
        elif (p.get("images") or [{}])[0].get("src"):
            img = p["images"][0]["src"]
        products.append({
            "id": p["id"],
            "title": p["title"],
            "price": price,
            "image": img,            # <- singular key (matches frontend)
        })
    return {"products": products}

@app.get("/orders_today")
def orders_today():
    params = {
        "status": "any",
        "created_at_min": start_of_today_utc_from_shop_tz(),
        "fields": "id,total_price,created_at",
        "limit": 250,
    }
    data = shopify_get("orders.json", params=params)
    orders = data.get("orders", [])
    return {
        "count": len(orders),
        "revenue": sum(float(o.get("total_price") or 0) for o in orders),
    }

@app.get("/orders_last_7d")
def orders_last_7d():
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    data = shopify_get("orders.json", params={
        "status": "any",
        "created_at_min": since,
        "fields": "id,total_price,created_at",
        "limit": 250,
    })
    orders = data.get("orders", [])
    return {
        "count": len(orders),
        "revenue": sum(float(o.get("total_price") or 0) for o in orders),
    }

@app.get("/top_selling_30d")
def top_selling_30d(n: int = 1):
    params = {
        "status": "any",
        "created_at_min": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
        "fields": "id,created_at,line_items",
        "limit": 250,
    }
    data = shopify_get("orders.json", params=params)
    counts = Counter()
    for o in data.get("orders", []):
        for li in (o.get("line_items") or []):
            counts[li.get("title", "Unknown")] += int(li.get("quantity") or 0)
    top = [{"title": t, "units": u} for t, u in counts.most_common(n)]
    return {"top": top}

@app.get("/orders_recent")
def orders_recent():
    return shopify_get("orders.json", params={
        "limit": 5, "order": "created_at desc",
        "fields": "id,created_at,total_price"
    })

@app.get("/orders_count")
def order_count():
    return shopify_get("orders/count.json")

@app.get("/debug")
def debug():
    return {
        "SHOPIFY_STORE_DOMAIN": os.getenv("SHOPIFY_STORE_DOMAIN"),
        "SHOPIFY_ACCESS_TOKEN_set": bool(os.getenv("SHOPIFY_ACCESS_TOKEN")),
        "OPENAI_API_KEY_set": bool(os.getenv("OPENAI_API_KEY")),
        "ENV_PATH": str(ENV_PATH),
        "API_VERSION": API_VERSION,
    }


# ---------- Chat ----------
def classify_intent_llm(q: str) -> dict:
    """
    Use the model to choose an intent and range_days.
    Falls back to heuristics if OpenAI isn't configured.
    """
    if not oai:
        ql = q.lower()
        if "today" in ql:
            return {"intent": "orders_today", "range_days": 1}
        if "top" in ql and "sell" in ql:
            return {"intent": "top_selling", "range_days": 30}
        if any(k in ql for k in ("sales", "revenue", "performance", "how are", "doing")):
            return {"intent": "sales_overview", "range_days": 7}
        return {"intent": "sales_overview", "range_days": 7}

    resp = oai.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        temperature=0,
        messages=[
            {"role": "system", "content":
            "Return JSON with fields: intent ('sales_overview'|'orders_today'|'top_selling'), "
            "range_days (one of 1,7,30). Choose 'sales_overview' for broad questions like 'how are sales doing'."},
            {"role": "user", "content": q},
        ],
    )
    try:
        data = json.loads(resp.choices[0].message.content or "{}")
    except Exception:
        data = {}
    intent = data.get("intent") or "sales_overview"
    try:
        range_days = int(data.get("range_days") or 7)
    except Exception:
        range_days = 7
    if range_days not in (1, 7, 30):
        range_days = 7
    return {"intent": intent, "range_days": range_days}

def phrase_answer(question: str, facts: dict) -> str:
    if not oai:
        # Fallback phrasing without OpenAI
        ov = facts.get("overview")
        if ov:
            cur = ov["current"]; prev = ov["previous"]
            return (
                f"Sales in last {ov['range_days']}d: {cur['orders_count']} orders, ${cur['revenue']:.2f} revenue "
                f"(prev: {prev['orders_count']} / ${prev['revenue']:.2f}). "
                f"Top items: " + ", ".join(f"{t['title']} ({t['units']}u, ${t['revenue']:.2f})" for t in cur["top_products"][:3])
            )
        return f"Facts: {facts}"
    resp = oai.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content":
            "You are a concise Shopify assistant. Use ONLY the provided facts. "
            "Return 2–4 bullet points: totals, week-over-week change, and top items with units & revenue. "
            "If data is empty, say that and suggest placing a test order."},
            {"role": "user", "content": f"Q: {question}\nFacts:\n{json.dumps(facts)}"},
        ],
    )
    return (resp.choices[0].message.content or "").strip()

@app.post("/chat")
def chat(body: ChatIn):
    q = body.question.strip()
    if not q:
        return {"answer": "Ask me something like: 'How are my sales doing?', 'Orders today?', or 'Top sellers?'"}

    choice = classify_intent_llm(q)
    try:
        if choice["intent"] == "orders_today":
            # use overview(1d) for richer details than count alone
            overview = sales_overview(range_days=1)
            return {"answer": phrase_answer(q, {"overview": overview})}

        if choice["intent"] == "top_selling":
            overview = sales_overview(range_days=30)  # includes top_products
            return {"answer": phrase_answer(q, {"overview": overview})}

        # default: sales_overview with selected range (1/7/30)
        overview = sales_overview(range_days=choice["range_days"])
        return {"answer": phrase_answer(q, {"overview": overview})}

    except Exception as e:
        return {"answer": f"Sorry, I hit an error while checking Shopify: {e!s}"}  # friendly error
