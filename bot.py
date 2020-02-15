#bot.py
import datetime, asyncio, subprocess, random, pickle, os, discord, youtube_dl, jsonpickle
from dotenv import load_dotenv
from ThreeWords import ThreeWords
from discord.ext import commands


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

dataPath = f'{os.getcwd()}\\data\\'

exec(open('audio_player.py').read())
exec(open('maze.py').read())          #code for the cave runner game

#3 different word lists to pull from.
Official_Three_Words = ThreeWords(f'{dataPath}otw.txt')
Random_Three_Words = ThreeWords(f'{dataPath}randwords.txt')
Cards_List = ThreeWords(f'{dataPath}White Cards.txt')

bot = commands.Bot(command_prefix='~')
exec(open('commands.py').read())      #command definitions

    
print('loading...') 
bot.run(token)
