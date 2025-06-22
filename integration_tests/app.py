from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from signi_email_otp.auth import request_otp, verify_otp
# enable logging
import logging


# set up logging for the OTP module
otp_logger = logging.getLogger("signi_email_otp")
otp_logger.setLevel(logging.DEBUG)

app = FastAPI()


class OTPRequest(BaseModel):
    email: str


class OTPVerify(BaseModel):
    email: str
    otp: str


@app.post("/otp/request")
def otp_request(data: OTPRequest):
    logging.info(f"Requesting OTP for email: {data.email}")
    otp = request_otp(data.email)
    return {"otp": otp}


@app.post("/otp/verify")
def otp_verify(data: OTPVerify):
    try:
        result = verify_otp(data.email, data.otp)
        return {"refresh_token": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))