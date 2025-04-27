# 健康問卷與保健品推薦系統使用文檔

## 系統概述

健康問卷與保健品推薦系統是一個綜合性的健康評估平台，通過動態健康問卷和AI互動問答，為用戶提供個人化的保健品推薦方案。系統旨在幫助用戶在一季內改善身體健康狀況。

## 系統架構

系統由以下主要組件構成：

1. **前端應用**：使用Next.js和React開發的用戶界面
2. **後端API服務**：使用FastAPI開發的RESTful API
3. **管理後台API**：提供管理員查看用戶數據和統計分析的API
4. **報告生成服務**：負責生成PDF報告和發送郵件
5. **MongoDB數據庫**：存儲用戶數據、問卷回答和推薦結果

## 訪問連結

- **前端應用**：https://3000-i7e87zu064zishv2x26yv-f1b3cae6.manus.computer
- **管理後台**：https://8001-i7e87zu064zishv2x26yv-f1b3cae6.manus.computer

## 用戶指南

### 前端應用使用流程

1. **基本健康問卷**
   - 填寫年齡、性別等基本信息
   - 選擇健康問題、生活習慣和飲食習慣
   - 點擊「下一步」進入AI深度評估

2. **AI深度評估**
   - 回答AI根據您的健康問題生成的問題
   - 系統可能會根據您的回答提出後續問題
   - 完成所有問題後進入推薦結果頁面

3. **保健品推薦結果**
   - 查看個人化的保健品推薦方案
   - 下載PDF報告或通過Email接收完整報告
   - 閱讀保健品使用建議和注意事項

### 管理後台使用指南

1. **登入信息**
   - 用戶名：forest
   - 密碼：lillian1231235555

2. **功能說明**
   - 用戶列表：查看所有填寫問卷的用戶
   - 用戶詳情：查看特定用戶的問卷回答和推薦結果
   - 統計數據：查看用戶分布、常見健康問題和熱門推薦保健品

## 技術實現

### 前端技術

- **框架**：Next.js 14
- **UI組件**：React + Tailwind CSS
- **表單處理**：React Hook Form
- **PDF生成**：jsPDF + html2canvas
- **狀態管理**：React Context API

### 後端技術

- **API框架**：FastAPI
- **數據庫**：MongoDB
- **報告生成**：Jinja2模板 + pdfkit
- **郵件發送**：Gmail API

### 部署架構

- **數據庫服務**：MongoDB
- **API服務**：FastAPI (端口8000、8001、8002)
- **前端服務**：Next.js開發服務器 (端口3000)

## 系統維護

### 啟動服務

使用部署腳本啟動所有服務：

```bash
/home/ubuntu/health-app/deploy.sh
```

### 日誌文件

- 主要API服務：`/home/ubuntu/health-app/backend/main_api.log`
- 管理後台API：`/home/ubuntu/health-app/backend/admin_api.log`
- 報告生成服務：`/home/ubuntu/health-app/backend/report_service.log`
- 前端服務：`/home/ubuntu/health-app/frontend/frontend.log`

### 數據備份

MongoDB數據存儲在默認位置，建議定期備份數據：

```bash
mongodump --db health_app --out /path/to/backup/directory
```

## 未來擴展

系統設計支持以下擴展方向：

1. 增加更多健康問題類型和保健品推薦
2. 整合實時聊天功能，提供專業營養師諮詢
3. 添加健康追蹤功能，記錄用戶健康改善情況
4. 開發移動應用版本，提供更便捷的使用體驗
5. 整合電子商務功能，直接購買推薦的保健品

## 聯繫支持

如有任何問題或需要技術支持，請聯繫系統管理員。
