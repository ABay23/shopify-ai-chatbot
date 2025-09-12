from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from collections import Counter
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from pathlib import Path
import os, requests

# load_dotenv()
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)
app = FastAPI()

'''
We can allow requests from the Frontend dev server
'''
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'], #* Frontend url
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

#* Shopify ENVs
STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

#* OpenAI ENVs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
oai = OpenAI(api_key=OPENAI_API_KEY)


def shopify_get(path: str, params: dict | None = None):
    if not STORE_DOMAIN or not ACCESS_TOKEN:
        raise RuntimeError("Missing SHOPIFY_STORE_DOMAIN or ACCESS_TOKEN in .env")
    url = f'https://{STORE_DOMAIN}/admin/api/2025-07/{path}'
    headers = {
        'X-Shopify-Access-Token': ACCESS_TOKEN,
        'Content-Type': 'application/json',
    }
    
    r = requests.get(url, headers=headers, params=params, timeout=20)
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()

def iso_utc_start_of_today() -> str:
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    return start.isoformat()

def iso_utc_days_ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

'''
Chatbot methods 
'''

class ChatIn(BaseModel):
    question: str

def classify_intent(q: str) -> str:
    q = q.lower()
    if ("top" in q and "sell" in q) or ("best" in q and "product" in q):
        return "top_selling"
    if "orders" in q and ("today" in q or "todays" in q or "today's" in q):
        return "orders_today"
    if "revenue" in q and "today" in q:
        return "orders_today"  # same endpoint returns revenue
    return "unknown"

def phrase_answer(question: str, facts: dict) -> str:
    """
    Use OpenAI to turn raw facts into a concise, helpful answer.
    """
    #* Fast performance with lighweight model
    resp = oai.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a concise Shopify assistant. "
                    "Use ONLY the provided facts. Include numbers and time ranges. "
                    "If data is empty, be clear about that."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {question}\nFacts (JSON): {facts}",
            },
        ],
    )
    return (resp.choices[0].message.content or "").strip()


'''
Endpoints with KPIs
'''
@app.get("/ping")
def ping():
    return {"message": "Backend is running!!!"}

@app.get('/products')
def products(limit: int = 5):
    return shopify_get('products.json', params={'limit': limit})

@app.get("/top_selling_30d")
def top_selling_30d(n: int = 1):
    params = {
        "status": "any",
        "created_at_min": iso_utc_days_ago(30),
        "fields": "id,created_at,line_items",
        "limit": 250,  # fine for a dev store; paging optional
    }
    data = shopify_get("orders.json", params=params)
    orders = data.get("orders", [])
    counts = Counter()
    for o in orders:
        for li in (o.get("line_items") or []):
            counts[li.get("title", "Unknown")] += int(li.get("quantity") or 0)
    top = [{"title": t, "units": u} for t, u in counts.most_common(n)]
    return {"top": top}

@app.get("/orders_today")
def orders_today():
    params = {
        "status": "any",
        "created_at_min": iso_utc_start_of_today(),
        "fields": "id,total_price,created_at",
        "limit": 250,
    }
    data = shopify_get("orders.json", params=params)
    orders = data.get("orders", [])
    count = len(orders)
    revenue = sum(float(o.get("total_price") or 0) for o in orders)
    return {"count": count, "revenue": revenue}

@app.get('/products_simple')
def products_simple(limit: int = 10):
    data = shopify_get(
        'products.json',
        params={
            'limit': limit,
            #* Only fetch these fields from Shopify
            'fields': 'id, title, images, variants'
        },
    )
    
    #* Shhape for the UI
    products = []
    for p in data.get('products', []):
        price = p['variants'][0]['price'] if p.get('variants') else None
        # img = (p.get('images') or [{}])[0].get('src')
        img = None
        if p.get("image") and p["image"].get("src"):
            img = p["image"]["src"]
        elif (p.get("images") or [{}])[0].get("src"):
            img = p["images"][0]["src"]
            
        products.append({
            'id': p['id'],
            'title': p['title'],
            'price': price,
            'images': img,
        })
    return {"products": products}

@app.get('/orders_count')
def order_count():
    #* lighweight count demo
    return shopify_get('orders/count.json')

@app.get("/debug")
def debug():
    sd = os.getenv("SHOPIFY_STORE_DOMAIN")
    tok = os.getenv("SHOPIFY_ACCESS_TOKEN")
    return {
        "SHOPIFY_STORE_DOMAIN": sd,
        "SHOPIFY_ACCESS_TOKEN_set": bool(tok),
        "ENV_PATH": str(ENV_PATH)
    }
    
'''
THis is the chat concept
'''
@app.post("/chat")
def chat(body: ChatIn):
    q = body.question.strip()
    if not q:
        return {"answer": "Ask me something like: 'Orders today?' or 'Top-selling product'."}

    intent = classify_intent(q)

    try:
        if intent == "orders_today":
            data = orders_today()  # call the function directly (fast)
            facts = {"orders_today": data}
            return {"answer": phrase_answer(q, facts)}

        if intent == "top_selling":
            data = top_selling_30d(n=1)
            facts = {"top_selling_30d": data}
            return {"answer": phrase_answer(q, facts)}

        # fallback: help the user with examples
        facts = {"notice": "No matching intent", "examples": ["Orders today?", "Top-selling product?"]}
        return {"answer": phrase_answer(q, facts)}

    except Exception as e:
        # Surface errors cleanly
        return {"answer": f"Sorry, I hit an error while checking Shopify: {e!s}"}
