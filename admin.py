from fastapi import FastAPI, HTTPException, Depends, Body, Request, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional, Any
import json
import os
import pymongo
from datetime import datetime, timedelta
import random
import secrets
import jinja2
import pdfkit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os.path

# 創建FastAPI應用
app = FastAPI(title="健康問卷管理後台API")

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制為特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全認證
security = HTTPBasic()

# 管理員憑證
ADMIN_USERNAME = "forest"
ADMIN_PASSWORD = "lillian1231235555"

# 確保數據目錄存在
os.makedirs("data", exist_ok=True)

# 確保模板目錄存在
os.makedirs("templates", exist_ok=True)

# 連接到MongoDB
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["health_app"]
    users_collection = db["users"]
    reports_collection = db["reports"]
    reminders_collection = db["reminders"]
    settings_collection = db["settings"]
except Exception as e:
    print(f"MongoDB連接錯誤: {e}")
    # 如果無法連接到MongoDB，使用內存存儲作為備用
    users_db = []
    reports_db = []
    reminders_db = []
    settings_db = {"reminder_days": 15, "reminder_enabled": True}

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

class ReminderSettings(BaseModel):
    days: int = 15
    enabled: bool = True

class EmailSettings(BaseModel):
    gmail_user: str
    gmail_password: str

class OpenAISettings(BaseModel):
    api_key: str

# 認證函數
def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認證失敗",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

# 輔助函數
def get_reminder_settings():
    """獲取提醒設置"""
    try:
        settings = settings_collection.find_one({"type": "reminder"})
        if settings:
            return {
                "days": settings.get("days", 15),
                "enabled": settings.get("enabled", True)
            }
        else:
            # 如果設置不存在，創建默認設置
            default_settings = {"type": "reminder", "days": 15, "enabled": True}
            settings_collection.insert_one(default_settings)
            return {"days": 15, "enabled": True}
    except Exception as e:
        print(f"獲取提醒設置時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'settings_db' in globals():
            return {
                "days": settings_db.get("reminder_days", 15),
                "enabled": settings_db.get("reminder_enabled", True)
            }
        return {"days": 15, "enabled": True}

def get_email_settings():
    """獲取郵件設置"""
    try:
        settings = settings_collection.find_one({"type": "email"})
        if settings:
            return {
                "gmail_user": settings.get("gmail_user", ""),
                "gmail_password": settings.get("gmail_password", "")
            }
        else:
            return {"gmail_user": "", "gmail_password": ""}
    except Exception as e:
        print(f"獲取郵件設置時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'settings_db' in globals():
            return {
                "gmail_user": settings_db.get("gmail_user", ""),
                "gmail_password": settings_db.get("gmail_password", "")
            }
        return {"gmail_user": "", "gmail_password": ""}

def get_openai_settings():
    """獲取OpenAI設置"""
    try:
        settings = settings_collection.find_one({"type": "openai"})
        if settings:
            return {"api_key": settings.get("api_key", "")}
        else:
            return {"api_key": ""}
    except Exception as e:
        print(f"獲取OpenAI設置時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'settings_db' in globals():
            return {"api_key": settings_db.get("openai_api_key", "")}
        return {"api_key": ""}

def create_reminder(user_email, report_id):
    """創建提醒"""
    try:
        # 獲取提醒設置
        reminder_settings = get_reminder_settings()
        
        if not reminder_settings["enabled"]:
            return
        
        # 獲取報告數據
        report = reports_collection.find_one({"report_id": report_id})
        if not report:
            print(f"找不到報告: {report_id}")
            return
        
        # 計算提醒日期
        reminder_date = datetime.now() + timedelta(days=reminder_settings["days"])
        
        # 創建提醒數據
        reminder_data = {
            "user_email": user_email,
            "report_id": report_id,
            "created_at": datetime.now(),
            "reminder_date": reminder_date,
            "sent": False,
            "health_data": report.get("health_data", {}),
            "recommendations": report.get("recommendations", {})
        }
        
        # 保存到數據庫
        reminders_collection.insert_one(reminder_data)
    except Exception as e:
        print(f"創建提醒時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'reminders_db' in globals():
            reminder_data = {
                "user_email": user_email,
                "report_id": report_id,
                "created_at": datetime.now(),
                "reminder_date": datetime.now() + timedelta(days=15),
                "sent": False
            }
            reminders_db.append(reminder_data)

def send_email(to_email, subject, html_content, pdf_path=None):
    """發送郵件"""
    try:
        # 獲取郵件設置
        email_settings = get_email_settings()
        
        if not email_settings["gmail_user"] or not email_settings["gmail_password"]:
            print("郵件設置不完整")
            return False
        
        # 創建郵件
        msg = MIMEMultipart()
        msg['From'] = email_settings["gmail_user"]
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # 添加HTML內容
        msg.attach(MIMEText(html_content, 'html'))
        
        # 如果有PDF附件，添加到郵件
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
                msg.attach(attach)
        
        # 發送郵件
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_settings["gmail_user"], email_settings["gmail_password"])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"發送郵件時出錯: {e}")
        return False

def generate_reminder_email(reminder):
    """生成提醒郵件內容"""
    try:
        # 獲取用戶數據
        user_email = reminder.get("user_email")
        health_data = reminder.get("health_data", {})
        recommendations = reminder.get("recommendations", {})
        
        # 獲取基本信息
        basic_info = health_data.get("basicInfo", {})
        gender = "男" if basic_info.get("gender") == "male" else "女" if basic_info.get("gender") == "female" else "其他"
        age = basic_info.get("age", "")
        
        # 獲取症狀和推薦
        symptoms = health_data.get("symptoms", [])
        supplements = recommendations.get("supplements", [])
        
        # 生成郵件內容
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; }}
                .highlight {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                .button {{ display: inline-block; background-color: #3498db; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>健康評估跟進提醒</h1>
                <p>親愛的用戶：</p>
                <p>距離您上次的健康評估已經快三個月了，我們建議您進行一次健康重新評估，以了解您的健康狀況變化並調整保健方案。</p>
                
                <div class="highlight">
                    <h2>您上次的健康評估摘要</h2>
                    <p><strong>基本信息：</strong> {gender}性，{age}歲</p>
                    <p><strong>主要健康問題：</strong> {', '.join(symptoms) if symptoms else '無特定症狀'}</p>
                    <p><strong>推薦保健品：</strong> {', '.join(supplements[:3]) if supplements else '無特定推薦'}</p>
                </div>
                
                <p>定期的健康評估可以幫助您：</p>
                <ul>
                    <li>追蹤健康狀況的改善情況</li>
                    <li>調整保健品使用方案</li>
                    <li>發現潛在的健康問題</li>
                    <li>獲得更個性化的健康建議</li>
                </ul>
                
                <a href="https://3000-i7e87zu064zishv2x26yv-f1b3cae6.manus.computer" class="button">立即進行健康重新評估</a>
                
                <div class="footer">
                    <p>此郵件是系統自動發送的。如果您有任何問題，請回覆此郵件或聯繫我們的客服團隊。</p>
                    <p>© {datetime.now().year} 健康問卷與保健品推薦系統. 保留所有權利.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    except Exception as e:
        print(f"生成提醒郵件內容時出錯: {e}")
        return f"""
        <html>
        <body>
            <h1>健康評估跟進提醒</h1>
            <p>親愛的用戶：</p>
            <p>距離您上次的健康評估已經快三個月了，我們建議您進行一次健康重新評估，以了解您的健康狀況變化並調整保健方案。</p>
            <a href="https://3000-i7e87zu064zishv2x26yv-f1b3cae6.manus.computer">立即進行健康重新評估</a>
        </body>
        </html>
        """

def check_and_send_reminders(background_tasks: BackgroundTasks):
    """檢查並發送提醒"""
    try:
        # 獲取提醒設置
        reminder_settings = get_reminder_settings()
        
        if not reminder_settings["enabled"]:
            return {"success": True, "message": "提醒功能已禁用"}
        
        # 獲取今天應該發送的提醒
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        reminders = reminders_collection.find({
            "reminder_date": {"$gte": today, "$lt": tomorrow},
            "sent": False
        })
        
        sent_count = 0
        for reminder in reminders:
            user_email = reminder.get("user_email")
            if not user_email:
                continue
            
            # 生成提醒郵件內容
            html_content = generate_reminder_email(reminder)
            
            # 發送郵件
            background_tasks.add_task(
                send_email,
                user_email,
                "健康評估跟進提醒",
                html_content
            )
            
            # 更新提醒狀態
            reminders_collection.update_one(
                {"_id": reminder["_id"]},
                {"$set": {"sent": True, "sent_at": datetime.now()}}
            )
            
            sent_count += 1
        
        return {"success": True, "message": f"已發送{sent_count}個提醒"}
    except Exception as e:
        print(f"檢查並發送提醒時出錯: {e}")
        return {"success": False, "message": f"發送提醒時出錯: {str(e)}"}

# API端點
@app.get("/")
async def root():
    return {"message": "健康問卷管理後台API"}

# 用戶管理API端點
@app.get("/api/admin/users", response_model=List[Dict[str, Any]])
async def get_users(_: str = Depends(get_current_admin)):
    """獲取所有用戶"""
    try:
        users = list(users_collection.find({}, {"_id": 0}))
        return users
    except Exception as e:
        print(f"獲取用戶時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'users_db' in globals():
            return users_db
        return []

@app.get("/api/admin/users/{email}", response_model=Dict[str, Any])
async def get_user(email: str, _: str = Depends(get_current_admin)):
    """獲取特定用戶"""
    try:
        user = users_collection.find_one({"email": email}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail=f"找不到用戶: {email}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        print(f"獲取用戶時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'users_db' in globals():
            for user in users_db:
                if user.get("email") == email:
                    return user
            raise HTTPException(status_code=404, detail=f"找不到用戶: {email}")
        raise HTTPException(status_code=500, detail=f"獲取用戶時出錯: {str(e)}")

@app.get("/api/admin/reports", response_model=List[Dict[str, Any]])
async def get_reports(_: str = Depends(get_current_admin)):
    """獲取所有報告"""
    try:
        reports = list(reports_collection.find({}, {"_id": 0}))
        return reports
    except Exception as e:
        print(f"獲取報告時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'reports_db' in globals():
            return reports_db
        return []

@app.get("/api/admin/reports/{report_id}", response_model=Dict[str, Any])
async def get_report(report_id: str, _: str = Depends(get_current_admin)):
    """獲取特定報告"""
    try:
        report = reports_collection.find_one({"report_id": report_id}, {"_id": 0})
        if not report:
            raise HTTPException(status_code=404, detail=f"找不到報告: {report_id}")
        return report
    except HTTPException:
        raise
    except Exception as e:
        print(f"獲取報告時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'reports_db' in globals():
            for report in reports_db:
                if report.get("report_id") == report_id:
                    return report
            raise HTTPException(status_code=404, detail=f"找不到報告: {report_id}")
        raise HTTPException(status_code=500, detail=f"獲取報告時出錯: {str(e)}")

# 提醒管理API端點
@app.get("/api/admin/reminders/settings", response_model=ReminderSettings)
async def get_reminder_settings_api(_: str = Depends(get_current_admin)):
    """獲取提醒設置"""
    settings = get_reminder_settings()
    return ReminderSettings(**settings)

@app.post("/api/admin/reminders/settings", response_model=ReminderSettings)
async def update_reminder_settings_api(settings: ReminderSettings, _: str = Depends(get_current_admin)):
    """更新提醒設置"""
    try:
        settings_dict = settings.dict()
        settings_collection.update_one(
            {"type": "reminder"},
            {"$set": settings_dict},
            upsert=True
        )
        return settings
    except Exception as e:
        print(f"更新提醒設置時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'settings_db' in globals():
            settings_db["reminder_days"] = settings.days
            settings_db["reminder_enabled"] = settings.enabled
            return settings
        raise HTTPException(status_code=500, detail=f"更新提醒設置時出錯: {str(e)}")

@app.get("/api/admin/reminders", response_model=List[Dict[str, Any]])
async def get_reminders(_: str = Depends(get_current_admin)):
    """獲取所有提醒"""
    try:
        reminders = list(reminders_collection.find({}, {"_id": 0}))
        return reminders
    except Exception as e:
        print(f"獲取提醒時出錯: {e}")
        # 如果數據庫操作失敗，使用內存存儲
        if 'reminders_db' i
(Content truncated due to size limit. Use line ranges to read in chunks)