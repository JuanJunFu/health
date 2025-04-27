#!/bin/bash

# 確保MongoDB服務正在運行
echo "啟動MongoDB服務..."
sudo systemctl start mongod
echo "MongoDB服務已啟動"

# 創建必要的目錄
mkdir -p /home/ubuntu/health-app/backend/pdf_reports
mkdir -p /home/ubuntu/health-app/backend/templates

# 初始化資料庫
echo "初始化資料庫..."
cd /home/ubuntu/health-app/backend
source venv/bin/activate
python init_db.py
echo "資料庫初始化完成"

# 啟動主要API服務
echo "啟動主要API服務..."
cd /home/ubuntu/health-app/backend
source venv/bin/activate
nohup python main.py > main_api.log 2>&1 &
echo "主要API服務已啟動"

# 啟動管理後台API服務
echo "啟動管理後台API服務..."
cd /home/ubuntu/health-app/backend
source venv/bin/activate
nohup python admin.py > admin_api.log 2>&1 &
echo "管理後台API服務已啟動"

# 啟動報告生成服務
echo "啟動報告生成服務..."
cd /home/ubuntu/health-app/backend
source venv/bin/activate
nohup python report_service.py > report_service.log 2>&1 &
echo "報告生成服務已啟動"

# 啟動前端服務
echo "啟動前端服務..."
cd /home/ubuntu/health-app/frontend
nohup npm run dev > frontend.log 2>&1 &
echo "前端服務已啟動"

# 等待服務啟動
echo "等待所有服務啟動..."
sleep 10

# 檢查服務狀態
echo "檢查服務狀態..."
ps aux | grep python | grep -v grep
ps aux | grep npm | grep -v grep

echo "所有服務已啟動，請使用expose_port工具訪問應用"
