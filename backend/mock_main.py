from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os, requests

app = FastAPI()
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000"],
    allow_methods=["*"], allow_headers=["*"],
)

STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_V = os.getenv("SHOPIFY_API_VERSION", "2024-07")

def shopify_get(path, params=None):
    url = f"https://{STORE}/admin/api/{API_V}/{path}"
    h = {"X-Shopify-Access-Token": TOKEN}
    return requests.get(url, headers=h, params=params, timeout=20).json()

@app.get("/products_simple")
def products_simple(limit: int = 6):
    data = shopify_get("products.json", {"limit": limit, "fields": "id,title"})
    return {"products": data.get("products", [])[:limit]}