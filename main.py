import discord
import os
from dotenv import load_dotenv
import buttplug
import logging
import sys
import time


load_dotenv()
name = "Dichotomy"
bot = discord.Bot()
token = os.getenv("TOKEN")
channel_id = os.getenv("CHANNEL_ID")
sub_id = os.getenv("SUB_ID")
intents = discord.Intents.default()
intents.message_content = True
bot_client = discord.Client(intents=intents)
vibe_device: buttplug.Device
vibe_client: buttplug.Client

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
        message.channel != channel_id | 
        message.author == bot_client.user | 
        message.author == sub_id
    ):
        return

    if "very" in message.content:
        strength = 2
    if "extremely" in message.content:
        strength = 3
    if "good fox" in message.content:
        await message.add_reaction("🪄")
        await reward_fox(strength)
    elif "bad fox" in message.content:
        await message.add_reaction("🔌")
        await punish_fox(strength)
    elif message.content == "$RetryConnect":
        await vibe_client.disconnect()
        await on_ready()


async def reward_fox(strength):
    global vibe_device
    await vibe_device.actuators[0].command(strength / 10)
    time.sleep(strength)
    await vibe_device.actuators[0].command(0)


async def punish_fox(strength):
    None


@bot_client.event
async def on_ready():
    global vibe_device
    global vibe_client
    connected = 0
    vibe_client = buttplug.Client(name, buttplug.ProtocolSpec.v3)
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
            logging.error("Wrong Intiface device connected")
            return
        connected += 1
        await update_status(connected)
    except Exception as e:
        logging.error(f"Could not connect to server, exiting: {e}")


@bot_client.event
async def on_disconnect():
    await vibe_client.disconnect()


bot_client.run(token)
