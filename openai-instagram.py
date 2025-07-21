from instagrapi import Client
import os
import random
import sys
from dotenv import load_dotenv

# Accept hashtag as optional argument
if len(sys.argv) < 3:
    print("Usage: python3 openai-instagram.py <username> <password> [<hashtag>]")
    sys.exit(1)

USERNAME = sys.argv[1]
PASSWORD = sys.argv[2]
hashtag = sys.argv[3] if len(sys.argv) > 3 else None

print(f"📸 Using credentials for: {USERNAME}")
print(f"🔍 Searching posts for #{hashtag}...")

def get_proxies():
    proxies = []
    try:
        with open('proxies.txt', 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
    except Exception:
        pass
    if not proxies:
        proxies = [os.getenv('TINYPROXY_HTTP', 'http://127.0.0.1:8888')]
    return proxies

cl = Client()
proxies = get_proxies()
login_success = False
for proxy in proxies:
    try:
        cl.set_proxy(proxy)
        print(f'🌐 Trying HTTP proxy: {proxy}')
        cl.login(USERNAME, PASSWORD)
        print("✅ Login successful!")
        login_success = True
        break
    except Exception as e:
        print(f"❌ Login failed with proxy {proxy}: {e}")

if not login_success:
    print("❌ Login failed with all proxies.")
    sys.exit(1)

# Require hashtag again
if not hashtag:
    print("Hashtag is required for hashtag-only search.")
    sys.exit(1)

# Fetch recent medias by hashtag
try:
    medias = cl.hashtag_medias_recent(hashtag, amount=30)
except Exception as e:
    print(f"Error fetching medias: {e}")
    medias = []

filtered_medias = []
for m in medias:
    try:
        _ = m.pk
        filtered_medias.append(m)
    except Exception as e:
        print(f"Skipping invalid media: {e}")

if not filtered_medias:
    print(f"No posts found for #{hashtag}.")
    sys.exit(0)

print(f"Found {len(filtered_medias)} posts for #{hashtag}, randomly selecting 3 to like...")

selected_medias = random.sample(filtered_medias, min(3, len(filtered_medias)))

for i, media in enumerate(selected_medias, 1):
    try:
        cl.media_like(media.id)
        print(f"❤️ Liked post {i}: https://www.instagram.com/p/{media.code}/")
    except Exception as e:
        print(f"⚠️ Failed to like post {i}: {e}")
