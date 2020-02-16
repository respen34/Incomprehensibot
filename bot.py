# bot.py
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

dataPath = f'{os.getcwd()}\\data\\'  # deprecated

bot = commands.Bot(command_prefix='~')
exec(open('commands.py').read())  # command definitions

print('loading...')
bot.run(token)
