# bot.py
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='~')


@bot.command()
async def load(ctx, extension):
    """Load a cog"""
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f"{extension} successfully loaded.")


@bot.command()
async def unload(ctx, extension):
    """Unload a cog"""
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f"{extension} successfully unloaded.")


@bot.command()
async def reload(ctx, extension):
    """Reload a cog"""
    bot.reload_extension(f'cogs.{extension}')
    await ctx.send(f"{extension} successfully reloaded.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("That's not a command!")
    else:
        raise error

print('loading...')
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(token)
