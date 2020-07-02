import discord
import time
import asyncio
from discord.ext import commands


class Timer(commands.Cog):
    clock = None

    def __init__(self, bot):
        self.bot = bot
        print("Timer initialized")

    @commands.command()
    async def timer(self, ctx, set_time: int = 0):
        if self.clock is None:
            self.clock = Clock(ctx, set_time)
            await self.clock.start()
        else:
            await self.clock.stop()
            self.clock = None

    @commands.command()
    async def countdown(self, ctx, set_time: int):
        if self.clock is None:
            self.clock = Clock(ctx, set_time)
            await self.clock.countdown(ctx)
        else:
            await self.clock.stop()
            self.clock = None


def setup(bot):
    bot.add_cog(Timer(bot))


class Clock:
    def __init__(self, ctx=None, set_time: int = 1):
        self.current_time = abs(set_time)
        self.is_running = False
        self.ctx = ctx

    async def start(self, direction=1):
        self.is_running = True
        start_time = time.time()
        message = await self.ctx.send(str(self.current_time))
        self.current_time += direction
        while self.current_time > 0 and self.is_running:
            await asyncio.sleep(1)
            self.current_time = int(time.time() - start_time)
            try:
                await message.edit(content=f"{self.current_time} seconds.")
            except:
                await self.stop()

    async def stop(self):
        self.is_running = False
        await self.ctx.send(f"Timer stopped at {self.current_time} seconds.")

    async def countdown(self, ctx):
        self.is_running = True
        start_time = time.time()
        time_interval = 0
        max_time = self.current_time
        message = await self.ctx.send(str(self.current_time))
        while self.current_time - time_interval > 0 and self.is_running:
            await asyncio.sleep(1)
            self.current_time = max_time - int(time.time() - start_time)
            try:
                await message.edit(content=f"{self.current_time - time_interval} seconds remaining.")
            except:
                await self.stop()
        if self.is_running:
            for _ in range(30):
                await asyncio.sleep(2)
                for member in ctx.message.mentions:
                    await ctx.send(member.mention)
        await self.stop()
