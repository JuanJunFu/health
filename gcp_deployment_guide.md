# GCP部署指南 - 健康問卷與保健品推薦系統

本文檔提供在Google Cloud Platform (GCP)上部署健康問卷與保健品推薦系統的完整步驟。

## 前置準備

1. 擁有GCP帳戶並創建一個新項目
2. 安裝並設置Google Cloud SDK
3. 啟用必要的API服務：Compute Engine, Cloud Build, Container Registry

## 部署架構

我們將使用以下GCP服務進行部署：

- **Compute Engine**: 運行應用程序的虛擬機
- **Cloud SQL**: MongoDB數據庫(或使用VM上的MongoDB)
- **Cloud Storage**: 存儲靜態資源和報告
- **Secret Manager**: 存儲敏感信息(如Gmail和OpenAI憑證)

## 部署步驟

### 1. 創建虛擬機實例

```bash
# 創建VM實例
gcloud compute instances create health-app-vm \
  --zone=asia-east1-b \
  --machine-type=e2-medium \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB \
  --tags=http-server,https-server

# 創建防火牆規則允許HTTP/HTTPS流量
gcloud compute firewall-rules create allow-http \
  --allow tcp:80,tcp:443 \
  --target-tags=http-server,https-server
```

### 2. 連接到虛擬機

```bash
gcloud compute ssh health-app-vm --zone=asia-east1-b
```

### 3. 安裝必要的軟件

```bash
# 更新系統
sudo apt-get update
sudo apt-get upgrade -y

# 安裝Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安裝Python和pip
sudo apt-get install -y python3-pip python3-venv

# 安裝MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# 安裝Nginx
sudo apt-get install -y nginx

# 安裝wkhtmltopdf (用於PDF生成)
sudo apt-get install -y wkhtmltopdf
```

### 4. 設置Secret Manager存儲敏感信息

```bash
# 創建Secret Manager密鑰
gcloud secrets create gmail-credentials --replication-policy="automatic"
gcloud secrets create openai-api-key --replication-policy="automatic"

# 設置Gmail憑證
echo '{"username": "your-email@gmail.com", "password": "your-app-password"}' | \
gcloud secrets versions add gmail-credentials --data-file=-

# 設置OpenAI API密鑰
echo 'your-openai-api-key' | gcloud secrets versions add openai-api-key --data-file=-
```

### 5. 克隆和設置應用程序

```bash
# 克隆代碼庫(假設您已將代碼推送到GitHub)
git clone https://github.com/your-username/health-app.git
cd health-app

# 設置前端
cd frontend
npm install
npm run build

# 設置後端
cd ../backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 創建必要的目錄
mkdir -p pdf_reports
mkdir -p templates
```

### 6. 修改配置文件以適應GCP環境

創建後端配置文件 `backend/config.py`:

```python
import os
import json
import subprocess

# 嘗試從Secret Manager獲取憑證
def get_secret(secret_id):
    try:
        result = subprocess.run(
            ['gcloud', 'secrets', 'versions', 'access', 'latest', '--secret', secret_id],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"無法獲取密鑰 {secret_id}: {e}")
        return None

# Gmail憑證
gmail_secret = get_secret('gmail-credentials')
if gmail_secret:
    try:
        gmail_config = json.loads(gmail_secret)
        GMAIL_USERNAME = gmail_config.get('username')
        GMAIL_PASSWORD = gmail_config.get('password')
    except:
        GMAIL_USERNAME = "your-email@gmail.com"
        GMAIL_PASSWORD = "your-app-password"
else:
    GMAIL_USERNAME = "your-email@gmail.com"
    GMAIL_PASSWORD = "your-app-password"

# OpenAI API密鑰
OPENAI_API_KEY = get_secret('openai-api-key') or "your-openai-api-key"

# MongoDB配置
MONGODB_URI = "mongodb://localhost:27017/"
MONGODB_DB = "health_app"

# 應用配置
DEBUG = False
HOST = "0.0.0.0"
MAIN_API_PORT = 8000
ADMIN_API_PORT = 8001
REPORT_API_PORT = 8002
```

### 7. 修改後端服務以使用配置

修改 `main.py`, `admin.py` 和 `report_service.py` 以使用配置文件:

```python
# 在每個文件頂部添加
import sys
sys.path.append('.')
from config import *

# 替換MongoDB連接
client = pymongo.MongoClient(MONGODB_URI)
db = client[MONGODB_DB]

# 在Gmail發送功能中使用憑證
smtp_username = GMAIL_USERNAME
smtp_password = GMAIL_PASSWORD

# 在底部運行服務器時使用配置
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
```

### 8. 設置Nginx作為反向代理

創建Nginx配置文件:

```bash
sudo nano /etc/nginx/sites-available/health-app
```

添加以下內容:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替換為您的域名

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /admin-api/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /report-api/ {
        proxy_pass http://localhost:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

啟用配置:

```bash
sudo ln -s /etc/nginx/sites-available/health-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. 創建服務啟動腳本

創建 `start_services.sh`:

```bash
#!/bin/bash

# 確保MongoDB服務正在運行
echo "檢查MongoDB服務..."
sudo systemctl start mongod

# 初始化資料庫
echo "初始化資料庫..."
cd /home/your-username/health-app/backend
source venv/bin/activate
python init_db.py

# 啟動主要API服務
echo "啟動主要API服務..."
cd /home/your-username/health-app/backend
source venv/bin/activate
nohup python main.py > main_api.log 2>&1 &

# 啟動管理後台API服務
echo "啟動管理後台API服務..."
cd /home/your-username/health-app/backend
source venv/bin/activate
nohup python admin.py > admin_api.log 2>&1 &

# 啟動報告生成服務
echo "啟動報告生成服務..."
cd /home/your-username/health-app/backend
source venv/bin/activate
nohup python report_service.py > report_service.log 2>&1 &

# 啟動前端服務
echo "啟動前端服務..."
cd /home/your-username/health-app/frontend
nohup npm start > frontend.log 2>&1 &

echo "所有服務已啟動"
```

設置執行權限:

```bash
chmod +x start_services.sh
```

### 10. 設置系統服務以自動啟動應用

創建systemd服務文件:

```bash
sudo nano /etc/systemd/system/health-app.service
```

添加以下內容:

```
[Unit]
Description=Health App Service
After=network.target mongodb.service

[Service]
User=your-username
WorkingDirectory=/home/your-username/health-app
ExecStart=/home/your-username/health-app/start_services.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

啟用服務:

```bash
sudo systemctl enable health-app
sudo systemctl start health-app
```

### 11. 設置HTTPS (可選但推薦)

使用Let's Encrypt獲取SSL證書:

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 12. 設置定期備份 (推薦)

創建備份腳本 `backup.sh`:

```bash
#!/bin/bash

# 設置變數
BACKUP_DIR="/home/your-username/backups"
DATE=$(date +%Y%m%d_%H%M%S)
MONGODB_DB="health_app"

# 創建備份目錄
mkdir -p $BACKUP_DIR

# 備份MongoDB
mongodump --db $MONGODB_DB --out $BACKUP_DIR/mongodb_$DATE

# 壓縮備份
tar -czf $BACKUP_DIR/mongodb_$DATE.tar.gz $BACKUP_DIR/mongodb_$DATE
rm -rf $BACKUP_DIR/mongodb_$DATE

# 保留最近10個備份
ls -t $BACKUP_DIR/mongodb_*.tar.gz | tail -n +11 | xargs -r rm

echo "備份完成: $BACKUP_DIR/mongodb_$DATE.tar.gz"
```

設置執行權限:

```bash
chmod +x backup.sh
```

添加到crontab以定期執行:

```bash
crontab -e
```

添加以下行以每天凌晨2點執行備份:

```
0 2 * * * /home/your-username/health-app/backup.sh
```

## 使用Google Cloud Storage進行備份 (可選)

如果您想將備份存儲在Google Cloud Storage:

```bash
# 安裝gsutil
sudo apt-get install -y google-cloud-sdk-gsutil

# 修改備份腳本，添加上傳到GCS的命令
echo "# 上傳到Google Cloud Storage" >> backup.sh
echo "gsutil cp $BACKUP_DIR/mongodb_$DATE.tar.gz gs://your-bucket-name/" >> backup.sh
```

## 監控和日誌

您可以使用以下命令檢查服務狀態:

```bash
# 檢查MongoDB狀態
sudo systemctl status mongod

# 檢查應用服務狀態
sudo systemctl status health-app

# 查看日誌
tail -f /home/your-username/health-app/backend/main_api.log
tail -f /home/your-username/health-app/backend/admin_api.log
tail -f /home/your-username/health-app/backend/report_service.log
tail -f /home/your-username/health-app/frontend/frontend.log
```

## 故障排除

1. 如果服務無法啟動，檢查日誌文件
2. 確保MongoDB服務正在運行
3. 檢查防火牆設置是否允許必要的端口
4. 確保所有依賴項都已正確安裝

## 更新應用程序

當您需要更新應用程序時:

```bash
# 停止服務
sudo systemctl stop health-app

# 拉取最新代碼
cd /home/your-username/health-app
git pull

# 更新前端
cd frontend
npm install
npm run build

# 更新後端
cd ../backend
source venv/bin/activate
pip install -r requirements.txt

# 重啟服務
sudo systemctl start health-app
```

## 使用Docker部署 (替代方案)

如果您偏好使用Docker進行部署，以下是基本步驟:

1. 在應用程序根目錄創建Dockerfile和docker-compose.yml
2. 構建和運行容器
3. 設置Nginx反向代理

這需要額外的Docker配置，如果您有興趣使用這種方法，請告知我們可以提供詳細指南。
