import os

TG_SECRET=os.getenv("TG_SECRET")
TG_HOST=os.getenv("TG_HOST")
TG_BOT_URL = f'{TG_HOST}/{TG_SECRET}'
