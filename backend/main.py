from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/ping")
def ping():
    return {"message": "Backend is running!!!"}

@app.get('/products')
def products(limit: int = 5):
    return shopify_get('products.json', params={'limit': limit})

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
        img = (p.get('images') or [{}])[0].get('src')
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
