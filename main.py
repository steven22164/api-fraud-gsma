# === Finalized FastAPI following GSMA Open Gateway structure ===
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# 模擬資料庫
mock_db = {
    "0912345678": {
        "device_location_region": "TW-TPE",
        "ip_location_region": "TW-TPE",
        "device_status": "active",
        "sim_change_days": 5,
        "device_trust_score": 85
    },
    "0922333444": {
        "device_location_region": "TW-KHH",
        "ip_location_region": "VN-HCM",
        "device_status": "suspended",
        "sim_change_days": 2,
        "device_trust_score": 60
    }
}

class RiskRequest(BaseModel):
    phone_number: str = Field(..., example="0912345678")

class RiskResponse(BaseModel):
    phone_number: str
    device_location_region: str
    ip_location_region: str
    device_status: str
    sim_change_days: int
    device_verified: bool
    sim_swap_flag: bool
    ip_risk_flag: bool
    risk_score: int
    risk_level: str

@app.post("/risk-check", response_model=RiskResponse)
def check_risk(data: RiskRequest):
    record = mock_db.get(data.phone_number)
    if not record:
        raise HTTPException(status_code=404, detail="Phone number not found in database")

    device_location_region = record["device_location_region"]
    ip_location_region = record["ip_location_region"]
    device_status = record["device_status"]
    sim_change_days = record["sim_change_days"]
    device_trust_score = record["device_trust_score"]

    # 驗證與比對
    location_match = device_location_region[:2] == ip_location_region[:2]
    ip_risk_flag = not location_match
    device_verified = device_status == "active"
    sim_swap_flag = sim_change_days <= 7

    # 風險分數計算
    score = 0
    if not location_match:
        score += 30
    if not device_verified:
        score += 30
    if sim_swap_flag:
        score += 30
    score += (100 - device_trust_score) * 0.1

    if score >= 80:
        risk_level = "極高風險"
    elif score >= 50:
        risk_level = "中風險"
    else:
        risk_level = "低風險"

    return RiskResponse(
        phone_number=data.phone_number,
        device_location_region=device_location_region,
        ip_location_region=ip_location_region,
        device_status=device_status,
        sim_change_days=sim_change_days,
        device_verified=device_verified,
        sim_swap_flag=sim_swap_flag,
        ip_risk_flag=ip_risk_flag,
        risk_score=int(score),
        risk_level=risk_level
    )
