import discord
import pickle
import json
import os
import random as r
import math as m
from discord.ext import commands
from utils import *

"""
Counting game for discord.
Before counting game can be played on a server
create a channel for counting game, and run the ~setupCountingGame command in it to initialize the game
then you're all set.
"""

COUNTING_GAME_TOPIC = "Counting Game: High Score = {}\n" \
                      "Rules:\n" \
                      "Count up to infinity\n" \
                      "Only enter one number in a row\n" \
                      "Only enter the next number in the sequence"


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


class Games(commands.Cog):
    cg_data_path = "./data/cg_instances.json"

    def __init__(self, bot):
        self.bot = bot
        if not os.path.exists(self.cg_data_path):
            with open(self.cg_data_path, "w") as f:
                json_object = {}
                json.dump(json_object, f)
        # load all counting game instances
        self.countingGameInstances = None
        self.load_counting_game()
        print("Games initialized")

    def save_counting_game(self):
        with open(self.cg_data_path, "w") as f:
            json.dump(self.countingGameInstances, f)

    def load_counting_game(self):
        with open(self.cg_data_path) as f:
            self.countingGameInstances = json.load(f)

    def get_channel(self, guild_id, channel_id):
        channel = discord.utils.get(self.bot.get_all_channels(), guild__id=guild_id, id=channel_id)
        return channel

    def print_stats(self, instance, users):
        stats = f"High score: {instance['highscore']}\n"
        for user in users:
            user_stats = instance["players"].get(str(user.id))
            if user_stats is None:
                continue
            stats += f"{user.name}:\n" \
                     f"Current: {user_stats['current']}   |" \
                     f"   All Time: {user_stats['points']}   |   Failures: {user_stats['fails']}\n"
        return stats

    def get_stats(self, channel, member=None):
        instance = self.countingGameInstances[str(channel.guild.id)]
        users = []
        if member == "all":
            for user_id in instance["players"].keys():
                user = get(channel.guild.members, id=int(user_id))
                if user is not None:
                    users.append(user)

        elif member:
            user = get(channel.guild.members, name=member)
            if user is None:
                return f"User {member} not found."
            users.append(user)
            member_stats = instance["players"].get(str())
            if member_stats is None:
                return f"No stats found for {member.name}."

        else:
            for user_id, user_stats in instance["players"].items():
                if user_stats["current"] > 0:
                    user = discord.utils.get(channel.guild.members, id=int(user_id))
                    if user is not None:
                        users.append(user)

        return self.print_stats(instance, users)

    async def give_roles(self, guild):
        instance = self.countingGameInstances[str(guild.id)]
        MASTER_THRESHOLD = 500
        LOSER_THRESHOLD = -200
        current_max = 0
        champion = None
        roles = [discord.utils.get(guild.roles, name=role) for role in ("Counting Champion",
                                                                        "Counting Master", "Loser")]
        for player_id, stats in instance["players"].items():
            member = get(guild.members, id=int(player_id))
            # remove champion role
            # if roles[0] in member.roles:
            #    await member.remove_roles(roles[0])
            # check for champion status
            if stats["current"] > current_max:
                current_max = stats["current"]
                champion = member
            # check for master status
            if stats["points"] >= MASTER_THRESHOLD and roles[1] not in member.roles:
                await member.add_roles(roles[1])
            elif roles[1] in member.roles:
                await member.remove_roles(roles[1])
            # check for loser status
            if (stats["points"] <= LOSER_THRESHOLD) and roles[2] not in member.roles:
                await member.add_roles(roles[2])
            elif roles[2] in member.roles:
                await member.remove_roles(roles[2])
        # give champion rank
        for player_id in instance["players"].keys():
            member = get(guild.members, id=int(player_id))
            if member != champion and roles[0] in member.roles:
                await member.remove_roles(roles[0])
        if instance["last_number"] > 50:
            if not roles[0] in champion.roles:
                await champion.add_roles(roles[0])

    async def retro_check(self, instance, channel):
        if instance["last_message"] is None:
            return
        start_from = await channel.fetch_message(instance["last_message"])
        async for message in channel.history(limit=None, after=start_from, oldest_first=True):
            # debug
            # print(message.content)
            # start at the last entry
            # then check every message after that for rule breakage
            if not is_int(message.content):
                continue
            if not await self.input(instance, message, True):
                break

    async def input(self, instance, message, quiet=False):
        player = message.author.id
        number = int(message.content)
        if number == instance["last_number"] + 1 and player != instance["last_player"]:
            # if correct, update values
            res = True
            instance["last_number"] = number
            instance["last_player"] = player
            instance["last_message"] = message.id

            # update player stats
            player_stats = instance["players"].get(str(player))
            if player_stats is None:
                player_stats = {"current": 1, "points": 1, "fails": 0}
            else:
                player_stats["current"] += 1
                player_stats["points"] += 1
            instance["players"][str(player)] = player_stats

            # check for new high score
            if instance["highscore"] < number:
                instance["highscore"] = number
                # await message.channel.edit(topic=COUNTING_GAME_TOPIC.format(instance["highscore"]))
                if not quiet:
                    await message.channel.edit(topic="High Score: {}".format(instance["highscore"]))

            # if a milestone has been reach, dispense encouragement
            if number % 50 == 0:
                insert = r.choices((number, "{current_number}", number // r.randint(2, 5), r.randint(-number, number)),
                                   (.70, .25, .04, .01))[0]
                response = r.choice(("{}. Great moves, keep it up, proud of you!",
                                     "Wow {} already, nice!",
                                     "{}? That's... uh...\n good?",
                                     "Alright, {} now your getting somewhere! Kinda...",
                                     "Neat, {} is very almost impressive.",
                                     "Wow {}? You're almost close.",
                                     "Nice work on making it to {}!",
                                     "{}. That's a multiple of 50 if I've ever seen one.")).format(insert)
                await message.channel.send(response)
        else:
            # if incorrect, reset values
            res = False
            await message.channel.send("Nice job, {}, you ruined it.".format(message.author.name))

            # update player stats
            failed_player = instance["players"].get(str(player))
            if failed_player is None:
                failed_player = {"current": 0, "points": 0, "fails": 1}
            failed_player["points"] -= m.ceil(instance["last_number"] / 2)
            failed_player["fails"] += 1
            instance["players"][str(player)] = failed_player

            instance["last_number"] = 0
            instance["last_player"] = None
            instance["last_message"] = None
            await message.channel.send(f"Stats:\n{self.get_stats(message.channel)}")
            for player_stats in instance["players"].values():
                player_stats["current"] = 0

        await self.give_roles(message.channel.guild)
        self.save_counting_game()
        return res

    async def initialize_game_instances(self):
        self.load_counting_game()
        for guild_id, instance in self.countingGameInstances.items():
            channel = self.get_channel(int(guild_id), instance["channel"])
            await self.retro_check(instance, channel)
            # await channel.edit(topic=COUNTING_GAME_TOPIC.format(instance["highscore"]))
            await channel.edit(topic="High Score: {}".format(instance["highscore"]))

    # events
    @commands.Cog.listener()
    async def on_ready(self):
        # load data
        await self.initialize_game_instances()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        game_instance = self.countingGameInstances.get(str(message.guild.id))
        if game_instance is not None:
            if is_int(message.content) and message.channel.id == game_instance["channel"]:
                await self.input(game_instance, message)

    # commands
    @commands.command(name="setupCountingGame")
    async def cg_setup(self, ctx):
        """Initialize counting game on a TC
        :param ctx:
        :return:"""
        guild = ctx.guild
        channel = ctx.message.channel
        highscore = 0
        try:
            await channel.edit(topic=COUNTING_GAME_TOPIC.format(highscore))
            instance = {
                "channel": channel.id,
                "last_number": 0,
                "last_player": None,
                "last_message": None,  # message id of the last message
                "highscore": highscore,
                "players": {}  # dict of user ids to number of contributions
            }
            self.countingGameInstances[str(guild.id)] = instance
            # save
            self.save_counting_game()
            await ctx.send("Counting Game setup complete.")
        except:
            await ctx.send("Counting Game setup failed.")

    @commands.command(name="counting_stats")
    async def cg_stats(self, ctx, *args):
        """Returns current game stats"""
        if len(args) == 0:
            member = None
        else:
            member = args[0]
        await ctx.send(self.get_stats(ctx.message.channel, member))

    # TIC TAC TOE
    # Helper functions
    class TicTacToe:
        games = {}

        def __init__(self, message, user):
            self.games[message] = self
            self.board = [0 for _ in range(9)]
            self.player = user
            self.print_board()


        def check_win(self):
            # horizontal test
            for n in range(3):
                check = sum(self.board[n * 3:n * 3 + 3])
                if check == 3:
                    return "X"
                if check == -3:
                    return "O"
            # vertical test
            for n in range(3):
                check = sum(self.board[n:n + 7:3])
                if check == 3:
                    return "X"
                if check == -3:
                    return "O"
            # diagonal test
            d1 = sum(self.board[0:9:4])
            d2 = sum(self.board[2:7:2])
            if d1 == 3 or d2 == 3:
                return "X"
            if d1 == -3 or d2 == -3:
                return "O"
            return "."

        def print_board(self):
            symbols = [" ", "X", "O"]
            chars = []
            res = ""
            for num in self.board:
                chars.append(symbols[num])
            for n in range(3):
                res += " # ".join(chars[n*3:n*3+3])
                if n < 2:
                    res += "\n#########\n"
            return res

    @commands.command(name="tictactoe")
    async def tictactoe(self, ctx):
        """Start a game of tictactoe with the bot"""
        message = await ctx.send("Setting up tictactoe...")
        self.TicTacToe(message, ctx.author)


def setup(bot):
    bot.add_cog(Games(bot))
