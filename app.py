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
API_HASH = os.environ.get('API_HASH', 'd9847a6694b961248f4052d16b89b912'))
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
    <h1 style='color:#0ff;background:#000;text-align:center;padding:50px;'>
    🆔 BRONX ULTRA API ✅<br>
    <small style='color:#888;'>/chatid?username=USERNAME</small>
    </h1>
    """

@app.route('/chatid')
def chatid():
    username = request.args.get('username', '').strip()
    
    if not username:
        return jsonify({"status":"error","message":"Missing username","credit":"@BRONX_ULTRA"}), 400
    
    async def get():
        await client.connect()
        e = await client.get_entity(username.replace("@", ""))
        return {
            "status": "success",
            "chat_id": e.id,
            "username": getattr(e, 'username', username),
            "type": "user" if not hasattr(e,'broadcast') else "channel",
            "name": getattr(e, 'first_name', getattr(e, 'title', '')),
            "credit": "@BRONX_ULTRA"
        }
    
    result = loop.run_until_complete(get())
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({"status":"ok"})

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
