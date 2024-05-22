import discord
import os
from dotenv import load_dotenv
import buttplug
import logging
import sys
import time
from openshock import ControlType, shock_api

load_dotenv()
bot_name = "Dichotomy"
bot = discord.Bot()
token = os.getenv("TOKEN")
channel_id = int(os.getenv("CHANNEL_ID"))
sub_id = os.getenv("SUB_ID")
shock_key = os.getenv("SHOCK_KEY")
shock_id = os.getenv("SHOCK_ID")
term = os.getenv("TERM")

intents = discord.Intents.default()
intents.message_content = True
bot_client = discord.Client(intents=intents)
vibe_device: buttplug.Device
vibe_client: buttplug.Client
shocker: shock_api.shocker

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


async def update_status(num):
    await bot_client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing, name=f"with {num}/2"
        )
    )


@bot_client.event
async def on_message(message):
    global vibe_client
    strength = 1

    if (
        message.channel.id != channel_id
        or message.author == bot_client.user
        or message.author == sub_id
    ):
        return

    if "very" in message.content.lower():
        strength = 2
    if "extremely" in message.content.lower():
        strength = 3
    if "good " + term in message.content.lower():
        await message.add_reaction("🪄")
        await reward(strength)
    elif "bad " + term in message.content.lower():
        await message.add_reaction("🔌")
        await punish(strength)
    elif message.content == "$RetryConnect":
        await vibe_client.disconnect()
        await on_ready()


async def reward(strength):
    global vibe_device
    if vibe_device:
        await vibe_device.actuators[0].command(strength / 10)
        time.sleep(strength)
        await vibe_device.actuators[0].command(0)

async def punish(strength):
    await shocker.control(ControlType.SHOCK, strength, strength*300)


@bot_client.event
async def on_ready():
    global vibe_device, vibe_client, shocker
    connected = 0
    vibe_client = buttplug.Client(bot_name, buttplug.ProtocolSpec.v3)
    connector = buttplug.WebsocketConnector(
        "ws://127.0.0.1:12345", logger=vibe_client.logger
    )

    await update_status(connected)
    try:
        await vibe_client.connect(connector)
        if len(vibe_client.devices) == 0:
            logging.error("No devices connected to Intifcae")
            return
        vibe_device = vibe_client.devices[0]
        if len(vibe_device.actuators) == 0:
            logging.error("Invalid Intiface device connected")
            return
        connected += 1
        await update_status(connected)
    except Exception as e:
        logging.error(f"Could not connect to Intiface server: {e}")

    shocker_api = shock_api(shock_key)
    shocker = shocker_api.create_shocker(shock_id)
    response = shocker.control(ControlType.SOUND, 1, 300, "Dichotomy")

    if response.ok:
        connected += 1
        await update_status(connected)
    else:
        logging.error(f"Could not connect to shocker: {response.content}")


@bot_client.event
async def on_disconnect():
    await vibe_client.disconnect()


bot_client.run(token)
