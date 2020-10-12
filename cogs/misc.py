import discord
from ThreeWords import ThreeWords
from discord.ext import commands
from os import path
import random as r
import asyncio
from utils import *


# word lists
officialThreeWords = ThreeWords('./data/otw.txt')
randomThreeWords = ThreeWords('./data/randwords.txt')
cardList = ThreeWords('./data/White Cards.txt')


class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.oppress = False
        self.nice = False
        print("Misc initialized")

    # events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user.name} is connected to the discord!')
        game = discord.Game(name="Cave_Mover")
        await self.bot.change_presence(activity=game)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        # replace all messages
        """await message.delete()
        await message.channel.send(message.content)"""
        # oppression mode
        if self.oppress and message.channel == self.oppress:
            await message.channel.send(self.oppress)
            return
        # nice mode
        if self.nice and message.channel == self.nice:
            await message.channel.send(self.be_nice)
            return
        # 69 check
        if "69 " in message.content.replace(',', ' ').replace('.', ' ').replace('!', ' ').replace('?', ' ') + ' ':
            await message.channel.send("Nice :point_left::sunglasses::point_right:")
        # random response to a message
        if r.random() <= 0.001:
            await message.channel.send("I get it!")
        # check for mentions
        if self.bot.user.mentioned_in(message) and not message.mention_everyone:
            await message.channel.send(r.choice(["Can I help help you?", "Can anyone help you?", "What do you want?"]))
        # dad bot
        await self.dad(message)
        # custom @anyone
        """anyone = get(message.role_mentions, name="anyone")
        if anyone is not None:
            print("testing")
            role = get(message.channel.guild.roles, name="anyone")
            for member in message.channel.guild.members:
                if role in member.roles:
                    await member.remove_roles(role)
            print(message.channel.guild.members)
            member = r.choice(message.channel.guild.members)
            print(member.name)
            await member.add_roles(role)"""


    """@commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        async with channel.typing():
            await asyncio.sleep(1)"""
    # text functions
    def oppress(self):
        return r.choice(["STOP TALKING ALREADY", "SHUT UP!", "UNACCEPTABLE!", "NOT IN MY HOUSE", "CUT THAT OUT!",
                         "ONE MORE WORD OUTTA YOU AND YOU'RE GONE!", "DON'T TEST ME I WILL BAN YOU!", "KNOCK IT OFF",
                         "DELET THIS NOW!", "GET OUT!", "NOT OK", "NOPE!", "CUT IT", "STOP!", "SHI'NE!", "JUST NO.",
                         "WATCH OUT BUDDY. I WILL FIND YOU!", "I WILL KILL YOU AND DISRESPECT YOUR WIDOW!",
                         "YOU CAN'T DO THAT HERE", "THAT'S ENOUGH OF THAT", "NO! NO! NO! OUT!", "I don't care. GET OUT!"
                         ])

    def be_nice(self):
        r.choice(["Have a lovely day!", "I LOVE that look!!!!!!!;)", "You look not terrible!", "Pretty neat!",
                  "That's soooooooooooooooooooo cool!♥", "What you said wasn't half bad.", "You are not garbage.",
                  "Your face looks less punchable today.", "You don't smell bad and I don't hate you at all!",
                  "Today is the first day of the rest of your life.", "You look like you need a hug.♥ XOXOXO",
                  "Gold Star", "You're so swell.", "Lookin' Snazzy.", "Lookin' good!", "Hugs and Kisses!",
                  "Feel good about yourself, NOW!", "You're decent", "Don't feel sad, just don't.", "I love that!",
                  "This conversation is interesting.", "Love ya!", "Call me!♥",
                  "This is the best conversation that I'm commenting on right now in this channel."
                  ])

    async def dad(self, message):
        DAD_CHANCE = 1
        dad_check = " " + message.content
        dad_check = dad_check.replace(" I'm ", " I am ").replace(" i'm ", " I am ")
        dad_check = dad_check.replace(" i am ", " I am ").replace(" im ", " I am ").replace(" Im ", " I am ")
        if "I am " in dad_check and r.random() < DAD_CHANCE:
            stop = dad_check.find(".")
            if stop == -1:
                name = dad_check[dad_check.find("I am ") + 5:]
            else:
                name = dad_check[dad_check.find("I am ") + 5:stop]
            await message.channel.send(f"Hi, {name}, I'm dad.")

    # commands
    @commands.command()
    async def oppression(self, ctx):
        """There's a new sheriff in town."""
        if not self.oppress:
            self.oppress = ctx.message.channel
            await ctx.send("Oppression mode activated.")
        else:
            self.oppress = None
            await ctx.send("Oppression mode deactivated.")

    @commands.command()
    async def nice(self, ctx):
        """Hello, nice to see you."""
        if not self.nice:
            self.nice = ctx.message.channel
            await ctx.send("Nice mode activated.")
        else:
            self.nice = None
            await ctx.send("No more Mr. Nice Guy.")

    @commands.command()
    async def random(self, ctx, number: int = 1, word_list='r'):
        """Returns a randomized three-word"""
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
        """Add new words to the list"""
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
        """Get the @all role
        :param ctx: Discord context"""
        member = ctx.author
        role = ctx.guild.roles[1]
        await member.add_roles(role)
        embed = discord.Embed(
            title='You have been added to @all.',
            color=discord.Color.dark_gray()
        )
        await ctx.send(embed=embed)

    @commands.command(name='opt-out')
    async def remove_role(self, ctx):
        """Remove the @all role
        :param ctx: Discord context"""
        member = ctx.author
        role = ctx.guild.roles[1]
        await member.remove_roles(role)
        embed = discord.Embed(
            title='You have been removed from @all.',
            color=discord.Color.dark_gray()
        )
        await ctx.send(embed=embed)

    @commands.command(name="epic")
    async def say_epic(self, ctx):
        """extreme epic
        :param ctx: discord context"""
        response = r.choice(('That^ is epic', 'epic', 'cipe', 'EPIC',
                             'most epic', 'yes.', 'very epic', 'indeed, epic',
                             "yep, that's pretty epic", 'so epic', 'I know, right?'))
        await ctx.send(response)
        
    @commands.command(name="-epic")
    async def not_epic(self, ctx):
        """most unfortunate
        :param ctx: discord context"""
        await ctx.send(r.choice(("That's not epic", 'not epic', 'cipe ton', '-EPIC',
                                 'least epic', 'no. sorry.', 'not very epic', 'indeed, unepic',
                                 "yep, that's not very epic", 'no epic', 'so sad.')))

    @commands.command(name="epic?")
    async def maybe_epic(self, ctx):
        """Let's find out!"""
        await ctx.send(r.choice(("yes. epic.", "no. not epic.", "indeed. that is epic.", "sorry. not epic.")))

    @commands.command(name="scramble")
    async def scramble(self, ctx, *message):
        """Scramble a sentence
        :param ctx: discord context
        :param message: sentence to scramble"""
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

    @commands.command(name="mute")
    @commands.is_owner()
    async def mute(self, ctx):
        channel = ctx.author.voice.channel
        if channel is None:
            await ctx.send("You must be in voice to use this command.")
        for member in channel.members:
            if member == self.bot:
                continue
            await member.edit(mute=not member.voice.mute)

    @commands.command(name="lookup")
    async def lookup(self, ctx):
        member = ctx.message.mentions[0]
        if member is None:
            return
        embed = discord.Embed(
            title=member.name,
            description=member.id
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
