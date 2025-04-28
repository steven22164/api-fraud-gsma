
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict
import firebase_admin
from firebase_admin import credentials, firestore

# 🚀 在這裡加系統介紹
app = FastAPI(
    title="Fraud Risk Detection API (GSMA Open Gateway Standard)",
    description="""
這個 API 系統模擬 GSMA Open Gateway 標準，協助 B 端企業快速驗證門號風險。

B 端只需輸入使用者的手機號碼，API 就會即時串接電信資料、IP資訊、裝置可信度與SIM卡異動記錄，分析出該門號的交易風險指數（Risk Score）及風險等級（Risk Level）。

功能特點：
- 自動檢查門號格式與有效性
- 即時從 Firebase 資料庫讀取用戶資料
- 交叉比對裝置位置、IP來源國與SIM卡異動情形
- 計算並回傳完整的風險分析結果
""",
    version="1.0.0",
)

# 🔥 以下原本的程式碼（直接接續下來）

# 初始化 Firebase
cred = credentials.Certificate("api-fraud-gsma-19e8e-firebase-adminsdk-fbsvc-8d73382f1f.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 請求欄位定義
class RiskRequest(BaseModel):
    phone_number: str = Field(
        ..., 
        example="0912345678", 
        description="使用者輸入的電話號碼，格式必須是台灣手機號碼，長度10碼，開頭09"
    )

# 回傳欄位定義
class RiskResponse(BaseModel):
    phone_number: str
    device_location_region: str
    ip_location_region: str
    device_status: str
    device_verified: bool
    sim_swap_flag: bool
    ip_risk_flag: bool
    risk_score: int
    risk_level: str

def get_user_data(phone_number: str) -> Dict:
    doc_ref = db.collection("users").document(phone_number)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None

def calculate_risk(data: Dict) -> Dict:
    ip_risk_flag = data["device_location_region"][:2] != data["ip_location_region"][:2]
    score = 0
    score += 30 if ip_risk_flag else 0
    score += 30 if not data["device_verified"] else 0
    score += 20 if data["sim_swap_flag"] else 0
    score += (100 - data["device_trust_score"]) * 0.2

    if score >= 80:
        level = "High Risk"
    elif score >= 50:
        level = "Medium Risk"
    else:
        level = "Low Risk"

    return {
        "ip_risk_flag": ip_risk_flag,
        "risk_score": int(score),
        "risk_level": level
    }

@app.post("/risk-check", response_model=RiskResponse)
def risk_check(request: RiskRequest):
    phone_number = request.phone_number

    if not (phone_number.startswith("09") and len(phone_number) == 10 and phone_number.isdigit()):
        raise HTTPException(status_code=400, detail="Wrong phone number format")

    user_data = get_user_data(phone_number)

    if not user_data:
        raise HTTPException(status_code=404, detail="Phone number not found in database")

    risk_result = calculate_risk(user_data)

    return RiskResponse(
        phone_number=phone_number,
        device_location_region=user_data["device_location_region"],
        ip_location_region=user_data["ip_location_region"],
        device_status=user_data["device_status"],
        device_verified=user_data["device_verified"],
        sim_swap_flag=user_data["sim_swap_flag"],
        ip_risk_flag=risk_result["ip_risk_flag"],
        risk_score=risk_result["risk_score"],
        risk_level=risk_result["risk_level"]
    )

@app.post(
    "/risk-check",
    response_model=RiskResponse,
    summary="檢查手機號碼的交易風險",
    description="""
輸入一組手機號碼後，系統會即時從電信資料庫（Firebase）查詢該門號相關資訊，並透過以下五個模組交叉驗證：

- 📍 Device Location（基地台地區）
- 🌐 IP Location（IP位置）
- 🔐 Device Verification（裝置綁定狀態）
- 🔄 SIM Swap Check（近期換卡狀態）
- 📞 Phone Number 格式檢核

綜合各項指標後，計算風險分數（Risk Score）並回傳風險等級（Risk Level）。

如果門號格式錯誤，將回傳 400；若資料庫查無此門號，將回傳 404。
"""
)
def risk_check(request: RiskRequest):
    ...
See
