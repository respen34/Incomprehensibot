import discord
from ThreeWords import ThreeWords
from discord.ext import commands


# word lists
officialThreeWords = ThreeWords(f'otw.txt')
randomThreeWords = ThreeWords(f'randwords.txt')
cardList = ThreeWords(f'White Cards.txt')


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

    # commands
    @commands.command()
    async def random(self, ctx, number: int = 1, word_list='r'):
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
    async def add(self, ctx, word):
        with open(f'randwords.txt', 'a') as f:
            f.write(f'\n{word}')
            randomThreeWords.load('randwords.txt')
        await ctx.send(f'Added: {word}.')

    @commands.command(hidden=True)
    async def message(self, ctx, message, guild, channel):
        if ctx.author.name == "respen34":
            guild = discord.utils.get(self.bot.guilds, name=guild)
            channel = discord.utils.get(guild.channels, name=channel)
            await channel.send(message)

    @commands.command(name='opt-in')
    async def add_role(self, ctx):
        """
        Get added to the @all role
        :param ctx: Discord context
        :return:
        """
        member = ctx.author
        role = ctx.guild.roles[1]
        await member.add_roles(role)
        await ctx.send('You have been added to @all.')

    @commands.command(name='opt-out')
    async def remove_role(self, ctx):
        """
        Get removed from the @all role
        :param ctx: Discord context
        :return:
        """
        member = ctx.author
        role = ctx.guild.roles[1]
        await member.remove_roles(role)
        await ctx.send('You have been removed from @all.')


def setup(bot):
    bot.add_cog(Misc(bot))
