import os
import requests
from dotenv import load_dotenv

load_dotenv()

urls = {
    "catbox": "https://catbox.moe/user/api.php",
    "telegram": f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/getMe",
    "facebook": "https://graph.facebook.com/v19.0/me",
    "threads": "https://graph.threads.net/v1.0/me"
}

print("Testing connections with 5s timeout...")
for name, url in urls.items():
    try:
        print(f"Connecting to {name} ({url})...")
        if name == "catbox":
            # Catbox is a POST, but a simple GET might return 200 or 400 immediately
            r = requests.get(url, timeout=5)
        elif name == "facebook":
            r = requests.get(url, params={"access_token": os.getenv("INSTAGRAM_ACCESS_TOKEN")}, timeout=5)
        elif name == "threads":
            r = requests.get(url, params={"access_token": os.getenv("THREADS_ACCESS_TOKEN")}, timeout=5)
        else:
            r = requests.get(url, timeout=5)
        print(f"  → Status: {r.status_code}, Response length: {len(r.text)}")
    except Exception as e:
        print(f"  → Failed: {e}")
