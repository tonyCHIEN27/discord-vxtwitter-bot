from flask import Flask
import threading
import discord
import os
import re
import asyncio

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN is None:
    print("請設定環境變數 DISCORD_BOT_TOKEN")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

bot_enabled = True

def is_admin(member):
    return any(role.permissions.administrator for role in member.roles)

@client.event
async def on_ready():
    print(f'已登入：{client.user}')

@client.event
async def on_message(message):
    global bot_enabled

    if message.author == client.user:
        return

    if message.content.lower() == "!bot on":
        if is_admin(message.author):
            bot_enabled = True
            await message.channel.send("機器人轉換功能已啟用 ✅")
        else:
            await message.channel.send("你沒有權限執行此指令 ❌")
        return

    if message.content.lower() == "!bot off":
        if is_admin(message.author):
            bot_enabled = False
            await message.channel.send("機器人轉換功能已停用 ⛔")
        else:
            await message.channel.send("你沒有權限執行此指令 ❌")
        return

    if not bot_enabled:
        return

    if "vxtwitter.com" in message.content.lower():
        return

    if "x.com" not in message.content.lower():
        return

    # 取出 x.com 連結
    pattern = r'(https?://x\.com/[^\s]+)'
    matches = re.findall(pattern, message.content)

    if not matches:
        return

    # 把原網址用 < > 包起來 (隱藏縮圖)
    modified_links = [f"<{url}>" for url in matches]

    try:
        # 回覆原訊息
        await message.channel.send(
            f"{message.author.mention} 分享的連結（隱藏縮圖）: {' '.join(modified_links)}"
        )

        # 再另外貼上 vxtwitter 轉換版
        for url in matches:
            vx_url = url.replace('x.com', 'vxtwitter.com')
            await message.channel.send(vx_url)
            await asyncio.sleep(0.5)

    except Exception as e:
        print(f"出現錯誤：{e}")

keep_alive()
client.run(TOKEN)
