from flask import Flask, request, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import os

app = Flask(__name__)

# ============================================
# CONFIGURATION
# ============================================
API_ID = int(os.environ.get('API_ID', '31968824'))
API_HASH = os.environ.get('API_HASH', 'd9847a6694b961248f4052d16b89b912')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

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
