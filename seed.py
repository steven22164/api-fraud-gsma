import firebase_admin
from firebase_admin import credentials, firestore
import random

# 初始化 Firebase Admin
cred = credentials.Certificate("api-fraud-gsma-19e8e-firebase-adminsdk-fbsvc-8d73382f1f.json")
firebase_admin.initialize_app(cred)

# 連到 Firestore
db = firestore.client()

# 生成 100筆測試資料
for _ in range(100):
    phone_number = f"09{random.randint(10000000, 99999999)}"
    data = {
        "device_location_region": "TW-TPE",
        "ip_location_region": random.choice(["TW-TPE", "JP-TYO", "VN-HAN"]),
        "device_status": random.choice(["active", "inactive"]),
        "device_trust_score": random.randint(50, 100),
        "sim_change_days": random.randint(0, 10),
        "device_verified": random.choice([True, False]),
        "sim_swap_flag": random.choice([True, False]),
    }
    # 上傳到 Firestore 的 "users" collection
    db.collection("users").document(phone_number).set(data)

print("✅ 資料庫初始化完成！（已上傳 100 筆手機資料）")
