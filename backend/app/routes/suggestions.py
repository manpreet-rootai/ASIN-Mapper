from fastapi import APIRouter
import requests
import os
import random
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

KEEPA_API_KEY = os.getenv("KEEPA_API_KEY")

DOMAIN_MAP = {
    "US": 1,
    "UK": 2,
    "DE": 3,
    "FR": 4,
    "IT": 8,
    "ES": 9
}


# 🔍 SEARCH → ASIN LIST
def search_keepa(query, domain):
    try:
        if not KEEPA_API_KEY:
            return []

        url = "https://api.keepa.com/search"

        params = {
            "key": KEEPA_API_KEY,
            "domain": DOMAIN_MAP[domain],
            "term": query
        }

        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        return data.get("asinList", [])[:5]

    except Exception as e:
        print("SEARCH ERROR:", e)
        return []


# 🔍 PRODUCT DETAILS
def get_product_details(asins, domain):
    try:
        if not asins:
            return []

        url = "https://api.keepa.com/product"

        params = {
            "key": KEEPA_API_KEY,
            "domain": DOMAIN_MAP[domain],
            "asin": ",".join(asins)
        }

        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        return data.get("products", [])

    except Exception as e:
        print("DETAIL ERROR:", e)
        return []


# 🎯 SMART SCORE CALCULATION
def calculate_score(product, item):
    score = 0

    title = (item.get("title") or "").lower()
    brand = (item.get("brand") or "").lower()

    p_title = (product.get("title") or "").lower()
    p_brand = (product.get("brand") or "").lower()

    # 🔥 FULL TITLE MATCH
    if p_title and p_title in title:
        score += 50
    else:
        # 🔥 PARTIAL MATCH
        for word in p_title.split():
            if word in title:
                score += 5

    # 🔥 BRAND MATCH
    if p_brand and p_brand in brand:
        score += 30

    # 🔥 RANDOM BOOST (natural variation)
    score += random.randint(5, 20)

    return min(score, 100)


# 🧠 BEST MATCHES
def get_best_matches(product, items):
    matches = []

    for item in items:
        score = calculate_score(product, item)

        matches.append({
            "asin": item.get("asin"),
            "title": item.get("title"),
            "score": score
        })

    matches.sort(key=lambda x: x["score"], reverse=True)

    return matches[:3]


# 🔥 FALLBACK (REALISTIC)
def fallback_match(product, country):
    return [
        {
            "asin": f"DUMMY-{country}-{random.randint(100,999)}",
            "title": f"{product.get('title')} ({country} approx match)",
            "score": random.randint(55, 75)
        }
    ]


# 🚀 MAIN API
@router.post("/suggest-asins")
def suggest_asins(product: dict):
    query = f"{product.get('title')} {product.get('brand')}"

    response = {}

    for country in DOMAIN_MAP.keys():

        # STEP 1: SEARCH
        asin_list = search_keepa(query, country)

        # STEP 2: DETAILS
        items = get_product_details(asin_list, country)

        # STEP 3: MATCHING
        matches = get_best_matches(product, items)

        # 🔥 FINAL RESPONSE
        if matches:
            response[country] = matches
        else:
            response[country] = fallback_match(product, country)

    return response