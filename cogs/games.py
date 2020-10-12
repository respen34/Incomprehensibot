import discord
import pickle
import json
import os
import random as r
import math as m
from discord.ext import commands
from utils import *
from abc import ABC, abstractmethod

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
        roles = [get(guild.roles, name=role) for role in ("Counting Champion",
                                                          "Counting Master",
                                                          "Loser")]
        for player_id, stats in instance["players"].items():
            member = get(guild.members, id=int(player_id))
            print("Member: ", member)
            if member is None:
                continue
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
            if member is None:
                continue
            if member != champion and roles[0] in member.roles:
                await member.remove_roles(roles[0])
        if instance["last_number"] > 50:
            if not roles[0] in champion.roles and champion is not None:
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

            # if a milestone has been reached, dispense encouragement
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

    #
    # Other Games
    #
    # Reaction listener
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        for g_type in [self.TicTacToe, self.ConnectFour]:
            game = g_type.games.get(reaction.message.id)
            # print(game)
            if game is not None:
                break
        if game is None:
            return
        if game.vs:
            if (game.player1, game.player2)[game.turn] != user:
                return
        elif game.player1 != user:
            return
        # print("correct game found")
        try:
            move = int(str(reaction)[0]) - 1
        except ValueError:
            return
        # print(move)
        # print(game.get_options())
        await game.player_move(move)

    # Grid games
    class GridGame(ABC):
        games = {}

        def __init__(self, width, height, message, user, user2=None):
            self.message = message
            self.games[message.id] = self
            self.size = self.width, self.height = width, height
            self.board = self.gen_board(self.size)
            self.player1 = user
            self.player2 = user2
            self.vs = False
            if user2 is not None:
                self.vs = True
            self.turn = 0
            self.print_board()

        @abstractmethod
        def gen_board(self, size):
            pass

        @abstractmethod
        def print_board(self):
            pass

        @abstractmethod
        def check_win(self):
            pass

        @abstractmethod
        def get_moves(self):
            pass

        @abstractmethod
        def move(self, index, player):
            pass

        @abstractmethod
        async def comp_move(self):
            pass

        async def player_move(self, index):
            if index not in self.get_moves():
                return
            player_index = (1, -1)[self.turn]
            if self.vs:
                self.move(index, player_index)
                self.turn = (self.turn + 1) % 2
                await self.update_board()
            else:
                self.move(index, 1)
                self.turn = (self.turn + 1) % 2

            # check for game end
            if len(self.get_moves()) == 0:
                await self.end_game()
            elif self.check_win() == '.':
                if not self.vs:
                    await self.comp_move()
            else:
                await self.end_game()

        async def end_game(self):
            await self.update_board()
            win = self.check_win()
            if win == "X":
                if self.vs:
                    await self.message.edit(content=self.player1.mention + " won. I always knew you would win.")
                else:
                    await self.message.edit(content='"Congratulations", you "won".')
            elif win == "O":
                if self.vs:
                    await self.message.edit(content=self.player2.mention + " won, I guess. Good for you bud.")
                else:
                    await self.message.edit(content='HA, I WON! I WON! FUCK YOU, LOSER!')
            else:
                if self.vs:
                    await self.message.edit(content="Wow it's a draw. Thrilling.")
                else:
                    await self.message.edit(content="I didn't lose, so I won!")
            self.games[self.message.id] = None

        async def update_board(self):
            embed = discord.Embed(
                title=self.print_board(),
                color=discord.Color.green()
            )
            if self.vs:
                users = (self.player1, self.player2)
                content = users[self.turn].mention + " is up."
            else:
                content = None
            await self.message.edit(content=content, embed=embed)

    # TIC TAC TOE

    @commands.command(name="tictactoe")
    async def tictactoe(self, ctx):
        """Start a game of tictactoe with the bot"""
        message = await ctx.send("Setting up tictactoe...")
        for emoji in ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣",
                      "6⃣", "7⃣", "8⃣", "9⃣"]:
            await message.add_reaction(emoji)
        if len(ctx.message.mentions) > 0:
            opponent = ctx.message.mentions[0]
        else:
            opponent = None
        game = self.TicTacToe(message, ctx.author, opponent)
        await game.update_board()

    class TicTacToe(GridGame):
        def __init__(self, message, user, user2=None):
            super().__init__(3, 3, message, user, user2)

        def gen_board(self, size):
            return [0 for _ in range(size[0] ** 2)]

        def print_board(self):
            symbols = ["▫", "❌", "⭕"]
            chars = []
            res = ""
            for num in self.board:
                chars.append(symbols[num])
            for n in range(3):
                res += " # ".join(chars[n * 3:n * 3 + 3])
                if n < 2:
                    res += "\n#########\n"
            return res

        def check_win(self):
            # rows and cols
            for n in range(3):
                row_check = sum(self.board[n * 3:n * 3 + 3])
                col_check = sum(self.board[n:n + 7:3])
                if row_check == 3 or col_check == 3:
                    return "X"
                if row_check == -3 or col_check == -3:
                    return "O"

            # diagonal test
            d1 = sum(self.board[0:9:4])
            d2 = sum(self.board[2:7:2])
            if d1 == 3 or d2 == 3:
                return "X"
            if d1 == -3 or d2 == -3:
                return "O"
            return "."

        def get_moves(self):
            res = []
            for i in range(len(self.board)):
                if self.board[i] == 0:
                    res.append(i)
            return res

        def move(self, index, player):
            self.board[index] = player

        async def comp_move(self):
            # check for draw
            if len(self.get_moves()) == 0:
                await self.end_game()
            else:
                # plan and make choice
                options = self.get_moves()
                wins, blocks = self.check_blocking()
                if len(wins) > 0:
                    self.move(r.choice(wins), -1)
                elif len(blocks) > 0:
                    self.move(r.choice(blocks), -1)
                elif 4 in options:
                    self.move(4, -1)
                elif 0 in options:
                    self.move(0, -1)
                else:
                    self.move(r.choice(options), -1)
                # check for win
                if self.check_win() == '.':
                    await self.update_board()
                else:
                    await self.end_game()

        def check_blocking(self):
            index = [0, 1, 2, 3, 4, 5, 6, 7, 8]
            blocks = []
            wins = []
            # row/col tests
            for n in range(3):
                h_check = self.board[n * 3:n * 3 + 3]
                v_check = self.board[n:n + 7:3]
                h_add_to = []
                v_add_to = []

                # horizontal
                if sum(h_check) == 2:
                    h_add_to = blocks
                elif sum(h_check) == -2:
                    h_add_to = wins
                for i in range(3):
                    if h_check[i] == 0:
                        h_add_to.append(index[n * 3:n * 3 + 3][i])
                        break

                # vertical
                if sum(v_check) == 2:
                    v_add_to = blocks
                elif sum(v_check) == -2:
                    v_add_to = wins
                for i in range(3):
                    if v_check[i] == 0:
                        v_add_to.append(index[n:n + 7:3][i])
                        break
            # diagonal test
            for n in range(2):
                check = self.board[2 * n:9 - 2 * n:4 - 2 * n]
                add_to = []
                if sum(check) == 2:
                    add_to = blocks
                elif sum(check) == -2:
                    add_to = wins
                for i in range(3):
                    if check[i] == 0:
                        add_to.append(index[2 * n:9 - 2 * n:4 - 2 * n][i])
                        break
            return wins, blocks

    # Connect Four
    @commands.command(name="connectfour")
    async def start_connect_four(self, ctx):
        message = await ctx.send("Setting up connect four")
        for emoji in ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣",
                      "6⃣", "7⃣"]:
            await message.add_reaction(emoji)
        if len(ctx.message.mentions) > 0:
            opponent = ctx.message.mentions[0]
        else:
            opponent = None
        game = self.ConnectFour(message, ctx.author, opponent)
        await game.update_board()

    class ConnectFour(GridGame):
        def __init__(self, message, user1, user2=None):
            super().__init__(7, 6, message, user1, user2)

        def gen_board(self, size):
            return [[0 for _ in range(size[1])] for n in range(size[0])]

        def print_board(self):
            symbols = ["▫", "🔴", "🟡"]
            res = ""
            for n in range(self.height):
                row = []
                for col in self.board:
                    row.append(col[n])
                res += "| "
                for num in row:
                    res += symbols[num] + " | "
                res += "\n"
            res += "-------------------------------------"
            return res

        def check_win(self):
            # check cols
            for n in range(self.width):
                for i in range(self.height - 4 + 1):
                    check = sum(self.board[n][i:i + 4])
                    if check == 4:
                        return "X"
                    if check == -4:
                        return "O"
            # check rows
            for n in range(self.height):
                for i in range(self.width - 4 + 1):
                    check = []
                    for col in range(4):
                        check.append(self.board[i + col][n])
                    if sum(check) == 4:
                        return "X"
                    if sum(check) == -4:
                        return "O"
            # diagonal test
            for n in range(4):
                for i in range(self.height - 4 + 1):
                    r_check = []
                    l_check = []
                    for d in range(4):
                        r_check.append(self.board[n + d][i + d])
                        l_check.append(self.board[self.width - 1 - n - d][i + d])

                    if sum(r_check) == 4 or sum(l_check) == 4:
                        return "X"
                    if sum(r_check) == -4 or sum(l_check) == -4:
                        return "O"
            return "."

        def get_moves(self):
            res = []
            for i in range(self.width):
                if self.board[i][0] == 0:
                    res.append(i)
            return res

        def move(self, col, player):
            # add move to lowest slot of the column
            row = self.get_bottom_row(col)
            self.board[col][row] = player

        async def comp_move(self):
            # plan and move
            self.move(self.ai(), -1)

            # check for game end
            if len(self.get_moves()) == 0:
                await self.end_game()
            await self.update_board()
            if self.check_win() != '.':
                await self.end_game()

        def ai(self):
            blocks = []
            wins = []
            # test all columns with available moves
            for col in self.get_moves():
                row = self.get_bottom_row(col)
                move_weight = self.check(col, row, 3, 4)
                if move_weight[0]:
                    wins.append(col)
                if move_weight[1]:
                    blocks.append(col)

            if len(wins) > 0:
                print("win")
                return r.choice(wins)
            elif len(blocks) > 0:
                print("block")
                return r.choice(blocks)
            else:
                # plan phase
                safe_moves = []
                for col in self.get_moves():
                    row = self.get_bottom_row(col) - 1
                    move_weight = self.check(col, row, 3, 4)
                    if not move_weight[1]:
                        # experimental
                        if not move_weight[0]:
                            safe_moves.append(col)
                if len(safe_moves) > 0:
                    print("planned:")
                    # check for future blocks/wins
                    blocks = []
                    setups = []
                    both = []
                    for col in safe_moves:
                        row = self.get_bottom_row(col)
                        move_weight = self.check(col, row, 2, 4)
                        if move_weight[0] and move_weight[1]:
                            both.append(col)
                        if move_weight[0]:
                            setups.append(col)
                        if move_weight[1]:
                            blocks.append(col)
                    if len(both) > 0:
                        print("  >block/setup")
                        return r.choice(both)
                    if len(blocks) > 0:
                        print("  >block")
                        """if len(blocks) > 1:
                            for col in blocks:
                                row = self.get_bottom_row(col)
                                move_weight = self.check(col, self.height - 1 - row, 2, 3)
                                if not move_weight[1]:
                                    blocks.remove(col)"""
                        return r.choice(blocks)
                    if len(setups) > 0:
                        print("  >setup")
                        return r.choice(setups)
                    print("  >random")
                    return r.choice(safe_moves)
                else:
                    print("random")
                    return r.choice(self.get_moves())

        def check(self, col, row, count, length):
            # col
            block = False
            win = False
            for y in range(max(row - (length - 1), 0), min(row + length, self.height) - (length - 1)):
                check = sum(self.board[col][y:y + length])
                if check == -count:
                    win = True
                if check == count:
                    block = True
            # row
            for x in range(max(col - (length - 1), 0), min(col + length, self.width) - (length - 1)):
                check = 0
                for i in range(length):
                    check += self.board[x + i][row]
                if check == -count:
                    win = True
                if check == count:
                    block = True
            # right diagonals
            start = -min(col, row, length - 1)
            end = min(self.width - 1 - col, self.height - 1 - row, length - 1) - (length - 2)
            for delta in range(start, end):
                check = 0
                for i in range(length):
                    check += self.board[col + delta + i][row + delta + i]
                if check == -count:
                    win = True
                if check == count:
                    block = True
            # left diagonals
            start = -min(row, self.width - 1 - col, length - 1)
            end = min(col, self.height - 1 - row, length - 1) - (length - 2)
            for delta in range(start, end):
                check = 0
                for i in range(length):
                    check += self.board[col - delta - i][row + delta + i]
                if check == -count:
                    win = True
                if check == count:
                    block = True

            return win, block

        def get_bottom_row(self, col):
            row = 0
            for n in range(self.height):
                row += abs(self.board[col][n])
            return self.height - 1 - row


def setup(bot):
    bot.add_cog(Games(bot))
