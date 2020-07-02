import discord
import pickle
import os
from discord.ext import commands

client = None


class Games(commands.Cog):
    hasRun = False
    countingGameInstance = None

    class CountingGame:
        def __init__(self, guild, channel):
            self.count_index = 0
            self.high_score = 0
            self.last_player = None
            self.channel = (guild, channel)

        def input(self, ctx, number):
            channel = get_channel(self.channel[0], self.channel[1])
            last = discord.utils.get(channel.guild.members, name=self.last_player)
            if ctx.author != last and number == self.count_index + 1:
                self.count_index += 1
                self.last_player = ctx.author.name

                if self.count_index > self.high_score:
                    self.high_score = self.count_index
                    return f'highscore: {self.high_score}', None
                else:
                    return None, None
            else:
                self.count_index = 0
                self.last_player = None
                message = f"Nice job, {ctx.author.name}, you ruined it."
                if self.high_score == self.count_index:
                    message += f"\nNew high score: {self.high_score}"
                return None, message

    def __init__(self, bot):
        global client
        self.bot = bot
        client = bot
        print("Games initialized")

    async def run_once(self):
        if not self.hasRun:
            self.hasRun = True
            await self.initialize_counting_game()

    async def initialize_counting_game(self):
        self.countingGameInstance = self.CountingGame("Incomprehensible Games", "counting-game")
        if not os.path.exists('countinggame.dat'):
            with open(f'countinggame.dat', 'w+b') as file:
                pickle.dump(self.countingGameInstance, file)
        with open(f'countinggame.dat', 'r+b') as file:
            self.countingGameInstance = pickle.load(file)
        channel = get_channel(self.countingGameInstance.channel[0], self.countingGameInstance.channel[1])
        topic = channel.topic
        high_score = int(topic[11:len(topic)])
        count_index = 0
        last_player = None
        async for message in channel.history(limit=20):
            if '~# ' in message.content:
                count_index = int(message.content[3:len(message.content)])
                last_player = message.author.name
                break
        if count_index > self.countingGameInstance.count_index:
            self.countingGameInstance.count_index = count_index
            self.countingGameInstance.last_player = last_player
            if self.countingGameInstance.count_index > self.countingGameInstance.high_score:
                self.countingGameInstance.high_score = self.countingGameInstance.count_index
        if self.countingGameInstance.high_score > high_score:
            await channel.edit(topic=f'highscore: {self.countingGameInstance.high_score}')

        # save state to data file
        with open(f'countinggame.dat', 'w+b') as file:
            pickle.dump(self.countingGameInstance, file)

    # events
    @commands.Cog.listener()
    async def on_ready(self):
        # load_data()
        await self.run_once()

    # commands
    @commands.command(name='#')
    async def counting_game(self, ctx, number: int):
        topic, message = self.countingGameInstance.input(ctx, number)
        channel = get_channel(self.countingGameInstance.channel[0], self.countingGameInstance.channel[1])
        if topic:
            await channel.edit(topic=topic)
        if message:
            await ctx.send(message)
        # save state to data file
        with open(f'countinggame.dat', 'w+b') as file:
            pickle.dump(self.countingGameInstance, file)


def setup(bot):
    bot.add_cog(Games(bot))


def get_channel(guild, channel):
    guild = discord.utils.get(client.guilds, name=guild)
    channel = discord.utils.get(guild.channels, name=channel)
    return channel
