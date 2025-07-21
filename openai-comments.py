from instagrapi import Client
import os
import random
import sys
from openai import OpenAI
from dotenv import load_dotenv

if len(sys.argv) < 4:
    print("Usage: python3 openai-comments.py <username> <password> <hashtag>")
    sys.exit(1)

USERNAME = sys.argv[1]
PASSWORD = sys.argv[2]
hashtag = sys.argv[3]

load_dotenv('config.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
    print("❌ Error: Please set OPENAI_API_KEY in config.env")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

print(f"📸 Using credentials for: {USERNAME}")

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

def generate_comment_with_chatgpt(post_content, hashtag):
    try:
        prompt = f"""
You are the social media manager for a restaurant. Generate a short, engaging comment (max 140 characters) for this Instagram post.

Post content: {post_content}
Hashtag: #{hashtag}

Requirements:
- Act as a restaurant's social media manager
- Be friendly and professional
- Show appreciation for food/cooking content
- Reference the hashtag naturally
- Keep it under 140 characters, be succint
- Add 1-2 relevant emojis ONLY if you find it necessary
- Sound natural and human-like
- Don't be overly promotional
- Focus on food appreciation and community engagement
- Avoid naming the restaurant in the comment
- In Italian

Comment:"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are the social media manager for a restaurant who engages with food and cooking content in a friendly, professional manner."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        comment = response.choices[0].message.content.strip()
        return comment
    except Exception as e:
        print(f"⚠️  ChatGPT API error: {e}")
        return f"Love this #{hashtag} content! 🍽️"

# Require hashtag for comments
if not hashtag:
    print("Hashtag is required for hashtag-only search.")
    sys.exit(1)

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

print(f"Found {len(filtered_medias)} posts for #{hashtag}, checking for posts you haven't commented on...")

posts_to_comment = []
for media in filtered_medias:
    try:
        comments = cl.media_comments(media.id)
        already_commented = any(comment.user.username == USERNAME for comment in comments)
        if not already_commented:
            posts_to_comment.append(media)
        else:
            print(f"Skipping post {media.code} - already commented")
    except Exception as e:
        print(f"Could not check comments for post {media.code}: {e}")
        posts_to_comment.append(media)

if not posts_to_comment:
    print("No posts found that you haven't already commented on.")
    sys.exit(0)

print(f"Found {len(posts_to_comment)} posts you haven't commented on")

num_to_comment = min(3, len(posts_to_comment))
selected_medias = random.sample(posts_to_comment, num_to_comment)

for i, media in enumerate(selected_medias, 1):
    try:
        post_content = ""
        if media.caption_text:
            post_content = media.caption_text
        else:
            post_content = f"Post about #{hashtag}"
        
        comment = generate_comment_with_chatgpt(post_content, hashtag)
        
        cl.media_comment(media.id, comment)
        print(f"💬 Commented on post {i}: https://www.instagram.com/p/{media.code}/")
        print(f"   Post content: {post_content[:100]}{'...' if len(post_content) > 100 else ''}")
        print(f"   AI Comment: {comment}")
        print("-" * 50)
        
    except Exception as e:
        print(f"⚠️ Failed to comment on post {i}: {e}") 