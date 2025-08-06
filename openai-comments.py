from instagrapi import Client
import os
import random
import sys
import time
import json
from pathlib import Path
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

def get_user_agents():
    """Rotate user agents for better stealth - Updated to latest 2024/2025 versions"""
    user_agents = [
        "Instagram 387.1.0.34.85 Android",
        "Instagram 385.0.0.47.74 Android", 
        "Instagram 384.0.0.46.83 Android",
        "Instagram 383.1.0.48.78 Android",
        "Instagram 382.0.0.49.84 Android"
    ]
    return random.choice(user_agents)

def get_device_settings():
    """Generate random device settings for better stealth - Updated to current devices"""
    devices = [
        {
            "manufacturer": "samsung",
            "model": "SM-S918B",  # Galaxy S23 Ultra
            "android_version": 34,
            "android_release": "14"
        },
        {
            "manufacturer": "xiaomi", 
            "model": "2312DRA50G",  # Redmi Note 13 Pro 5G
            "android_version": 34,
            "android_release": "14"
        },
        {
            "manufacturer": "realme",
            "model": "RMX3842",  # Realme device
            "android_version": 35,
            "android_release": "15"
        },
        {
            "manufacturer": "oppo",
            "model": "CPH2665",
            "android_version": 35,
            "android_release": "15"
        },
        {
            "manufacturer": "vivo",
            "model": "V2420",
            "android_version": 34,
            "android_release": "14"
        }
    ]
    return random.choice(devices)

def load_session(username):
    """Load existing session if available"""
    session_file = f"session_{username}.json"
    if os.path.exists(session_file):
        try:
            print(f"📁 Loading existing session for {username}")
            return session_file
        except Exception as e:
            print(f"⚠️ Failed to load session: {e}")
    return None

def save_session(cl, username):
    """Save session for future use"""
    try:
        session_file = f"session_{username}.json"
        cl.dump_settings(session_file)
        print(f"💾 Session saved for {username}")
    except Exception as e:
        print(f"⚠️ Failed to save session: {e}")

def safe_delay(min_seconds=2, max_seconds=8):
    """Add random delay between actions"""
    delay = random.uniform(min_seconds, max_seconds)
    print(f"⏳ Waiting {delay:.1f} seconds...")
    time.sleep(delay)

def check_rate_limits():
    """Simple rate limiting check"""
    rate_file = "rate_limits.json"
    current_time = time.time()
    
    # Load existing limits
    limits = {"likes": [], "comments": []}
    if os.path.exists(rate_file):
        try:
            with open(rate_file, 'r') as f:
                limits = json.load(f)
        except:
            pass
    
    # Clean old entries (older than 1 hour)
    hour_ago = current_time - 3600
    limits["likes"] = [t for t in limits["likes"] if t > hour_ago]
    limits["comments"] = [t for t in limits["comments"] if t > hour_ago]
    
    # Check limits (more conservative for comments)
    if len(limits["comments"]) >= 15:  # Reduced from 20 to 15 comments per hour
        print("⚠️ Rate limit reached for comments (15/hour)")
        return False
    
    return True

def update_rate_limits(action_type):
    """Update rate limit tracking"""
    rate_file = "rate_limits.json"
    current_time = time.time()
    
    # Load existing limits
    limits = {"likes": [], "comments": []}
    if os.path.exists(rate_file):
        try:
            with open(rate_file, 'r') as f:
                limits = json.load(f)
        except:
            pass
    
    # Add current action
    if action_type in limits:
        limits[action_type].append(current_time)
    
    # Save limits
    try:
        with open(rate_file, 'w') as f:
            json.dump(limits, f)
    except Exception as e:
        print(f"⚠️ Failed to update rate limits: {e}")

# Check rate limits before starting
if not check_rate_limits():
    print("❌ Rate limit exceeded. Please wait before trying again.")
    sys.exit(1)

# Initialize client with best practices
cl = Client()

# Set device settings for better stealth
device = get_device_settings()
cl.set_device(device)

# Set user agent
cl.set_user_agent(get_user_agents())

# Set proxy and login with session management
proxies = get_proxies()
login_success = False

# Try to load existing session first
session_file = load_session(USERNAME)
if session_file:
    try:
        cl.load_settings(session_file)
        cl.login(USERNAME, PASSWORD)
        print("✅ Login successful with existing session!")
        login_success = True
    except Exception as e:
        print(f"⚠️ Session login failed: {e}")
        print("🔄 Attempting fresh login...")

# If session login failed, try fresh login with proxies
if not login_success:
    for proxy in proxies:
        try:
            cl.set_proxy(proxy)
            print(f'🌐 Trying HTTP proxy: {proxy}')
            safe_delay(1, 3)  # Delay before login attempt
            cl.login(USERNAME, PASSWORD)
            print("✅ Login successful!")
            save_session(cl, USERNAME)
            login_success = True
            break
        except Exception as e:
            print(f"❌ Login failed with proxy {proxy}: {e}")
            safe_delay(2, 5)  # Delay before next proxy

if not login_success:
    print("❌ Login failed with all proxies.")
    sys.exit(1)

def generate_comment_with_chatgpt(post_content, hashtag):
    try:
        # More human-like prompt with natural variations
        prompts = [
            f"""You are a real person commenting on Instagram. Write a natural, casual comment for this food post.

Post: {post_content}
Hashtag: #{hashtag}

Write like a real person would comment - casual, friendly, maybe with a small typo or informal language. Keep it under 120 characters. Don't be overly enthusiastic or promotional. Just be natural.

Comment:""",
            
            f"""Comment on this Instagram food post as a regular person:

Post: {post_content}
Hashtag: #{hashtag}

Write a casual, human comment. Maybe mention something specific about the food, or just say you like it. Keep it short and natural. No excessive emojis.

Comment:""",
            
            f"""You're commenting on a food Instagram post. Be natural and casual:

Post: {post_content}
Hashtag: #{hashtag}

Write like you're talking to a friend. Maybe ask a question or just say you like it. Keep it conversational and under 120 characters.

Comment:"""
        ]
        
        prompt = random.choice(prompts)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a real person commenting on Instagram food posts. Write natural, casual comments like a human would. Don't be overly enthusiastic or promotional."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=80,
            temperature=0.8  # Higher temperature for more variation
        )
        
        comment = response.choices[0].message.content.strip()
        
        # Sometimes add small human touches
        if random.random() < 0.3:  # 30% chance
            human_touches = [
                lambda x: x.replace("!", "! "),
                lambda x: x + " 😊" if "😊" not in x else x,
                lambda x: x.replace("amazing", "nice"),
                lambda x: x.replace("delicious", "good"),
                lambda x: x + " looks good",
                lambda x: x.replace("love", "like"),
            ]
            comment = random.choice(human_touches)(comment)
        
        return comment
    except Exception as e:
        print(f"⚠️  ChatGPT API error: {e}")
        # More natural fallback comments
        fallbacks = [
            f"nice #{hashtag}",
            f"looks good",
            f"yum",
            f"delicious",
            f"love this",
            f"looks tasty",
            f"yummy",
            f"nice post",
            f"looks great",
            f"good stuff"
        ]
        return random.choice(fallbacks)

# Require hashtag for comments
if not hashtag:
    print("Hashtag is required for hashtag-only search.")
    sys.exit(1)

# Add delay before API calls
safe_delay(3, 7)

# Fetch medias with retries
max_retries = 3
for attempt in range(max_retries):
    try:
        print(f"📥 Fetching posts (attempt {attempt + 1}/{max_retries})")
        medias = cl.hashtag_medias_recent(hashtag, amount=30)
        break
    except Exception as e:
        print(f"Error fetching medias (attempt {attempt + 1}): {e}")
        if attempt < max_retries - 1:
            safe_delay(10, 20)  # Longer delay on error
        else:
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
        safe_delay(2, 5)  # Delay between API calls
        comments = cl.media_comments(media.id)
        already_commented = any(comment.user.username == USERNAME for comment in comments)
        if not already_commented:
            posts_to_comment.append(media)
        else:
            print(f"Skipping post {media.code} - already commented")
    except Exception as e:
        print(f"Could not check comments for post {media.code}: {e}")
        posts_to_comment.append(media)
        safe_delay(5, 10)  # Longer delay on error

if not posts_to_comment:
    print("No posts found that you haven't already commented on.")
    sys.exit(0)

print(f"Found {len(posts_to_comment)} posts you haven't commented on")

# Limit to max 2 comments for safety (more conservative than likes)
# Reduce by 20% - now 1-2 comments with 20% chance to skip entirely
if random.random() < 0.2:  # 20% chance to skip commenting entirely
    print("🎲 Randomly skipping comment generation (20% reduction)")
    sys.exit(0)

num_to_comment = min(random.randint(1, 2), len(posts_to_comment))  # 1-2 comments instead of always 2
selected_medias = random.sample(posts_to_comment, num_to_comment)

success_count = 0
for i, media in enumerate(selected_medias, 1):
    try:
        safe_delay(10, 20)  # Longer delay between comments (10-20 seconds)
        
        post_content = ""
        if media.caption_text:
            post_content = media.caption_text
        else:
            post_content = f"Post about #{hashtag}"
        
        comment = generate_comment_with_chatgpt(post_content, hashtag)
        
        # Sometimes add human-like typos or casual language
        if random.random() < 0.15:  # 15% chance for human touches
            human_modifications = [
                lambda x: x.replace("looks", "looks like"),
                lambda x: x.replace("amazing", "amaz"),
                lambda x: x.replace("delicious", "delish"),
                lambda x: x + " tbh",
                lambda x: x.replace("!", "!!"),
                lambda x: x.replace("love", "luv"),
                lambda x: x.replace("really", "rly"),
                lambda x: x.replace("you", "u"),
                lambda x: x.replace("are", "r"),
                lambda x: x + " tho",
                lambda x: x.replace("good", "gd"),
                lambda x: x.replace("great", "gr8"),
            ]
            comment = random.choice(human_modifications)(comment)
        
        # Additional delay before posting comment (more human-like)
        safe_delay(5, 12)  # Slightly longer delay to seem more human
        
        cl.media_comment(media.id, comment)
        print(f"💬 Commented on post {i}: https://www.instagram.com/p/{media.code}/")
        print(f"   Post content: {post_content[:100]}{'...' if len(post_content) > 100 else ''}")
        print(f"   AI Comment: {comment}")
        print("-" * 50)
        
        # Update rate limits
        update_rate_limits("comments")
        success_count += 1
        
        # Additional delay after successful comment (more human-like)
        safe_delay(8, 18)  # Longer delay to seem more natural
        
    except Exception as e:
        print(f"⚠️ Failed to comment on post {i}: {e}")
        safe_delay(15, 30)  # Much longer delay on comment error

print(f"✅ Successfully commented on {success_count}/{len(selected_medias)} posts")

# Final delay before exit
safe_delay(2, 5) 