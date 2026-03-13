from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Product model
class Product(BaseModel):
    id: int
    name: str
    price: int
    category: str
    in_stock: bool = True

class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


# Initial products
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Keyboard", "price": 899, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 199, "category": "Stationery", "in_stock": True},
]

# Get all products
@app.get("/products")
def get_products():
    return {"total": len(products), "products": products}


# Get product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")


# Add product
@app.post("/products", status_code=201)
def add_product(new_product: NewProduct):

    for product in products:
        if product["name"].lower() == new_product.name.lower():
            raise HTTPException(status_code=400, detail="Product already exists")

    new_id = len(products) + 1

    product_dict = {
        "id": new_id,
        **new_product.dict()
    }

    products.append(product_dict)

    return {"message": "Product added", "product": product_dict}


# Update product
@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):

    for product in products:

        if product["id"] == product_id:

            if price is not None:
                product["price"] = price

            if in_stock is not None:
                product["in_stock"] = in_stock

            return {"message": "Product updated", "product": product}

    raise HTTPException(status_code=404, detail="Product not found")


# Delete product
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for product in products:

        if product["id"] == product_id:
            products.remove(product)
            return {"message": f"Product '{product['name']}' deleted"}

    raise HTTPException(status_code=404, detail="Product not found")