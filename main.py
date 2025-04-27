from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# 請求模型
class RiskRequest(BaseModel):
    phone_number: str = Field(..., example="0912345678")

# 回應模型
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

# 假資料庫
mock_database = {
    "0912345678": {
        "device_location_region": "TW-TPE",
        "ip_location_region": "TW-TPE",
        "device_status": "active",
        "device_verified": True,
        "sim_change_days": 3,
    },
    "0987654321": {
        "device_location_region": "US-NYC",
        "ip_location_region": "CN",
        "device_status": "inactive",
        "device_verified": False,
        "sim_change_days": 0,
    }
}

@app.post("/risk-check", response_model=RiskResponse)
def check_risk(data: RiskRequest):
    user_data = mock_database.get(data.phone_number)

    if not user_data:
        return {
            "phone_number": data.phone_number,
            "device_location_region": "UNKNOWN",
            "ip_location_region": "UNKNOWN",
            "device_status": "inactive",
            "device_verified": False,
            "sim_swap_flag": False,
            "ip_risk_flag": True,
            "risk_score": 100,
            "risk_level": "HIGH"
        }

    # 交叉比對 Device Location 和 IP Location
    location_match = (user_data["device_location_region"][:2] == user_data["ip_location_region"])

    # 計算 flags
    sim_swap_flag = user_data["sim_change_days"] <= 7
    ip_risk_flag = not location_match

    # 計算風險分數
    score = 0
    score += 30 if sim_swap_flag else 0
    score += 30 if ip_risk_flag else 0
    score += 20 if user_data["device_status"] != "active" else 0
    score += (0 if user_data["device_verified"] else 20)

    # 決定 risk level
    if score >= 80:
        risk_level = "HIGH"
    elif score >= 50:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return RiskResponse(
        phone_number=data.phone_number,
        device_location_region=user_data["device_location_region"],
        ip_location_region=user_data["ip_location_region"],
        device_status=user_data["device_status"],
        device_verified=user_data["device_verified"],
        sim_swap_flag=sim_swap_flag,
        ip_risk_flag=ip_risk_flag,
        risk_score=score,
        risk_level=risk_level
    )


