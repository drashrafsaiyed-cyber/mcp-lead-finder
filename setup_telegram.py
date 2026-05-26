"""
Run this ONCE to get your Telegram Chat ID automatically.
Usage: python setup_telegram.py
"""
import sys
import requests
from pathlib import Path

print("=" * 50)
print("  Telegram Setup Helper")
print("=" * 50)
print()

token = input("Paste your Telegram Bot Token here: ").strip()
if not token:
    print("❌ No token entered.")
    sys.exit(1)

print("\n👉 Now open Telegram and send ANY message to your bot (e.g. 'hello')")
input("Press Enter when done...")

# fetch updates to get chat ID
url = f"https://api.telegram.org/bot{token}/getUpdates"
try:
    resp = requests.get(url, timeout=10)
    data = resp.json()
    updates = data.get("result", [])
    if not updates:
        print("\n❌ No messages found. Make sure you sent a message to your bot first.")
        sys.exit(1)

    chat_id = str(updates[-1]["message"]["chat"]["id"])
    first_name = updates[-1]["message"]["chat"].get("first_name", "")
    print(f"\n✅ Found your Chat ID: {chat_id} (Hi {first_name}!)")

    # write to .env
    env_path = Path(__file__).parent / ".env"
    content = env_path.read_text()
    content = content.replace("your_bot_token_here", token)
    content = content.replace("your_chat_id_here", chat_id)
    env_path.write_text(content)

    print(f"✅ Saved to .env file automatically!")
    print()
    print("🚀 Test notification sending now...")

    test_msg = (
        "✅ <b>MCP Lead Finder connected!</b>\n\n"
        "You will receive lead alerts here whenever high-relevance "
        "MCP/AI integration jobs are found.\n\n"
        "🔥 = Score 10+ (Very relevant)\n"
        "⭐ = Score 5+ (Relevant)"
    )
    resp2 = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": test_msg, "parse_mode": "HTML"},
        timeout=10
    )
    if resp2.ok:
        print("✅ Test message sent to Telegram! Check your phone.")
    else:
        print(f"❌ Send failed: {resp2.text}")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
