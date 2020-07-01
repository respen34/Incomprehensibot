# bot.py
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='~')


@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f"{extension} successfully loaded.")


@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f"{extension} successfully unloaded.")


@bot.command()
async def reload(ctx, extension):
    bot.reload_extension(f'cogs.{extension}')
    await ctx.send(f"{extension} successfully reloaded.")

print('loading...')
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


os.chdir('./data')
bot.run(token)
