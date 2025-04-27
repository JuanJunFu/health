from fastapi import FastAPI, HTTPException, Depends, Body, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional, Any
import json
import os
import pymongo
from datetime import datetime
import random
import jinja2
import pdfkit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os.path

# 創建FastAPI應用
app = FastAPI(title="報告生成與郵件發送API")

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

# 確保模板目錄存在
os.makedirs("templates", exist_ok=True)

# 確保報告目錄存在
os.makedirs("reports", exist_ok=True)

# 連接到MongoDB
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["health_app"]
    reports_collection = db["reports"]
    settings_collection = db["settings"]
except Exception as e:
    print(f"MongoDB連接錯誤: {e}")
    # 如果無法連接到MongoDB，使用內存存儲作為備用
    reports_db = []
    settings_db = {}

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

class ReportRequest(BaseModel):
    report_id: str
    email: Optional[str] = None

# 創建報告模板
report_template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>健康評估與保健品推薦報告</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .section {
            margin-bottom: 30px;
            padding: 15px;
            border-radius: 5px;
        }
        .basic-info {
            background-color: #f8f9fa;
        }
        .symptoms {
            background-color: #e8f4f8;
        }
        .recommendations {
            background-color: #e8f8ef;
        }
        .usage {
            background-color: #f8f4e8;
        }
        .footer {
            margin-top: 50px;
            font-size: 12px;
            text-align: center;
            color: #7f8c8d;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .supplement-item {
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px dashed #ddd;
        }
        .supplement-name {
            font-weight: bold;
            color: #3498db;
        }
        .disclaimer {
            font-style: italic;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>健康評估與保健品推薦報告</h1>
        <p>報告生成日期：{{ report_date }}</p>
        <p>報告編號：{{ report_id }}</p>
    </div>

    <div class="section basic-info">
        <h2>基本信息</h2>
        <table>
            <tr>
                <th>性別</th>
                <td>{{ gender }}</td>
                <th>年齡</th>
                <td>{{ age }}</td>
            </tr>
            <tr>
                <th>身高</th>
                <td>{{ height }} cm</td>
                <th>體重</th>
                <td>{{ weight }} kg</td>
            </tr>
        </table>
    </div>

    {% if symptoms %}
    <div class="section symptoms">
        <h2>健康狀況摘要</h2>
        
        {% if symptoms %}
        <h3>主要症狀</h3>
        <ul>
            {% for symptom in symptoms %}
            <li>{{ symptom }}</li>
            {% endfor %}
        </ul>
        {% endif %}
        
        {% if body_systems %}
        <h3>需要支持的身體系統</h3>
        <ul>
            {% for system in body_systems %}
            <li>{{ system }}</li>
            {% endfor %}
        </ul>
        {% endif %}
        
        {% if conditions %}
        <h3>特定身體狀況</h3>
        <ul>
            {% for condition in conditions %}
            <li>{{ condition }}</li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
    {% endif %}

    {% if ai_answers %}
    <div class="section">
        <h2>深度健康評估</h2>
        {% for question, answer in ai_answers.items() %}
        <div style="margin-bottom: 15px;">
            <p style="font-weight: bold;">{{ question }}</p>
            <p>{{ answer }}</p>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="section recommendations">
        <h2>保健品推薦</h2>
        <p>{{ explanation }}</p>
        
        {% for supplement in supplements %}
        <div class="supplement-item">
            <div class="supplement-name">{{ supplement }}</div>
            <table>
                <tr>
                    <th>建議劑量</th>
                    <td>{{ dosage[supplement] }}</td>
                </tr>
                <tr>
                    <th>使用方法</th>
                    <td>{{ usage[supplement] }}</td>
                </tr>
            </table>
        </div>
        {% endfor %}
    </div>

    <div class="section usage">
        <h2>使用建議</h2>
        <ul>
            <li>保健品應作為均衡飲食的補充，不能替代正常飲食</li>
            <li>請按照建議劑量服用，不要過量</li>
            <li>如有慢性疾病或正在服用藥物，請在服用前諮詢醫生</li>
            <li>保持規律作息和適當運動，效果更佳</li>
            <li>建議在3個月後重新評估健康狀況，調整保健方案</li>
        </ul>
    </div>

    <div class="footer">
        <p class="disclaimer">本報告僅供參考，不構成醫療建議。如有健康問題，請諮詢專業醫療人員。</p>
        <p>© {{ current_year }} 健康問卷與保健品推薦系統. 保留所有權利.</p>
    </div>
</body>
</html>
"""

# 將模板保存到文件
with open("templates/report_template.html", "w", encoding="utf-8") as f:
    f.write(report_template)

# 輔助函數
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

def generate_report_html(report_data):
    """生成報告HTML"""
    try:
        # 獲取報告數據
        report_id = report_data.get("report_id", "未知")
        health_data = report_data.get("health_data", {})
        recommendations = report_data.get("recommendations", {})
        
        # 獲取基本信息
        basic_info = health_data.get("basicInfo", {})
        gender_map = {"male": "男", "female": "女", "other": "其他"}
        gender = gender_map.get(basic_info.get("gender", ""), "未知")
        age = basic_info.get("age", "")
        height = basic_info.get("height", "")
        weight = basic_info.get("weight", "")
        
        # 獲取症狀和身體系統
        symptoms = health_data.get("symptoms", [])
        body_systems = health_data.get("bodySystemIssues", [])
        conditions = health_data.get("specificConditions", [])
        ai_answers = health_data.get("aiAnswers", {})
        
        # 獲取推薦
        supplements = recommendations.get("supplements", [])
        dosage = recommendations.get("dosage", {})
        usage = recommendations.get("usage", {})
        explanation = recommendations.get("explanation", "")
        
        # 創建Jinja2環境
        env = jinja2.Environment()
        template = env.from_string(report_template)
        
        # 渲染模板
        html = template.render(
            report_id=report_id,
            report_date=datetime.now().strftime("%Y-%m-%d"),
            current_year=datetime.now().year,
            gender=gender,
            age=age,
            height=height,
            weight=weight,
            symptoms=symptoms,
            body_systems=body_systems,
            conditions=conditions,
            ai_answers=ai_answers,
            supplements=supplements,
            dosage=dosage,
            usage=usage,
            explanation=explanation
        )
        
        return html
    except Exception as e:
        print(f"生成報告HTML時出錯: {e}")
        return f"""
        <html>
        <body>
            <h1>健康評估與保健品推薦報告</h1>
            <p>報告生成時出錯: {str(e)}</p>
        </body>
        </html>
        """

def generate_report_pdf(report_id, html_content):
    """生成報告PDF"""
    try:
        # 保存HTML到臨時文件
        html_path = f"reports/{report_id}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # 生成PDF
        pdf_path = f"reports/{report_id}.pdf"
        pdfkit.from_file(html_path, pdf_path)
        
        return pdf_path
    except Exception as e:
        print(f"生成報告PDF時出錯: {e}")
        return None

def send_report_email(to_email, report_id, html_content):
    """發送報告郵件"""
    try:
        # 獲取郵件設置
        email_settings = get_email_settings()
        
        if not email_settings["gmail_user"] or not email_settings["gmail_password"]:
            print("郵件設置不完整")
            return False
        
        # 生成PDF
        pdf_path = generate_report_pdf(report_id, html_content)
        
        # 創建郵件
        msg = MIMEMultipart()
        msg['From'] = email_settings["gmail_user"]
        msg['To'] = to_email
        msg['Subject'] = "您的健康評估與保健品推薦報告"
        
        # 添加HTML內容
        msg.attach(MIMEText(html_content, 'html'))
        
        # 如果有PDF附件，添加到郵件
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', filename=f"健康評估報告_{report_id}.pdf")
                msg.attach(attach)
        
        # 發送郵件
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_settings["gmail_user"], email_settings["gmail_password"])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"發送報告郵件時出錯: {e}")
        return False

# API端點
@app.get("/")
async def root():
    return {"message": "報告生成與郵件發送API"}

@app.get("/api/report/{report_id}", response_class=HTMLResponse)
async def get_report_html(report_id: str):
    """獲取報告HTML"""
    try:
        # 獲取報告數據
        report = reports_collection.find_one({"report_id": report_id})
        if not report:
            raise HTTPException(status_code=404, detail=f"找不到報告: {report_id}")
        
        # 生成報告HTML
        html = generate_report_html(report)
        
        return HTMLResponse(content=html)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取報告時出錯: {str(e)}")

@app.get("/api/report/{report_id}/pdf")
async def get_report_pdf(report_id: str):
    """獲取報告PDF"""
    try:
        # 獲取報告數據
        report = reports_collection.find_one({"report_id": report_id})
        if not report:
            raise HTTPException(status_code=404, detail=f"找不到報告: {report_id}")
        
        # 生成報告HTML
        html = generate_report_html(report)
        
        # 生成報告PDF
        pdf_path = generate_report_pdf(report_id, html)
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="生成PDF失敗")
        
        return FileResponse(pdf_path, filename=f"健康評估報告_{report_id}.pdf")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取報告時出錯: {str(e)}")

@app.post("/api/report/send", response_model=Dict[str, Any])
async def send_report(request: ReportRequest):
    """發送報告郵件"""
    try:
        report_id = request.report_id
        email = request.email
        
        if not email:
            raise HTTPException(status_code=400, detail="缺少電子郵件地址")
        
        # 獲取報告數據
        report = reports_collection.find_one({"report_id": report_id})
        if not report:
            raise HTTPException(status_code=404, detail=f"找不到報告: {report_id}")
        
        # 生成報告HTML
        html = generate_report_html(report)
        
        # 發送郵件
        success = send_report_email(email, report_id, html)
        
        if success:
            return {"success": True, "message": f"報告已成功發送到 {email}"}
        else:
            return {"success": False, "message": "發送報告失敗，請檢查郵件設置"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"發送報告時出錯: {str(e)}")

# 啟動應用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
