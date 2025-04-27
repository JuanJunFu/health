from pymongo import MongoClient
import json
from datetime import datetime
import os

# 資料庫初始化腳本
def initialize_database():
    try:
        # 連接到MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        
        # 創建或獲取資料庫
        db = client['health_app']
        
        # 創建集合
        users_collection = db['users']
        recommendations_collection = db['recommendations']
        
        # 創建索引
        users_collection.create_index([('created_at', -1)])
        recommendations_collection.create_index([('user_id', 1)])
        
        # 載入保健品資料
        supplements_data = {}
        try:
            with open("data/health_supplements.json", "r", encoding="utf-8") as f:
                supplements_data = json.load(f)
                
            # 創建保健品集合
            supplements_collection = db['supplements']
            
            # 清空現有資料
            supplements_collection.delete_many({})
            
            # 插入保健品資料
            for category, items in supplements_data.items():
                if isinstance(items, dict):
                    for subcategory, products in items.items():
                        if isinstance(products, list):
                            for product in products:
                                supplements_collection.insert_one({
                                    'category': category,
                                    'subcategory': subcategory,
                                    'product': product,
                                    'created_at': datetime.now()
                                })
                        elif isinstance(products, dict):
                            for usage, usage_products in products.items():
                                for product in usage_products:
                                    supplements_collection.insert_one({
                                        'category': category,
                                        'subcategory': subcategory,
                                        'usage': usage,
                                        'product': product,
                                        'created_at': datetime.now()
                                    })
                elif isinstance(items, dict):
                    for product, description in items.items():
                        supplements_collection.insert_one({
                            'category': category,
                            'product': product,
                            'description': description,
                            'created_at': datetime.now()
                        })
            
            print("保健品資料已成功載入到資料庫")
        except Exception as e:
            print(f"載入保健品資料失敗: {e}")
        
        # 創建管理員集合並添加預設管理員
        admin_collection = db['admins']
        
        # 檢查是否已存在管理員
        if admin_collection.count_documents({}) == 0:
            admin_collection.insert_one({
                'username': 'forest',
                'password': 'lillian1231235555',  # 實際應用中應該使用加密密碼
                'created_at': datetime.now()
            })
            print("預設管理員已創建")
        
        print("資料庫初始化完成")
        return True
    except Exception as e:
        print(f"資料庫初始化失敗: {e}")
        return False

if __name__ == "__main__":
    initialize_database()
