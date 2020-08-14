import discord
from ThreeWords import ThreeWords
from discord.ext import commands
from os import path
import random as r
import asyncio


# word lists
officialThreeWords = ThreeWords('./data/otw.txt')
randomThreeWords = ThreeWords('./data/randwords.txt')
cardList = ThreeWords('./data/White Cards.txt')


class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print("Misc initialized")

    # events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user.name} is connected to the discord!')
        game = discord.Game(name="Cave_Mover")
        await self.bot.change_presence(activity=game)

    @commands.Cog.listener()
    async def on_message(self, message):
        if "69" in message.content:
            await message.channel.send("Nice :point_left::sunglasses::point_right:")

    """@commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        async with channel.typing():
            await asyncio.sleep(1)"""

    # commands
    @commands.command()
    async def random(self, ctx, number: int = 1, word_list='r'):
        """
        Returns a randomized three-word
        """
        if word_list == 'r':
            response = [
                randomThreeWords.metawords()
                for _ in range(number)
            ]
        elif word_list == 'c':
            response = [
                cardList.metawords()
                for _ in range(number)
            ]
        elif word_list == 't':
            response = [
                officialThreeWords.metawords()
                for _ in range(number)
            ]
        else:
            response = []
        await ctx.send('\n'.join(response))

    @commands.command()
    async def add(self, ctx, *words):
        """
        Add new words to the list
        """
        with open(f'randwords.txt', 'a') as f:
            f.write("\n".join(words))
            randomThreeWords.load('randwords.txt')
        await ctx.send(f'Added: {", ".join(words)}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def message(self, ctx, guild, channel, message):
        guild = discord.utils.get(self.bot.guilds, name=guild)
        channel = discord.utils.get(guild.channels, name=channel)
        await channel.send(message)

    @commands.command(name='opt-in')
    async def add_role(self, ctx):
        """
        Get the @all role
        :param ctx: Discord context
        """
        member = ctx.author
        role = ctx.guild.roles[1]
        await member.add_roles(role)
        await ctx.send('You have been added to @all.')

    @commands.command(name='opt-out')
    async def remove_role(self, ctx):
        """
        Removed the @all role
        :param ctx: Discord context
        """
        member = ctx.author
        role = ctx.guild.roles[1]
        await member.remove_roles(role)
        await ctx.send('You have been removed from @all.')

    @commands.command(name="epic")
    async def say_epic(self, ctx):
        """
        extreme epic
        :param ctx: discord context
        """
        await ctx.send(r.choice(('That^ is epic', 'epic', 'cipe', 'EPIC',
                                 'most epic', 'yes.', 'very epic', 'indeed, epic',
                                 "yep, that's pretty epic", 'so epic', 'I know, right?')))
        
    @commands.command(name="-epic")
    async def not_epic(self, ctx):
        """
        most unfortunate
        :param ctx: discord context
        """
        await ctx.send(r.choice(("That's not epic", 'not epic', 'cipe ton', '-EPIC',
                                 'least epic', 'no. sorry.', 'not very epic', 'indeed, unepic',
                                 "yep, that's not very epic", 'no epic', 'so sad.')))

    @commands.command(name="scramble")
    async def scramble(self, ctx, *message):
        """
        Scramble a sentence
        :param ctx: discord context
        :param message: sentence to scramble
        """
        mlist = [item for item in message]
        if len(mlist) == 1:
            word = mlist.pop(0)
            for char in word:
                mlist.append(char)
            r.shuffle(mlist)
            await ctx.send(''.join(mlist))
        else:
            r.shuffle(mlist)
            await ctx.send(' '.join(mlist))

    @commands.command(name="clean", hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def clean(self, ctx, amount: int):
        await ctx.message.channel.purge(limit=amount)


def setup(bot):
    bot.add_cog(Misc(bot))
