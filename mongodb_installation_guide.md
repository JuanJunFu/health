# MongoDB 安裝與配置指南

本文檔提供在 GCP 虛擬機上安裝和配置 MongoDB 的詳細步驟。

## MongoDB 安裝步驟

### 1. 導入 MongoDB 公鑰

```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
```

### 2. 創建 MongoDB 源列表文件

```bash
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
```

### 3. 更新套件列表

```bash
sudo apt-get update
```

### 4. 安裝 MongoDB 套件

```bash
sudo apt-get install -y mongodb-org
```

### 5. 啟動 MongoDB 服務

```bash
sudo systemctl start mongod
```

### 6. 設置 MongoDB 開機自動啟動

```bash
sudo systemctl enable mongod
```

### 7. 驗證 MongoDB 服務狀態

```bash
sudo systemctl status mongod
```

## 常見問題排除

### 問題：找不到 mongod.service

如果您看到 "Unit mongod.service not found" 錯誤，可能是因為：

1. MongoDB 安裝不完整
2. 服務名稱不正確
3. systemd 未正確識別服務

解決方案：

```bash
# 檢查 MongoDB 是否已安裝
dpkg -l | grep mongodb

# 如果未安裝或安裝不完整，重新安裝
sudo apt-get purge mongodb-org*
sudo apt-get autoremove
# 然後重新執行安裝步驟

# 如果已安裝但服務未啟動，嘗試手動啟動
sudo mongod --config /etc/mongod.conf
```

### 問題：MongoDB 無法啟動

如果 MongoDB 服務無法啟動，可能是因為：

1. 資料目錄權限問題
2. 端口被佔用
3. 配置文件錯誤

解決方案：

```bash
# 檢查日誌
sudo cat /var/log/mongodb/mongod.log

# 修復資料目錄權限
sudo chown -R mongodb:mongodb /var/lib/mongodb
sudo chmod 755 /var/lib/mongodb

# 檢查端口佔用
sudo lsof -i :27017

# 重新啟動服務
sudo systemctl restart mongod
```

## 初始化資料庫

安裝並啟動 MongoDB 後，您可以初始化資料庫：

```bash
# 連接到 MongoDB
mongo

# 創建資料庫
use health_app

# 創建用戶集合
db.createCollection("users")

# 創建推薦集合
db.createCollection("recommendations")

# 創建產品集合
db.createCollection("products")

# 退出 MongoDB shell
exit
```

## 資料庫備份與恢復

### 備份

```bash
mongodump --db health_app --out /home/$(whoami)/mongodb_backup_$(date +%Y%m%d)
```

### 恢復

```bash
mongorestore --db health_app /home/$(whoami)/mongodb_backup_YYYYMMDD/health_app
```

## 下一步

成功安裝 MongoDB 後，您可以繼續部署應用程式的其他部分，包括：

1. 部署後端 API 服務
2. 部署前端應用
3. 配置 Nginx 反向代理
4. 設置系統服務
