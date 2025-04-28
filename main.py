
from fastapi import FastAPI
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase（這段你應該已經有）
cred = credentials.Certificate("你的-service-account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 只需要 phone_number 的 Request
class RiskRequest(BaseModel):
    phone_number: str

# Response格式（如果你有定義，可以保留）
class RiskResponse(BaseModel):
    risk_score: int
    risk_level: str

app = FastAPI()

@app.post("/risk-check", response_model=RiskResponse, summary="檢查手機號碼的交易風險")
async def risk_check(request: RiskRequest):
    phone_number = request.phone_number

    # 從 Firestore 查資料
    doc_ref = db.collection("users").document(phone_number)
    doc = doc_ref.get()

    if not doc.exists:
        # 如果找不到這個門號
        return {"risk_score": 0, "risk_level": "not_found"}

    data = doc.to_dict()

    # 根據資料計算簡單的風險分數
    score = 0
    if data.get("device_location_region") != data.get("ip_location_region"):
        score += 30
    if not data.get("device_verified", True):
        score += 20
    if data.get("sim_swap_flag"):
        score += 50

    # 判斷等級
    if score >= 70:
        level = "high"
    elif score >= 30:
        level = "medium"
    else:
        level = "low"

    return {"risk_score": score, "risk_level": level}

