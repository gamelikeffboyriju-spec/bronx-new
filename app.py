from flask import Flask, request, jsonify
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
import asyncio
import os
from datetime import datetime
import pytz

app = Flask(__name__)

# ============================================
# CONFIGURATION
# ============================================
API_ID = int(os.environ.get('API_ID', '31968824'))
API_HASH = os.environ.get('API_HASH', 'd9847a6694b961248f4052d16b89b912')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_account_age(timestamp):
    if not timestamp:
        return None
    created = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    delta = now - created
    return {
        "created_date": created.strftime("%Y-%m-%d %H:%M:%S"),
        "days": delta.days,
        "months": round(delta.days / 30, 1),
        "years": round(delta.days / 365, 2)
    }

def get_india_time():
    india = pytz.timezone('Asia/Kolkata')
    now = datetime.now(india)
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day": now.strftime("%A"),
        "timezone": "Asia/Kolkata"
    }

# ============================================
# ROUTES
# ============================================
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BRONX ULTRA API</title>
        <style>
            body { background: #000; color: #0ff; font-family: monospace; text-align: center; padding: 50px; }
            code { background: #111; padding: 10px; color: #fa0; border-radius: 5px; }
            .info { color: #888; margin-top: 30px; }
        </style>
    </head>
    <body>
        <h1>👑 BRONX ULTRA API</h1>
        <p>Telegram OSINT - 15+ Features in One Request</p>
        <code>GET /chatid?username=USERNAME</code>
        <p class="info">@BRONX_ULTRA | v3.0.0</p>
    </body>
    </html>
    """

@app.route('/chatid')
def chatid():
    username = request.args.get('username', '').strip()
    
    if not username:
        return jsonify({
            "status": "error",
            "message": "Missing username parameter",
            "credit": "@BRONX_ULTRA"
        }), 400
    
    async def get_full_info():
        await client.connect()
        clean = username.replace("@", "")
        entity = await client.get_entity(f"@{clean}")
        
        # Base result
        result = {
            "status": "success",
            "credit": "@BRONX_ULTRA",
            "developer": "@BRONX_ULTRA"
        }
        
        # ============================================
        # FEATURE 1: Name
        # ============================================
        if hasattr(entity, 'first_name'):
            result["first_name"] = entity.first_name or ""
        if hasattr(entity, 'last_name'):
            result["last_name"] = entity.last_name or ""
        if hasattr(entity, 'title'):
            result["title"] = entity.title or ""
            result["first_name"] = entity.title or ""
        
        # ============================================
        # FEATURE 2: Chat ID
        # ============================================
        result["chat_id"] = entity.id
        
        # ============================================
        # FEATURE 3: Username
        # ============================================
        result["username"] = getattr(entity, 'username', clean)
        
        # ============================================
        # FEATURE 4: Type (User/Channel/Group/Bot)
        # ============================================
        if hasattr(entity, 'broadcast') and entity.broadcast:
            result["type"] = "channel"
        elif hasattr(entity, 'megagroup') and entity.megagroup:
            result["type"] = "supergroup"
        elif hasattr(entity, 'title'):
            result["type"] = "group"
        elif hasattr(entity, 'bot') and entity.bot:
            result["type"] = "bot"
        else:
            result["type"] = "user"
        
        # ============================================
        # FEATURE 5: Phone (if visible)
        # ============================================
        result["phone"] = getattr(entity, 'phone', None)
        
        # ============================================
        # FEATURE 6: Bio / About
        # ============================================
        try:
            if result["type"] == "user":
                full = await client(functions.users.GetFullUserRequest(entity))
                result["bio"] = full.full_user.about or ""
            elif result["type"] in ["channel", "supergroup"]:
                full = await client(functions.channels.GetFullChannelRequest(entity))
                result["bio"] = full.full_chat.about or ""
            else:
                result["bio"] = None
        except:
            result["bio"] = None
        
        # ============================================
        # FEATURE 7: Premium Status
        # ============================================
        result["is_premium"] = getattr(entity, 'premium', False)
        
        # ============================================
        # FEATURE 8: Verified Status
        # ============================================
        result["is_verified"] = getattr(entity, 'verified', False)
        
        # ============================================
        # FEATURE 9: Scam / Fake Flags
        # ============================================
        result["is_scam"] = getattr(entity, 'scam', False)
        result["is_fake"] = getattr(entity, 'fake', False)
        
        # ============================================
        # FEATURE 10: Account Creation Date & Age
        # ============================================
        if result["type"] == "user":
            try:
                full = await client(functions.users.GetFullUserRequest(entity))
                if hasattr(full.full_user, 'premium_since') and full.full_user.premium_since:
                    result["premium_since"] = full.full_user.premium_since.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
            
            # Approximate creation from ID
            import time
            creation_time = entity.id >> 32
            if creation_time > 0:
                result["account_age"] = get_account_age(creation_time)
            else:
                result["account_age"] = None
        
        # ============================================
        # FEATURE 11: Today Date (India Time)
        # ============================================
        result["india_time"] = get_india_time()
        
        # ============================================
        # FEATURE 12: Profile Photo
        # ============================================
        try:
            if result["type"] == "user":
                full = await client(functions.users.GetFullUserRequest(entity))
                result["has_profile_photo"] = full.full_user.profile_photo is not None
            else:
                result["has_profile_photo"] = getattr(entity, 'photo', None) is not None
        except:
            result["has_profile_photo"] = False
        
        # ============================================
        # FEATURE 13: Common Chats Count
        # ============================================
        try:
            if result["type"] == "user":
                full = await client(functions.users.GetFullUserRequest(entity))
                result["common_chats_count"] = full.full_user.common_chats_count
            else:
                result["common_chats_count"] = 0
        except:
            result["common_chats_count"] = 0
        
        # ============================================
        # FEATURE 14: Restricted Status
        # ============================================
        result["is_restricted"] = getattr(entity, 'restricted', False)
        result["restriction_reason"] = list(getattr(entity, 'restriction_reason', []))
        
        # ============================================
        # FEATURE 15: Language Code
        # ============================================
        result["lang_code"] = getattr(entity, 'lang_code', None)
        
        # ============================================
        # FEATURE 16: Mutual Contact
        # ============================================
        result["is_mutual_contact"] = getattr(entity, 'mutual_contact', False)
        
        # ============================================
        # FEATURE 17: Participants Count (Channel)
        # ============================================
        if result["type"] in ["channel", "supergroup", "group"]:
            result["participants_count"] = getattr(entity, 'participants_count', None)
        
        return result
    
    try:
        result = loop.run_until_complete(get_full_info())
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "credit": "@BRONX_ULTRA"
        }), 404

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "india_time": get_india_time(),
        "credit": "@BRONX_ULTRA"
    })

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
