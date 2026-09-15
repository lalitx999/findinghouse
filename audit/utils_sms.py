import os
import logging
import requests

logger = logging.getLogger(__name__)

def send_sms_otp(phone: str) -> tuple[bool, str, str]:
    api_key = os.getenv('SMSMKT_API_KEY', '').strip()
    secret_key = os.getenv('SMSMKT_SECRET_KEY', '').strip()
    project_key = os.getenv('SMSMKT_PROJECT_KEY', '').strip()

    clean_phone = phone.replace('-', '').replace(' ', '').strip()
    if clean_phone.startswith('+66'):
        clean_phone = '0' + clean_phone[3:]

    if not api_key or not secret_key or not project_key:
        return False, "SMS Gateway credentials missing", ""

    url = "https://portal-otp.smsmkt.com/api/otp-send"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "api_key": api_key,
        "secret_key": secret_key,
    }
    payload = {
        "project_key": project_key,
        "phone": clean_phone
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res_data = response.json()
        code = str(res_data.get('code', ''))

        if response.status_code == 200 and code in ['000', '0']:
            token = res_data.get('result', {}).get('token', '')
            logger.info(f"[SMSMKT Real] Sent to {clean_phone}, Token: {token}")
            return True, "Success", token
        else:
            err = res_data.get('detail') or res_data.get('message') or str(res_data)
            logger.error(f"[SMSMKT Error] {err}")
            return False, err, ""
    except Exception as e:
        logger.exception(f"[SMSMKT Exception] {e}")
        return False, str(e), ""

def verify_sms_otp_gateway(token: str, otp_code: str) -> tuple[bool, str]:
    api_key = os.getenv('SMSMKT_API_KEY', '').strip()
    secret_key = os.getenv('SMSMKT_SECRET_KEY', '').strip()

    url = "https://portal-otp.smsmkt.com/api/otp-validate"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "api_key": api_key,
        "secret_key": secret_key,
    }
    payload = {
        "token": token,
        "otp_code": otp_code.strip()
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res_data = response.json()
        code = str(res_data.get('code', ''))

        if response.status_code == 200 and code in ['000', '0']:
            return True, "ยืนยันสำเร็จ"
        else:
            msg = res_data.get('detail') or res_data.get('message') or "รหัส OTP ไม่ถูกต้อง"
            return False, msg
    except Exception as e:
        return False, f"เชื่อมต่อล้มเหลว: {e}"
