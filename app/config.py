import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
AUTHORIZED_USER_IDS = os.getenv("AUTHORIZED_USER_IDS", "")
GATEWAY_CONTAINER = "ib-gateway"
LOG_LINES = 30

# Parse authorized user IDs
if AUTHORIZED_USER_IDS:
    AUTHORIZED_USER_IDS_SET = set(int(uid.strip()) for uid in AUTHORIZED_USER_IDS.split(",") if uid.strip())
else:
    AUTHORIZED_USER_IDS_SET = set()
