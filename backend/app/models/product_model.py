def product_helper(product):
    return {
        "id": str(product["_id"]),
        "title": product["title"],
        "brand": product.get("brand"),
        "ean": product.get("ean"),
        "asins": product.get("asins", {})
    }