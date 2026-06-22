import os
import secrets

BOT_TOKEN = "8903142933:AAEHtd2rd8eTEk5ULzaIgOAwoZ34MbC3ftg"
MAIN_ADMIN_ID =  8766579960
DB_PATH = os.path.join(os.path.dirname(__file__), "debts_kaa.db")
SECRET_KEY = secrets.token_hex(24)

# 1. Сиздин ngrok адресиңиз (пробелсиз!)
NGROK_URL = "https://cruncher-impound-paralyze.ngrok-free.dev"

# 2. Web App URL (кейбод ушын)
WEB_APP_URL = NGROK_URL

# 3. Webhook URL (дұрыс форматта)
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{NGROK_URL}{WEBHOOK_PATH}"
