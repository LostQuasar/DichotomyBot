import discord
import os
from dotenv import load_dotenv
import buttplug
import logging
import sys
import time

name = "Dichotomy"

load_dotenv()
bot = discord.Bot()
token = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
botClient = discord.Client(intents=intents)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
vibeDevice: buttplug.Device
vibeClient: buttplug.Client


async def updateStatus(num):
    await botClient.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing, name=f"with {num}/2"
        )
    )


@botClient.event
async def on_message(message):
    global vibeClient
    if message.author == botClient.user:  # | message.author == 208273752956338198:
        return

    strength = 1

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
        await vibeClient.disconnect()
        await on_ready()


async def reward_fox(strength):
    global vibeDevice
    await vibeDevice.actuators[0].command(strength / 10)
    time.sleep(strength)
    await vibeDevice.actuators[0].command(0)


async def punish_fox(strength):
    None


@botClient.event
async def on_ready():
    global vibeDevice
    global vibeClient
    connected = 0

    await updateStatus(connected)

    vibeClient = buttplug.Client(name, buttplug.ProtocolSpec.v3)
    connector = buttplug.WebsocketConnector(
        "ws://127.0.0.1:12345", logger=vibeClient.logger
    )
    try:
        await vibeClient.connect(connector)

        if len(vibeClient.devices) == 0:
            logging.error("No devices connected to Intifcae")
            return

        vibeDevice = vibeClient.devices[0]

        if len(vibeDevice.actuators) == 0:
            logging.error("Wrong Intiface device connected")
            return

        connected += 1
        await updateStatus(connected)

    except Exception as e:
        logging.error(f"Could not connect to server, exiting: {e}")


@botClient.event
async def on_disconnect():
    await vibeClient.disconnect()


botClient.run(token)
