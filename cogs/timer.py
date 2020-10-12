import discord
import time
import asyncio
from utils import *
from discord.ext import commands


class Timer(commands.Cog):
    clocks = []

    def __init__(self, bot):
        self.bot = bot
        print("Timer initialized")

    @commands.command()
    async def timer(self, ctx, set_time: int = 0):
        """
        Stopwatch timer
        """
        clock = get(self.clocks, guild=ctx.guild, channel=ctx.message.channel)
        if clock is None:
            clock = Clock(ctx, set_time)
            await clock.start()
        else:
            await clock.stop()

    @commands.command()
    async def countdown(self, ctx, set_time: int = 60):
        """
        Countdown timer
        """
        clock = get(self.clocks, guild=ctx.guild, channel=ctx.message.channel)
        if clock is None:
            clock = Clock(ctx, set_time)
            await clock.countdown(ctx)
        else:
            await clock.stop()


def setup(bot):
    bot.add_cog(Timer(bot))


class Clock:
    TIMER_TEXT = "{}:{}"

    def __init__(self, ctx, set_time):
        self.full_time = abs(set_time)
        self.current_time = abs(set_time)
        self.is_running = False
        self.guild = ctx.guild
        self.channel = ctx.message.channel

        Timer.clocks.append(self)

    def format_time(self, seconds):
        return self.TIMER_TEXT.format(seconds // 60, str(seconds % 60).zfill(2))

    async def start(self, direction=1):
        self.is_running = True
        start_time = time.time()
        message = await self.channel.send(self.format_time(self.current_time))
        self.current_time += direction
        while self.current_time > 0 and self.is_running:
            await asyncio.sleep(1)
            self.current_time = int(time.time() - start_time)
            try:
                await message.edit(content=self.format_time(self.current_time))
            except:
                await self.stop()

    async def stop(self):
        self.is_running = False
        Timer.clocks.remove(self)
        await self.channel.send(f"Timer stopped at " + self.format_time(self.current_time))

    async def countdown(self, ctx):
        self.is_running = True
        start_time = time.time()
        time_interval = 0
        max_time = self.current_time

        message = await self.channel.send(self.format_time(self.current_time))
        while self.current_time - time_interval > 0 and self.is_running:
            await asyncio.sleep(1)
            self.current_time = max_time - int(time.time() - start_time)
            try:
                await message.edit(content=self.format_time(self.current_time))
            except:
                await self.stop()
        if self.is_running:
            await self.stop()
            if ctx.message.mentions:
                for _ in range(self.full_time // 6):
                    await asyncio.sleep(2)
                    for member in ctx.message.mentions:
                        await ctx.send(member.mention)
