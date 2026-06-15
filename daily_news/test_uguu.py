import requests

file_path = "/Users/seongjegeun/.gemini/antigravity/brain/922b32bd-5347-48ac-ae56-f12e7319518b/2026-06-08_card_01.png"

print("Uploading to uguu.se...")
try:
    with open(file_path, "rb") as f:
        res = requests.post(
            "https://uguu.se/upload.php",
            files={"files[]": f},
            timeout=10
        )
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Failed: {e}")
