from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict
import random

app = FastAPI()

# 模擬的 fake 資料庫（100筆）
mock_database = {
    f"09{random.randint(10000000, 99999999)}": {
        "device_location_region": "TW-TPE",
        "ip_location_region": random.choice(["TW-TPE", "JP-TYO", "VN-HAN"]),
        "device_status": random.choice(["active", "inactive"]),
        "device_trust_score": random.randint(50, 100),
        "sim_change_days": random.randint(0, 10),
        "device_verified": random.choice([True, False]),
        "sim_swap_flag": random.choice([True, False]),
    }
    for _ in range(100)
}

class RiskRequest(BaseModel):
    phone_number: str = Field(..., example="0912345678")

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

def calculate_risk(data: Dict) -> Dict:
    # 交叉比對
    ip_risk_flag = data["device_location_region"][:2] != data["ip_location_region"][:2]

    # 計算分數
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

    # 格式檢查：長度不對或開頭不是 09
    if not (phone_number.startswith("09") and len(phone_number) == 10 and phone_number.isdigit()):
        raise HTTPException(status_code=400, detail="Wrong phone number format")

    # 查 fake 資料庫
    user_data = mock_database.get(phone_number)

    # 找不到
    if not user_data:
        raise HTTPException(status_code=404, detail="Phone number not found in database")

    # 風險評分
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

