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
