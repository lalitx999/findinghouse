import os
import logging
import requests

logger = logging.getLogger(__name__)

def send_sms_otp(phone: str, otp_code: str) -> tuple[bool, str]:
    """
    Send SMS OTP using SMSMKT API service.
    
    Environment variables required in .env:
    - SMSMKT_API_KEY
    - SMSMKT_SECRET_KEY
    - SMSMKT_SENDER_NAME (Optional, default: 'SMSMKT' or your approved Sender Name)
    """
    api_key = os.getenv('SMSMKT_API_KEY', '').strip()
    secret_key = os.getenv('SMSMKT_SECRET_KEY', '').strip()
    sender_name = os.getenv('SMSMKT_SENDER_NAME', 'SMSMKT').strip()

    # Format phone number to clean Thai phone format (e.g. 0812345678)
    clean_phone = phone.replace('-', '').replace(' ', '').strip()
    if clean_phone.startswith('+66'):
        clean_phone = '0' + clean_phone[3:]

    message = f"[FINDINGHOUSE] รหัส OTP ของคุณคือ {otp_code} (มีอายุ 5 นาที)"

    # If API keys are missing, run in Sandbox / Development Fallback Mode
    if not api_key or not secret_key:
        logger.warning(f"[SMSMKT Sandbox] SMSMKT_API_KEY or SMSMKT_SECRET_KEY not found in .env. Dummy OTP sent to {clean_phone}: {otp_code}")
        return True, f"Sandbox Mode: OTPคือ {otp_code}"

    # Call SMSMKT REST API
    url = "https://api.smsmkt.com/sms/send"
    headers = {
        "api_key": api_key,
        "secret_key": secret_key,
        "Content-Type": "application/json"
    }
    payload = {
        "sender": sender_name,
        "to": clean_phone,
        "message": message
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res_data = response.json()

        # SMSMKT Success response check (code "000" or status True)
        if response.status_code == 200 and (res_data.get('code') in ['000', 0, '0'] or res_data.get('status') is True):
            logger.info(f"[SMSMKT Success] Sent OTP to {clean_phone}")
            return True, "ส่งรหัส OTP สำเร็จ"
        else:
            error_msg = res_data.get('detail') or res_data.get('message') or str(res_data)
            logger.error(f"[SMSMKT Error] Failed to send SMS: {error_msg}")
            return False, f"ส่ง SMS ล้มเหลว: {error_msg}"
            
    except Exception as e:
        logger.exception(f"[SMSMKT Exception] Error connecting to SMSMKT API: {e}")
        return False, f"เกิดข้อผิดพลาดในการเชื่อมต่อ SMSMKT: {str(e)}"
