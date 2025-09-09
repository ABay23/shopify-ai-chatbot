from fastapi import FastAPI, HTTPException
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

STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

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
