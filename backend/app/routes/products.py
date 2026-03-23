from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.database.db import products_collection
from app.models.product_model import product_helper

router = APIRouter()

# 🔥 CONSTANT (IMPORTANT)
COUNTRIES = ["US", "UK", "DE", "FR", "IT", "ES"]
TOTAL_COUNTRIES = len(COUNTRIES)


# ✅ GET ALL PRODUCTS
@router.get("/products")
def get_products():
    try:
        products = products_collection.find()
        return [product_helper(p) for p in products]
    except Exception as e:
        print("GET PRODUCTS ERROR:", e)
        return []


# ✅ CREATE PRODUCT
@router.post("/products")
def create_product(product: dict):
    try:
        product["asins"] = {}
        result = products_collection.insert_one(product)

        return {
            "id": str(result.inserted_id),
            "message": "Product created successfully"
        }

    except Exception as e:
        print("CREATE ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to create product")


# 🔥 FINAL STATS API (REAL LOGIC)
@router.get("/products/stats")
def get_stats():
    try:
        products = list(products_collection.find())

        total_products = len(products)
        total_asins = 0
        pending = 0

        # ✅ country-wise tracking
        country_data = {c: 0 for c in COUNTRIES}

        for p in products:
            asins = p.get("asins") or {}

            valid_count = 0

            for country in COUNTRIES:
                value = asins.get(country)

                if value and value.strip() != "":
                    valid_count += 1
                    country_data[country] += 1

            total_asins += valid_count

            # 🔥 FIXED LOGIC (IMPORTANT)
            if valid_count < TOTAL_COUNTRIES:
                pending += 1

        return {
            "total": total_products,
            "mapped": total_asins,  # total mapped ASINs
            "pending": pending,     # incomplete products
            "countries": TOTAL_COUNTRIES,
            "countryData": country_data
        }

    except Exception as e:
        print("STATS ERROR:", e)

        return {
            "total": 0,
            "mapped": 0,
            "pending": 0,
            "countries": TOTAL_COUNTRIES,
            "countryData": {c: 0 for c in COUNTRIES}
        }


# ✅ GET SINGLE PRODUCT
@router.get("/products/{id}")
def get_product(id: str):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID")

        product = products_collection.find_one({"_id": ObjectId(id)})

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return product_helper(product)

    except HTTPException as e:
        raise e

    except Exception as e:
        print("GET PRODUCT ERROR:", e)
        raise HTTPException(status_code=500, detail="Server error")


# ✅ UPDATE ASINS
@router.put("/products/{id}")
def update_product(id: str, data: dict):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID")

        asins = data.get("asins")

        if not isinstance(asins, dict):
            raise HTTPException(status_code=400, detail="Invalid ASIN data")

        products_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"asins": asins}}
        )

        return {"message": "ASINs updated successfully"}

    except HTTPException as e:
        raise e

    except Exception as e:
        print("UPDATE ERROR:", e)
        raise HTTPException(status_code=500, detail="Update failed")