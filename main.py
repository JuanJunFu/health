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
app = FastAPI(title="健康問卷與保健品推薦系統API")

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

# 加載保健品數據
try:
    with open("data/health_supplements.json", "r", encoding="utf-8") as f:
        supplements_data = json.load(f)
except FileNotFoundError:
    supplements_data = {}

# 連接到MongoDB
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["health_app"]
    users_collection = db["users"]
    reports_collection = db["reports"]
    products_collection = db["products"]
except Exception as e:
    print(f"MongoDB連接錯誤: {e}")
    # 如果無法連接到MongoDB，使用內存存儲作為備用
    users_db = []
    reports_db = []
    products_db = []

# 數據模型
class BasicInfo(BaseModel):
    age: str
    gender: str
    height: str
    weight: str

class HealthData(BaseModel):
    basicInfo: BasicInfo
    symptoms: List[str]
    bodySystemIssues: List[str]
    specificConditions: List[str]
    aiAnswers: Dict[str, str] = {}

class RecommendationData(BaseModel):
    supplements: List[str]
    dosage: Dict[str, str]
    usage: Dict[str, str]
    explanation: str

class UserSubmission(BaseModel):
    healthData: HealthData
    email: Optional[str] = None

class Product(BaseModel):
    name: str
    category: str
    description: str
    price: float
    purchase_link: Optional[str] = None
    image_url: Optional[str] = None

# 輔助函數
def generate_recommendations(health_data: HealthData) -> RecommendationData:
    """根據健康數據生成保健品推薦"""
    recommended_supplements = []
    dosage = {}
    usage = {}
    
    # 處理症狀
    for symptom in health_data.symptoms:
        if symptom in supplements_data.get("生理癥狀的營養免疫調理法", {}):
            for supplement in supplements_data["生理癥狀的營養免疫調理法"][symptom]:
                if supplement not in recommended_supplements:
                    recommended_supplements.append(supplement)
    
    # 處理身體系統
    for system in health_data.bodySystemIssues:
        if system in supplements_data.get("身體系統的營養支持", {}):
            for supplement in supplements_data["身體系統的營養支持"][system]:
                if supplement not in recommended_supplements:
                    recommended_supplements.append(supplement)
    
    # 處理特定狀況
    for condition in health_data.specificConditions:
        if condition in supplements_data.get("具體身體狀況的營養對策", {}):
            condition_data = supplements_data["具體身體狀況的營養對策"][condition]
            if isinstance(condition_data, list):
                for supplement in condition_data:
                    if supplement not in recommended_supplements:
                        recommended_supplements.append(supplement)
            elif isinstance(condition_data, dict):
                for key, supplements in condition_data.items():
                    for supplement in supplements:
                        if supplement not in recommended_supplements:
                            recommended_supplements.append(supplement)
    
    # 如果沒有足夠的推薦，添加一些基本保健品
    if len(recommended_supplements) < 2:
        basic_supplements = ["綜合維他命", "魚油", "B群"]
        for supplement in basic_supplements:
            if supplement not in recommended_supplements:
                recommended_supplements.append(supplement)
                if len(recommended_supplements) >= 3:
                    break
    
    # 生成劑量和使用方法
    for supplement in recommended_supplements:
        # 模擬劑量和使用方法
        if "鈣" in supplement:
            dosage[supplement] = "每日1-2次，每次1片"
            usage[supplement] = "飯後服用，避免與茶、咖啡同時服用"
        elif "B群" in supplement:
            dosage[supplement] = "每日1次，每次1片"
            usage[supplement] = "早餐後服用，增加能量代謝"
        elif "魚油" in supplement:
            dosage[supplement] = "每日1次，每次1-2粒"
            usage[supplement] = "餐後服用，幫助吸收"
        elif "OPC" in supplement:
            dosage[supplement] = "每日1次，每次1匙"
            usage[supplement] = "早上空腹服用，用30ml水調勻"
        elif "酵素" in supplement:
            dosage[supplement] = "每餐前服用，每次1-2粒"
            usage[supplement] = "餐前15-30分鐘服用，幫助消化"
        elif "蘆薈" in supplement:
            dosage[supplement] = "每日2-3次，每次30ml"
            usage[supplement] = "稀釋後飲用，可緩解發炎症狀"
        else:
            dosage[supplement] = "每日1次，每次1片"
            usage[supplement] = "飯後服用，效果更佳"
    
    # 生成解釋文本
    symptoms_text = "、".join(health_data.symptoms) if health_data.symptoms else "一般健康維護"
    systems_text = "、".join(health_data.bodySystemIssues) if health_data.bodySystemIssues else "整體身體系統"
    
    explanation = f"""根據您提供的健康信息，我們為您推薦了{len(recommended_supplements)}種保健品。
    這些保健品針對您的{symptoms_text}等症狀，以及{systems_text}等身體系統需求進行了優化選擇。
    堅持使用這些保健品，配合均衡飲食和適當運動，有助於改善您的整體健康狀況。
    建議您在一個季度（約3個月）後進行健康重新評估，以調整保健方案。"""
    
    return RecommendationData(
        supplements=recommended_supplements,
        dosage=dosage,
        usage=usage,
        explanation=explanation
    )

def generate_report_id():
    """生成唯一的報告ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices('0123456789', k=4))
    return f"RPT-{timestamp}-{random_suffix}"

# API端點
@app.get("/")
async def root():
    return {"message": "健康問卷與保健品推薦系統API"}

@app.post("/api/submit", response_model=Dict[str, Any])
async def submit_questionnaire(submission: UserSubmission):
    """提交健康問卷並獲取推薦"""
    try:
        # 生成推薦
        recommendations = generate_recommendations(submission.healthData)
        
        # 生成報告ID
        report_id = generate_report_id()
        
        # 創建報告數據
        report_data = {
            "report_id": report_id,
            "created_at": datetime.now(),
            "health_data": submission.healthData.dict(),
            "recommendations": recommendations.dict(),
            "email": submission.email
        }
        
        # 保存到數據庫
        try:
            reports_collection.insert_one(report_data)
            
            # 如果提供了電子郵件，保存用戶信息
            if submission.email:
                user_data = {
                    "email": submission.email,
                    "basic_info": submission.healthData.basicInfo.dict(),
                    "last_report_id": report_id,
                    "last_assessment_date": datetime.now(),
                    "reports": [report_id]
                }
                
                # 檢查用戶是否已存在
                existing_user = users_collection.find_one({"email": submission.email})
                if existing_user:
                    # 更新現有用戶
                    users_collection.update_one(
                        {"email": submission.email},
                        {
                            "$set": {
                                "basic_info": submission.healthData.basicInfo.dict(),
                                "last_report_id": report_id,
                                "last_assessment_date": datetime.now()
                            },
                            "$push": {"reports": report_id}
                        }
                    )
                else:
                    # 創建新用戶
                    users_collection.insert_one(user_data)
        except Exception as e:
            print(f"數據庫操作錯誤: {e}")
            # 如果數據庫操作失敗，使用內存存儲
            if 'users_db' in globals():
                if submission.email:
                    user_data = {
                        "email": submission.email,
                        "basic_info": submission.healthData.basicInfo.dict(),
                        "last_report_id": report_id,
                        "last_assessment_date": datetime.now(),
                        "reports": [report_id]
                    }
                    users_db.append(user_data)
                reports_db.append(report_data)
        
        # 返回推薦結果和報告ID
        return {
            "success": True,
            "report_id": report_id,
            "recommendations": recommendations.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理問卷時出錯: {str(e)}")

@app.post("/api/ai-questions", response_model=Dict[str, Any])
async def generate_ai_questions(health_data: HealthData):
    """根據健康數據生成AI問題"""
    try:
        questions = []
        
        # 基於症狀生成問題
        if "失眠" in health_data.symptoms:
            questions.append("您的失眠情況持續多久了？是否有特定時間段特別嚴重？")
        
        if "疼痛" in health_data.symptoms:
            questions.append("您的疼痛主要集中在哪些部位？疼痛的性質是怎樣的（如：刺痛、鈍痛、灼熱感等）？")
        
        if "胃部不適" in health_data.symptoms:
            questions.append("您的胃部不適通常在什麼時候發生？是否與進食有關？")
        
        # 基於身體系統問題生成問題
        if "神經系統" in health_data.bodySystemIssues:
            questions.append("您是否經常感到頭痛、頭暈或注意力不集中？這些症狀多久出現一次？")
        
        if "消化系統" in health_data.bodySystemIssues:
            questions.append("您的消化問題主要表現為哪些症狀？是否有食物不耐受的情況？")
        
        # 基於特定身體狀況生成問題
        if "乾眼症" in health_data.specificConditions:
            questions.append("您的乾眼症狀是否與用眼時間或環境因素有關？您目前使用眼藥水嗎？")
        
        if "過敏性鼻炎" in health_data.specificConditions:
            questions.append("您的過敏症狀是季節性的還是全年都有？已知的過敏原有哪些？")
        
        # 如果沒有足夠的問題，添加一些通用問題
        if len(questions) < 3:
            general_questions = [
                "您平時的飲食習慣如何？是否有特定的飲食偏好或限制？",
                "您每週的運動頻率和強度如何？",
                "您的睡眠質量如何？平均每晚睡幾個小時？",
                "您是否正在服用任何藥物或保健品？如果是，請列出名稱和劑量。",
                "您的工作或生活環境是否存在壓力因素？如何應對這些壓力？"
            ]
            
            # 添加通用問題直到達到至少3個問題
            for q in general_questions:
                if q not in questions:
                    questions.append(q)
                    if len(questions) >= 5:
                        break
        
        return {
            "success": True,
            "questions": questions[:5]  # 最多返回5個問題
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成AI問題時出錯: {str(e)}")

@app.post("/api/send-report", response_model=Dict[str, Any])
async def send_report_email(data: Dict[str, str] = Body(...)):
    """發送報告到用戶郵箱"""
    try:
        email = data.get("email")
        report_id = data.get("report_id")
        
        if not email:
            raise HTTPException(status_code=400, detail="缺少電子郵件地址")
        
        if not report_id:
            raise HTTPException(status_code=400, detail="缺少報告ID")
        
        # 在實際應用中，這裡會調用郵件發送服務
        # 現在我們只是模擬發送成功
        
        return {
            "success": True,
            "message": f"報告已成功發送到 {email}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"發送報告時出錯: {str(e)}")

# 產品管理API端點
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
