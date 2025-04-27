#!/bin/bash

# 啟動所有服務的腳本

# 設置工作目錄
cd /home/ubuntu/health-app

# 啟動MongoDB服務
echo "啟動MongoDB服務..."
sudo systemctl start mongod || echo "MongoDB服務啟動失敗，可能已經在運行"

# 啟動主要API服務
echo "啟動主要API服務..."
cd backend
source venv/bin/activate
nohup python main.py > main_api.log 2>&1 &
echo $! > main_api.pid
echo "主要API服務已啟動，PID: $(cat main_api.pid)"

# 啟動產品管理API服務
echo "啟動產品管理API服務..."
nohup python product_api.py > product_api.log 2>&1 &
echo $! > product_api.pid
echo "產品管理API服務已啟動，PID: $(cat product_api.pid)"

# 啟動提醒系統API服務
echo "啟動提醒系統API服務..."
nohup python reminder_service.py > reminder_service.log 2>&1 &
echo $! > reminder_service.pid
echo "提醒系統API服務已啟動，PID: $(cat reminder_service.pid)"

# 啟動前端服務
echo "啟動前端服務..."
cd ../frontend
npm run build
nohup npm start > frontend.log 2>&1 &
echo $! > frontend.pid
echo "前端服務已啟動，PID: $(cat frontend.pid)"

echo "所有服務已啟動，請等待幾秒鐘讓服務完全初始化..."
sleep 5

echo "服務啟動完成！"
echo "前端訪問地址: http://localhost:3000"
echo "主要API地址: http://localhost:8001"
echo "產品管理API地址: http://localhost:8003"
echo "提醒系統API地址: http://localhost:8004"
