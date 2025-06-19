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

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

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

    content_lower = message.content.lower()

    if "vxtwitter.com" in content_lower:
        return

    if "x.com" not in content_lower:
        return

    pattern = r'https?://x\.com/[^\s]+'
    matches = re.findall(pattern, message.content)

    if not matches:
        return

    modified_links = [url.replace('x.com', 'vxtwitter.com') for url in matches]

    try:
        await message.delete()
        for url in modified_links:
            await message.channel.send(url)
            await asyncio.sleep(0.5)
    except discord.Forbidden:
        print("沒有刪除權限，請確認 BOT 權限足夠")
    except discord.HTTPException as e:
        print(f"刪除訊息時出錯：{e}")

keep_alive()
client.run(TOKEN)
