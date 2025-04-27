
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict
from mock_database import mock_database

app = FastAPI()

class PhoneNumberRequest(BaseModel):
    phone_number: str = Field(..., example="0912345001")

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

@app.post("/risk-check", response_model=RiskResponse)
def risk_check(data: PhoneNumberRequest):
    record = mock_database.get(data.phone_number)
    if not record:
        raise HTTPException(status_code=404, detail="Phone number not found in database")
    
    sim_swap_flag = record["sim_change_days"] <= 7
    ip_risk_flag = record["device_location_region"][:2] != record["ip_location_region"][:2]
    device_verified = record["device_status"] == "active"
    
    score = 0
    if not device_verified:
        score += 40
    if sim_swap_flag:
        score += 30
    if ip_risk_flag:
        score += 30
    
    if score >= 80:
        level = "HIGH"
    elif score >= 50:
        level = "MEDIUM"
    else:
        level = "LOW"

    return RiskResponse(
        phone_number=data.phone_number,
        device_location_region=record["device_location_region"],
        ip_location_region=record["ip_location_region"],
        device_status=record["device_status"],
        device_verified=device_verified,
        sim_swap_flag=sim_swap_flag,
        ip_risk_flag=ip_risk_flag,
        risk_score=score,
        risk_level=level
    )
