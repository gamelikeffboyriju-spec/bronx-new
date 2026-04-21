from flask import Flask, request, jsonify
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession
from telethon.tl.types import UserStatusOnline, UserStatusRecently, UserStatusOffline
import asyncio
import os
import json
from datetime import datetime

app = Flask(__name__)

# ============================================
# CONFIGURATION
# ============================================
API_ID = int(os.environ.get('API_ID', '31968824'))
API_HASH = os.environ.get('API_HASH', 'd9847a6694b961248f4052d16b89b912'))
SESSION_STRING = os.environ.get('SESSION_STRING', '')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)

# ============================================
# HELPER FUNCTIONS
# ============================================
def parse_user_status(status):
    if isinstance(status, UserStatusOnline):
        return {"status": "online", "expires": str(status.expires)}
    elif isinstance(status, UserStatusRecently):
        return {"status": "recently", "last_seen": "within last week"}
    elif isinstance(status, UserStatusOffline):
        return {"status": "offline", "was_online": str(status.was_online)}
    return {"status": "unknown"}

def format_photo(photo):
    if not photo:
        return None
    return {
        "photo_id": photo.photo_id,
        "dc_id": photo.dc_id,
        "has_video": photo.has_video,
        "is_personal": photo.personal,
        "sizes": [{"type": s.type, "location": str(s)} for s in photo.sizes]
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
        <title>BRONX ULTRA PRIME API</title>
        <meta charset="UTF-8">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                background: linear-gradient(135deg, #0a0a0a, #1a0033);
                color: #bf00ff; 
                font-family: 'Courier New', monospace; 
                padding: 30px;
                min-height: 100vh;
            }
            h1 { 
                text-align: center; 
                color: #bf00ff; 
                text-shadow: 0 0 20px #bf00ff;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .subtitle { text-align: center; color: #888; margin-bottom: 30px; }
            .endpoint-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                max-width: 1200px;
                margin: 0 auto;
            }
            .card {
                background: #111;
                border: 1px solid #333;
                border-radius: 15px;
                padding: 20px;
                transition: all 0.3s;
            }
            .card:hover {
                border-color: #bf00ff;
                box-shadow: 0 0 30px #bf00ff33;
                transform: translateY(-5px);
            }
            .card h3 { color: #bf00ff; margin-bottom: 15px; }
            .badge {
                display: inline-block;
                padding: 3px 10px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                margin-right: 5px;
            }
            .basic { background: #0066ff; color: white; }
            .vip { background: #ff6600; color: white; }
            .prime { background: #bf00ff; color: white; }
            .ultra { background: linear-gradient(135deg, #bf00ff, #ff0066); color: white; }
            code {
                display: block;
                background: #000;
                padding: 10px;
                border-radius: 8px;
                color: #00ff88;
                margin: 10px 0;
                font-size: 13px;
                word-break: break-all;
            }
            .feature-list {
                list-style: none;
                margin-top: 10px;
            }
            .feature-list li {
                color: #aaa;
                font-size: 12px;
                padding: 3px 0;
            }
            .feature-list li::before {
                content: "✓ ";
                color: #00ff88;
            }
            footer {
                text-align: center;
                margin-top: 50px;
                color: #555;
            }
        </style>
    </head>
    <body>
        <h1>👑 BRONX ULTRA PRIME API</h1>
        <p class="subtitle">Telegram OSINT • Maximum Information Extractor</p>
        
        <div class="endpoint-grid">
            <div class="card">
                <h3>
                    <span class="badge basic">BASIC</span>
                    /chatid
                </h3>
                <code>/chatid?username=USER</code>
                <ul class="feature-list">
                    <li>Chat ID</li>
                    <li>Username</li>
                    <li>Name</li>
                    <li>Type</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>
                    <span class="badge vip">VIP</span>
                    /vip
                </h3>
                <code>/vip?username=USER</code>
                <ul class="feature-list">
                    <li>All Basic Info</li>
                    <li>Phone (if visible)</li>
                    <li>Bio / About</li>
                    <li>Premium Status</li>
                    <li>Profile Photos</li>
                    <li>Common Chats</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>
                    <span class="badge prime">PRIME</span>
                    /prime
                </h3>
                <code>/prime?username=USER</code>
                <ul class="feature-list">
                    <li>All VIP Info</li>
                    <li>Last Seen Status</li>
                    <li>Online Status</li>
                    <li>Stories Count</li>
                    <li>Emoji Status</li>
                    <li>Wallpaper/Color</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>
                    <span class="badge ultra">ULTRA</span>
                    /ultra
                </h3>
                <code>/ultra?username=USER</code>
                <ul class="feature-list">
                    <li>All Prime Info</li>
                    <li>Full Profile Data</li>
                    <li>All Photos</li>
                    <li>Mutual Contacts</li>
                    <li>Common Groups List</li>
                    <li>Restriction Info</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>
                    <span class="badge ultra">CHANNEL</span>
                    /channel
                </h3>
                <code>/channel?username=CHANNEL</code>
                <ul class="feature-list">
                    <li>Channel ID & Title</li>
                    <li>Subscribers Count</li>
                    <li>Description</li>
                    <li>Linked Chat</li>
                    <li>Invite Link</li>
                    <li>Admins Count</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>
                    <span class="badge prime">SEARCH</span>
                    /search
                </h3>
                <code>/search?query=NAME</code>
                <ul class="feature-list">
                    <li>Global Search</li>
                    <li>Find Users</li>
                    <li>Find Channels</li>
                    <li>Find Groups</li>
                </ul>
            </div>
        </div>
        
        <footer>
            🔒 @BRONX_ULTRA | ULTRA PRIME OSINT | v2.0.0
        </footer>
    </body>
    </html>
    """

@app.route('/chatid')
def chatid():
    username = request.args.get('username', '').strip()
    if not username: return jsonify({"error": "Missing username"}), 400
    
    async def get():
        await client.connect()
        e = await client.get_entity(username.replace("@", ""))
        return {
            "status": "success",
            "chat_id": e.id,
            "username": getattr(e, 'username', username),
            "type": "channel" if hasattr(e, 'broadcast') else "user",
            "name": getattr(e, 'first_name', getattr(e, 'title', '')),
            "credit": "@BRONX_ULTRA"
        }
    return jsonify(loop.run_until_complete(get()))

@app.route('/vip')
def vip():
    username = request.args.get('username', '').strip()
    if not username: return jsonify({"error": "Missing username"}), 400
    
    async def get():
        await client.connect()
        clean = username.replace("@", "")
        e = await client.get_entity(f"@{clean}")
        
        result = {
            "status": "success",
            "chat_id": e.id,
            "username": getattr(e, 'username', clean),
            "credit": "@BRONX_ULTRA"
        }
        
        if hasattr(e, 'broadcast') and e.broadcast:
            result["type"] = "channel"
            result["title"] = e.title
            result["participants_count"] = getattr(e, 'participants_count', None)
            result["verified"] = e.verified
            result["scam"] = e.scam
            result["fake"] = e.fake
            
            try:
                full = await client(functions.channels.GetFullChannelRequest(e))
                result["about"] = full.full_chat.about
                result["linked_chat_id"] = full.full_chat.linked_chat_id
                result["invite_link"] = full.full_chat.exported_invite.link if full.full_chat.exported_invite else None
            except:
                pass
        else:
            result["type"] = "user"
            result["first_name"] = e.first_name
            result["last_name"] = e.last_name
            result["phone"] = e.phone
            result["premium"] = e.premium
            result["verified"] = e.verified
            result["scam"] = e.scam
            result["fake"] = e.fake
            
            try:
                full = await client(functions.users.GetFullUserRequest(e))
                result["bio"] = full.full_user.about
                result["common_chats"] = full.full_user.common_chats_count
                result["profile_photo"] = format_photo(full.full_user.profile_photo)
            except:
                pass
        
        return result
    return jsonify(loop.run_until_complete(get()))

@app.route('/prime')
def prime():
    username = request.args.get('username', '').strip()
    if not username: return jsonify({"error": "Missing username"}), 400
    
    async def get():
        await client.connect()
        clean = username.replace("@", "")
        e = await client.get_entity(f"@{clean}")
        
        result = {
            "status": "success",
            "chat_id": e.id,
            "username": getattr(e, 'username', clean),
            "credit": "@BRONX_ULTRA"
        }
        
        if not hasattr(e, 'broadcast'):
            result["type"] = "user"
            result["first_name"] = e.first_name
            result["last_name"] = e.last_name
            result["phone"] = e.phone
            result["premium"] = e.premium
            result["verified"] = e.verified
            result["scam"] = e.scam
            result["fake"] = e.fake
            result["restricted"] = e.restricted
            result["restriction_reason"] = e.restriction_reason if e.restriction_reason else []
            result["lang_code"] = e.lang_code
            
            # Status
            result["status"] = parse_user_status(e.status)
            
            try:
                full = await client(functions.users.GetFullUserRequest(e))
                result["bio"] = full.full_user.about
                result["common_chats"] = full.full_user.common_chats_count
                result["blocked"] = full.full_user.blocked
                result["stories_count"] = full.full_user.stories_count if hasattr(full.full_user, 'stories_count') else 0
                result["profile_photo"] = format_photo(full.full_user.profile_photo)
                result["personal_photo"] = format_photo(full.full_user.personal_photo)
                result["fallback_photo"] = format_photo(full.full_user.fallback_photo)
                result["wallpaper"] = str(full.full_user.wallpaper) if full.full_user.wallpaper else None
                result["theme_emoticon"] = full.full_user.theme_emoticon
                result["emoji_status"] = str(full.full_user.emoji_status) if full.full_user.emoji_status else None
            except:
                pass
        
        return result
    return jsonify(loop.run_until_complete(get()))

@app.route('/ultra')
def ultra():
    username = request.args.get('username', '').strip()
    if not username: return jsonify({"error": "Missing username"}), 400
    
    async def get():
        await client.connect()
        clean = username.replace("@", "")
        e = await client.get_entity(f"@{clean}")
        
        result = await prime_get(e, clean)
        
        # Extra ULTRA info
        if not hasattr(e, 'broadcast'):
            try:
                # Get mutual contacts
                contacts = await client(functions.contacts.GetContactsRequest(hash=0))
                result["is_contact"] = any(c.id == e.id for c in contacts.contacts)
                
                # Get common groups
                result["common_groups"] = []
                dialogs = await client.get_dialogs()
                for d in dialogs:
                    if d.is_group:
                        try:
                            participants = await client.get_participants(d)
                            if any(p.id == e.id for p in participants):
                                result["common_groups"].append({
                                    "id": d.id,
                                    "title": d.title,
                                    "username": d.entity.username if hasattr(d.entity, 'username') else None
                                })
                        except:
                            pass
            except:
                pass
        
        return result
    
    async def prime_get(e, clean):
        result = {
            "status": "success",
            "chat_id": e.id,
            "username": getattr(e, 'username', clean),
            "type": "user",
            "first_name": e.first_name,
            "last_name": e.last_name,
            "phone": e.phone,
            "premium": e.premium,
            "verified": e.verified,
            "scam": e.scam,
            "fake": e.fake,
            "restricted": e.restricted,
            "restriction_reason": e.restriction_reason if e.restriction_reason else [],
            "lang_code": e.lang_code,
            "status": parse_user_status(e.status),
            "credit": "@BRONX_ULTRA"
        }
        
        try:
            full = await client(functions.users.GetFullUserRequest(e))
            result["bio"] = full.full_user.about
            result["common_chats_count"] = full.full_user.common_chats_count
            result["stories_count"] = getattr(full.full_user, 'stories_count', 0)
            result["profile_photo"] = format_photo(full.full_user.profile_photo)
            result["emoji_status"] = str(full.full_user.emoji_status) if full.full_user.emoji_status else None
            result["premium_since"] = str(full.full_user.premium_since) if hasattr(full.full_user, 'premium_since') else None
        except:
            pass
        
        return result
    
    return jsonify(loop.run_until_complete(get()))

@app.route('/channel')
def channel():
    username = request.args.get('username', '').strip()
    if not username: return jsonify({"error": "Missing username"}), 400
    
    async def get():
        await client.connect()
        clean = username.replace("@", "")
        e = await client.get_entity(f"@{clean}")
        
        result = {
            "status": "success",
            "chat_id": e.id,
            "username": getattr(e, 'username', clean),
            "type": "channel" if hasattr(e, 'broadcast') else "group",
            "title": e.title,
            "participants_count": getattr(e, 'participants_count', None),
            "verified": e.verified,
            "scam": e.scam,
            "fake": e.fake,
            "credit": "@BRONX_ULTRA"
        }
        
        try:
            full = await client(functions.channels.GetFullChannelRequest(e))
            result["about"] = full.full_chat.about
            result["linked_chat_id"] = full.full_chat.linked_chat_id
            result["invite_link"] = full.full_chat.exported_invite.link if full.full_chat.exported_invite else None
            result["admins_count"] = full.full_chat.admins_count if hasattr(full.full_chat, 'admins_count') else None
            result["kicked_count"] = full.full_chat.kicked_count if hasattr(full.full_chat, 'kicked_count') else None
            result["banned_count"] = full.full_chat.banned_count if hasattr(full.full_chat, 'banned_count') else None
            result["can_view_stats"] = full.full_chat.can_view_stats
            result["can_set_username"] = full.full_chat.can_set_username
            result["can_set_stickers"] = full.full_chat.can_set_stickers
        except:
            pass
        
        return result
    return jsonify(loop.run_until_complete(get()))

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query: return jsonify({"error": "Missing query"}), 400
    
    async def get():
        await client.connect()
        results = await client(functions.contacts.SearchRequest(q=query, limit=20))
        
        return {
            "status": "success",
            "query": query,
            "users": [{
                "id": u.id,
                "username": u.username,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "premium": u.premium,
                "verified": u.verified
            } for u in results.users],
            "chats": [{
                "id": c.id,
                "title": c.title,
                "username": getattr(c, 'username', None),
                "participants": getattr(c, 'participants_count', None)
            } for c in results.chats],
            "credit": "@BRONX_ULTRA"
        }
    return jsonify(loop.run_until_complete(get()))

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "credit": "@BRONX_ULTRA"})

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
