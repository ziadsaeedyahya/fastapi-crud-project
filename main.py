from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Professional CRUD API")

# --- Models ---
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int

# داتا وهمية (Database Simulation)
db = []

# --- Endpoints ---

# 1. الصفحة الرئيسية (عشان اللينك ميفضلش يحمل)
@app.get("/")
def home():
    return {"message": "Welcome to my FastAPI CRUD! Go to /docs to play with the API"}

# 2. إضافة (Create)
@app.post("/items/", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate):
    new_id = len(db) + 1
    new_item = {"id": new_id, **item.dict()}
    db.append(new_item)
    return new_item

# 3. عرض الكل (Read)
@app.get("/items/", response_model=List[ItemResponse])
def get_items():
    return db

# 4. تعديل (Update)
@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, updated_item: ItemCreate):
    for index, item in enumerate(db):
        if item["id"] == item_id:
            db[index] = {"id": item_id, **updated_item.dict()}
            return db[index]
    raise HTTPException(status_code=404, detail="Item not found")

# 5. مسح (Delete) - الجديدة اهي يا وحش
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    for index, item in enumerate(db):
        if item["id"] == item_id:
            db.pop(index)
            return {"message": f"Item {item_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")