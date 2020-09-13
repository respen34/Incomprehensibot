from discord.utils import get
from os import path, getcwd
import asyncio


# functions
def get_channel(bot, guild_id, channel_id):
    if isinstance(guild_id, int):
        guild = get(bot.guilds, id=guild_id)
    elif isinstance(guild_id, str):
        guild = get(bot.guilds, name=guild_id)
    else:
        guild = None
    if guild is None:
        return
    if isinstance(channel_id, int):
        channel = get(guild.channels, id=channel_id)
    elif isinstance(channel_id, str):
        channel = get(guild.channels, name=channel_id)
    else:
        channel = None
    return channel


# constants
DATA_PATH = path.join(getcwd(), "data")

