import discord
import datetime
import asyncio
from discord.ext import commands


class FPF(commands.Cog):
    hasRun = False

    def __init__(self, bot):
        self.bot = bot
        print("FPF initialized")

    async def run_once(self):
        if not self.hasRun:
            self.hasRun = True
            await self.fanny_pack_friday()

    def get_channel(self, guild, channel):
        guild = discord.utils.get(self.bot.guilds, name=guild)
        channel = discord.utils.get(guild.channels, name=channel)
        return channel

    async def fanny_pack_friday(self):
        # prints fanny pack friday meme once every friday at 1pm cst/cdt
        delay = next_friday()
        print(f'{delay} seconds until the next fanny pack friday!')
        await asyncio.sleep(delay)
        guild = discord.utils.get(self.bot.guilds, name='Incomprehensible Games')
        channel = discord.utils.get(guild.channels, name='image-surveillance')
        await channel.send('It is fanny pack friday!',
                           file=discord.File(
                               ';lkaypoi2374509123n4pds0f9877akj123;l459p\
                               -837409u0u0-uklfjpasdo;klzxjcpl;j---adsf;lk32-asfl;ahdfl;kja4.mp4'))
        print('I gotta tell ya, I just feel super about it.')
        await asyncio.sleep(600)
        await self.fanny_pack_friday()

    # events
    @commands.Cog.listener()
    async def on_ready(self):
        await self.run_once()

    # commands
    @commands.command()
    async def fpf(self, ctx):
        """Returns the number of seconds until the next fanny pack friday."""
        await ctx.send(f'Only {int(next_friday())} more seconds until the next fanny pack friday')


def next_friday():
    # returns the number of seconds until 1pm on the closest friday
    today = datetime.datetime.today()

    if today.weekday() == 4 and today.hour > 13 or (today.hour == 13 and (today.minute > 0 or today.second > 0)):
        day = 7
    else:
        day = (-today.weekday() - 3) % 7

    friday = datetime.datetime(today.year, today.month, today.day, 13, 0, 0, 0) + datetime.timedelta(days=day)
    return (friday - today).total_seconds()


def setup(bot):
    bot.add_cog(FPF(bot))
