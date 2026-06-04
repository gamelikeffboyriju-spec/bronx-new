from flask import Flask, request, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import os

app = Flask(__name__)

# ============================================
# CONFIGURATION
# ============================================
API_ID = int(os.environ.get('API_ID', '36879151'))
API_HASH = os.environ.get('API_HASH', '45360a236343352099ffa29570f48700')
SESSION_STRING = os.environ.get('SESSION_STRING', '1BVtsOMMBu7v0Z4l4crbseaz_Jk5pbPQmvIxIPA8YwD04nSQotIPK-unFuWFDu18gEFS3BS-MJFe_V6a3SyoI22fnfLpOr5tHStDXpXeUk5gmsuIsa6U47lTj4aaj_f0k-yxj9ZO28Rluf89rvLBLZCUXg4mFdJQj1NdBdCkszNqWwLi569ouj4bZsZzlXSzIg2NNUHK2QL1nxLUj0xCDKcmg3oyEUy2gP4UCCQgRte8VwUQSEkEUhrHwWTijibAPVl0MJquDqaoiw2G4eYXwlXB4l7YzW207px8longAIoynFVHAqEzf6MJj8HH06iG5iuZe7D8DXPp0FeUjvrky-UdPa9kGTm4=')

# Create new event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Create client
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)

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
        </style>
    </head>
    <body>
        <h1>🆔 BRONX ULTRA API</h1>
        <h3>✅ ONLINE</h3>
        <code>GET /chatid?username=USERNAME</code>
        <p style="color:#555; margin-top:30px;">@BRONX_ULTRA</p>
    </body>
    </html>
    """

@app.route('/chatid')
def chatid():
    username = request.args.get('username', '').strip()
    
    if not username:
        return jsonify({
            "status": "error",
            "message": "Missing username",
            "credit": "@BRONX_ULTRA"
        }), 400
    
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
            result["title"] = getattr(e, 'title', '')
        elif hasattr(e, 'title'):
            result["type"] = "group"
            result["title"] = e.title
        else:
            result["type"] = "user"
            result["first_name"] = getattr(e, 'first_name', '')
        
        return result
    
    try:
        result = loop.run_until_complete(get())
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "credit": "@BRONX_ULTRA"
        }), 404

@app.route('/health')
def health():
    return jsonify({"status": "ok", "credit": "@BRONX_ULTRA"})

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
