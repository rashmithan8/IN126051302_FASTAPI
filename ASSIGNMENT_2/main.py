from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# -----------------------------
# Sample Product Database
# -----------------------------
products = [
    {"id": 1, "name": "Wireless Mouse", "category": "electronics", "price": 499, "in_stock": True},
    {"id": 2, "name": "USB Hub", "category": "electronics", "price": 799, "in_stock": True},
    {"id": 3, "name": "Gaming Keyboard", "category": "electronics", "price": 1299, "in_stock": True},
    {"id": 4, "name": "Office Chair", "category": "furniture", "price": 4500, "in_stock": False},
    {"id": 5, "name": "Desk Lamp", "category": "furniture", "price": 999, "in_stock": True},
]

# --------------------------------------------------
# Q1 — Filter Products (min_price query parameter)
# --------------------------------------------------
@app.get("/products/filter")
def filter_products(
    category: Optional[str] = Query(None, description="Product category"),
    max_price: Optional[int] = Query(None, description="Maximum price"),
    min_price: Optional[int] = Query(None, description="Minimum price")
):

    result = products

    if category:
        result = [p for p in result if p["category"] == category]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    return {"filtered_products": result}


# --------------------------------------------------
# Q2 — Get Product Price
# --------------------------------------------------
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "product_name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}


# --------------------------------------------------
# Q3 — Customer Feedback (POST)
# --------------------------------------------------
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


feedback_list = []


@app.post("/feedback")
def submit_feedback(feedback: CustomerFeedback):

    feedback_list.append(feedback.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": feedback.dict(),
        "total_feedback": len(feedback_list)
    }


# --------------------------------------------------
# Q4 — Product Summary Dashboard
# --------------------------------------------------
@app.get("/products/summary")
def product_summary():

    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    most_expensive = max(products, key=lambda x: x["price"])
    cheapest = min(products, key=lambda x: x["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive_product": most_expensive["name"],
        "cheapest_product": cheapest["name"],
        "categories_available": categories
    }


# --------------------------------------------------
# Q5 — Bulk Order API
# --------------------------------------------------
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)


class BulkOrder(BaseModel):
    company_name: str
    contact_email: str
    items: List[OrderItem]


@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    total_price = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })

        elif not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })

        else:
            subtotal = product["price"] * item.quantity
            total_price += subtotal

            confirmed.append({
                "product_name": product["name"],
                "quantity": item.quantity,
                "subtotal": subtotal
            })

    return {
        "company": order.company_name,
        "confirmed_orders": confirmed,
        "failed_orders": failed,
        "grand_total": total_price
    }