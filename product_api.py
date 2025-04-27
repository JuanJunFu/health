from fastapi import FastAPI, HTTPException, Depends, Body, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional, Any
import json
import os
import pymongo
from datetime import datetime
import random

# 創建FastAPI應用
app = FastAPI(title="產品管理API")

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制為特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 確保數據目錄存在
os.makedirs("data", exist_ok=True)

# 連接到MongoDB
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["health_app"]
    products_collection = db["products"]
except Exception as e:
    print(f"MongoDB連接錯誤: {e}")
    # 如果無法連接到MongoDB，使用內存存儲作為備用
    products_db = []

# 數據模型
class Product(BaseModel):
    name: str
    category: str
    description: str
    price: float
    purchase_link: Optional[str] = None
    image_url: Optional[str] = None

# API端點
@app.get("/")
async def root():
    return {"message": "產品管理API"}

@app.get("/api/products", response_model=List[Product])
async def get_products():
    """獲取所有產品"""
    try:
        products = list(products_collection.find({}, {"_id": 0}))
        return products
    except Exception as e:
        print(f"獲取產品時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'products_db' in globals():
            return products_db
        return []

@app.get("/api/products/{product_name}", response_model=Product)
async def get_product(product_name: str):
    """獲取特定產品"""
    try:
        product = products_collection.find_one({"name": product_name}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail=f"找不到產品: {product_name}")
        return product
    except HTTPException:
        raise
    except Exception as e:
        print(f"獲取產品時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'products_db' in globals():
            for product in products_db:
                if product.get("name") == product_name:
                    return product
            raise HTTPException(status_code=404, detail=f"找不到產品: {product_name}")
        raise HTTPException(status_code=500, detail=f"獲取產品時出錯: {str(e)}")

@app.post("/api/products", response_model=Product)
async def create_product(product: Product):
    """創建新產品"""
    try:
        product_dict = product.dict()
        products_collection.insert_one(product_dict)
        # 移除MongoDB的_id字段
        product_dict.pop("_id", None)
        return product_dict
    except Exception as e:
        print(f"創建產品時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'products_db' in globals():
            products_db.append(product.dict())
            return product.dict()
        raise HTTPException(status_code=500, detail=f"創建產品時出錯: {str(e)}")

@app.put("/api/products/{product_name}", response_model=Product)
async def update_product(product_name: str, product: Product):
    """更新產品"""
    try:
        product_dict = product.dict()
        result = products_collection.update_one(
            {"name": product_name},
            {"$set": product_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"找不到產品: {product_name}")
        
        return product_dict
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新產品時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'products_db' in globals():
            for i, p in enumerate(products_db):
                if p.get("name") == product_name:
                    products_db[i] = product.dict()
                    return product.dict()
            raise HTTPException(status_code=404, detail=f"找不到產品: {product_name}")
        raise HTTPException(status_code=500, detail=f"更新產品時出錯: {str(e)}")

@app.delete("/api/products/{product_name}", response_model=Dict[str, Any])
async def delete_product(product_name: str):
    """刪除產品"""
    try:
        result = products_collection.delete_one({"name": product_name})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"找不到產品: {product_name}")
        
        return {"success": True, "message": f"產品已刪除: {product_name}"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"刪除產品時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'products_db' in globals():
            for i, p in enumerate(products_db):
                if p.get("name") == product_name:
                    del products_db[i]
                    return {"success": True, "message": f"產品已刪除: {product_name}"}
            raise HTTPException(status_code=404, detail=f"找不到產品: {product_name}")
        raise HTTPException(status_code=500, detail=f"刪除產品時出錯: {str(e)}")

# 啟動應用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
