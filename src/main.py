import discord
import os
from dotenv import load_dotenv
import buttplug
import logging
import sys
import time
import json
from openshock import ControlType, openshock_api

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
shocker: openshock_api.shocker

config_default = {
    "ShockLow": 2,
    "ShockHigh": 6,
    "VibeLow": 2,
    "VibeHigh": 6,
    "Duration": 300,
}

config = None

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


async def update_status(num):
    await bot_client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing, name=f"with {num}/2"
        )
    )


async def update_config(key, value):
    if key in config.keys():
        config[key] = value
        with open("config.json", "w") as file_config:
            json.dump(config, file_config, indent=2)
    else:
        logging.error("Config key provided is invalid")


@bot_client.event
async def on_message(message):
    global vibe_client
    strong = False

    if (
        message.channel.id != channel_id
        or message.author == bot_client.user
        or message.author == sub_id
    ):
        return

    if "very" in message.content.lower():
        strong = True
    if "good " + term in message.content.lower():
        await message.add_reaction("🪄")
        await reward(strong)
    elif "bad " + term in message.content.lower():
        await message.add_reaction("🔌")
        await shocker.control(
            ControlType.SHOCK,
            config["ShockHigh" if strong else "ShockLow"],
            config["Duration"],
            message.author.display_name,
        )
    if message.content == "$RetryConnect":
        await vibe_client.disconnect()
        await on_ready()

    if "$Config" in message.content:
        split_message = message.content.split(" ")
        try:
            await update_config(split_message[1], int(split_message[2]))
            await message.add_reaction("✅")
        except Exception as e:
            logging.error(f"Error occurred while updating config: {e}")


async def reward(strong: bool):
    global vibe_device
    if vibe_device:
        await vibe_device.actuators[0].command(
            ("VibeHigh" if strong else "VibeLow") / 10
        )
        time.sleep(config["Duration"])
        await vibe_device.actuators[0].command(0)


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
            logging.error("No devices connected to Intiface")
            return
        vibe_device = vibe_client.devices[0]
        if len(vibe_device.actuators) == 0:
            logging.error("Invalid Intiface device connected")
            return
        connected += 1
        await update_status(connected)
    except Exception as e:
        logging.error(f"Could not connect to Intiface server: {e}")

    shocker_api = openshock_api(shock_key)
    shocker = shocker_api.create_shocker(shock_id)
    response = await shocker.control(ControlType.SOUND, 1, 300, "Dichotomy")

    if response.ok:
        connected += 1
        await update_status(connected)
    else:
        logging.error(
            f"Could not connect to shocker: {json.loads(response.content)['message']}"
        )


@bot_client.event
async def on_disconnect():
    await vibe_client.disconnect()


if __name__ == "__main__":
    try:
        with open("config.json", "r") as file_config:
            config = json.load(file_config)
    except:
        logging.warn("Config loading failed.")

    if not config:
        with open("config.json", "w+") as file_config:
            json.dump(config_default, file_config, indent=2)

    bot_client.run(token)
