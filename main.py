import os
import discord
from keep_alive import keep_alive
import requests

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

Cookies = os.environ.get("cookies")

print(Cookies)

def GetPending():
    url = "https://economy.roblox.com/v2/users/5012222377/transaction-totals"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://www.roblox.com",
        "Connection": "keep-alive",
        "Referer": "https://www.roblox.com/",
        "Cookie": str(Cookies),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers"
    }

    params = {
        "timeFrame": "Month",
        "transactionType": "summary"
    }

    response = requests.get(url, headers=headers, params=params)
    print("response:",response)
    return response.json()["pendingRobuxTotal"]


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    keep_alive()

async def is_admin(ctx):
    for role in ctx.author.roles:
        if role.name == "Admin" or role.name == "Game Tester" or role.name == "Tester" or role.permissions.administrator:  # Check for both "Admin" role name and administrator permission
            return True
    return False

async def add_reaction(message):
  try:
      await message.add_reaction("😬")
  except discord.HTTPException as error:
    print(f"Error adding reaction: {error}")

async def get_first_message(Message):
    channel = Message.channel
    async for first_message in channel.history(limit=1, oldest_first=True):
        return first_message  

@client.event
async def on_message(message):
    print("on_message", message.content, "!", message.channel.type)
    if message.author == client.user: 
        return

    print("is_admin(message):", await is_admin(message))

    if await is_admin(message) == False:
        return

    if message.content.lower() == "$del" and message.channel.type == discord.ChannelType.public_thread:
        if not message.channel.permissions_for(message.guild.me).manage_channels:
            await message.channel.send("I don't have permission to delete channels!")
            return

        # Confirmation before deletion (optional)
        confirmation_message = await message.channel.send("Are you sure you want to delete this forum channel? (yes/no)")
        response = await client.wait_for('message', check=lambda msg: msg.author == message.author and msg.channel == confirmation_message.channel)

        if response.content.lower() == "yes":
            await message.channel.delete()
        else:
            await confirmation_message.delete()
            await message.channel.send("Deletion cancelled.")

    if message.content.lower() == "$im" and message.channel.type == discord.ChannelType.public_thread:
        target_channel = message.channel
        old_channel_name = target_channel.name
        confirmation_message = await message.channel.send("This Channel is now Set as Important")
        FirstMessageInChannel = await get_first_message(message)
        await target_channel.edit(name="[Important] " + str(old_channel_name))
        await add_reaction(FirstMessageInChannel)

    if message.content.lower() == "$pe" or message.content.lower() == "$pending":
        target_channel = message.channel
        # text = "Current Pending:" + str(GetPending())
        # await message.channel.send(text)


token = os.environ.get("token")
client.run(token)
