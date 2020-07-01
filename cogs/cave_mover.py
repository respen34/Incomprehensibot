import discord
import codecs
from maze import *
from discord.ext import commands


class Cave(commands.Cog):
    cave = None

    def __init__(self, bot):
        self.bot = bot
        print("Cave_Mover initialized")

    @commands.command()
    async def example(self, ctx):
        pass

    @commands.command(name='cave')
    async def cave_game(self, ctx, command=None, *args):
        player = self.lookup_player(ctx.author)
        if command.lower() == 'join':
            # creates a new character if one doesn't already exist
            if args:
                if self.lookup_player(ctx.author):
                    message = 'Player already exists.'
                else:
                    name = ' '.join(args)
                    self.cave.new_player(name[0:min([len(name), 40])], ctx.author)
                    player = self.lookup_player(ctx.author)
                    tile = self.cave.maze[player.coords]
                    # print(cave.players[-1].user)  # debug
                    message = f'Welcome, {name}.'
                    await ctx.author.send(f'Welcome to the cave, {name}.' + '\n' + tile.description(player))
            else:
                message = 'Invalid argument(s). Proper Usage: ~cave join [name]'

            await ctx.send(message)
            return

        if player is None:
            await ctx.send('Create a player first with, ~cave join [name]')
            return

        tile = self.cave.maze[player.coords]
        message = ''
        if command.lower() in ('move', 'go', 'walk', 'run'):
            # move command. args: direction:
            if args:
                direction = args[0].lower()
                directions = {'north': 0, 'east': 1, 'south': 2, 'west': 3,
                              'up': 0, 'right': 1, 'down': 2, 'left': 3}

                if direction in directions:  # checks for a proper direction
                    previous_tile = tile
                    direction_index = directions[direction]
                    message = player.move(direction_index)

                    if previous_tile != self.cave.maze[player.coords]:  # called on successful move
                        # inform players of entrance and departure
                        leave_direction = list(directions.keys())[direction_index]
                        enter_direction = list(directions.keys())[(direction_index + 2) % 4]
                        await self.inform(player, previous_tile,
                                          f'{player.name} went {leave_direction}.')
                        await self.inform(player, self.cave.maze[player.coords],
                                          f'{player.name} entered from the {enter_direction}.')
                        # todo: add entity move calls here{}
                else:
                    message = f'{direction} is not a direction.'

            else:
                message = f'You can move: {", ".join(tile.move_options())}'

        elif command.lower() in ('open', 'loot', 'take'):
            # adds items in container to player's inventory
            # usage: ~cave open {container_name} {item:all} {amount}

            # parse arguments:
            container_name, item, amount = [None for _ in range(3)]
            if len(args) > 0:
                container_name = args[0].lower()
            else:
                for name in ('chest', 'corpse', 'merchant', 'tile'):
                    if name in tile.lootables:
                        container_name = name
                        break

            if len(args) >= 2:
                item = args[1].lower()
            if len(args) >= 3:
                amount = int(args[2])

            # decide result:
            if container_name is not None:
                if container_name in tile.tags:
                    if container_name in tile.lootables:
                        # gets the container object associated with args[0]
                        container = tile.lootables[container_name]

                        loot = container.loot(item, amount)
                        if loot is str:  # fail
                            message = loot

                        else:  # success
                            contents = [f'{loot[n].type} x{loot[n].amount}'
                                        for n in range(len(loot))]

                            for item in loot:
                                player.add_inv(item)

                            message = f'You take: {", ".join(contents)}'

                    else:
                        message = f"You can't loot {container_name}."
                else:
                    message = f"There are no {container_name}s here."  # needs fixing as tile doesn't pass through.
            else:
                message = "There's nothing to loot here."

        elif command.lower() == 'search':
            if 'chest' in tile.lootables:
                # Displays contents of a chest if there is one
                contents = [f'{tile.chest.inv[n].type} x{tile.chest.inv[n].amount}'
                            for n in range(len(tile.chest.inv))]
                if len(contents) == 0:
                    contents = ['Nothing']
                message = f'Chest contains: {", ".join(contents)}'
            else:
                message = 'There is nothing to search.'

        elif command.lower() in ('store', 'place'):
            # adds items in player's inventory to container
            # usage: ~cave store {container_name} {item} {amount}

            # parse arguments:
            container_name, item, amount = [None for _ in range(3)]

            if len(args) > 0:
                container_name = args[0].lower()
            else:
                for name in ('chest', 'corpse', 'merchant', 'tile'):
                    if name in tile.lootables:
                        container_name = name
                        break

            if len(args) >= 2:
                item = args[1].lower()
            if len(args) >= 3:
                amount = int(args[2])

            # decide result:
            if container_name is not None:
                if container_name in tile.tags:
                    if container_name in tile.lootables:
                        # gets the container object associated with args[0]
                        container = tile.lootables[container_name]

                        loot = player.loot(item, amount)
                        if loot is str:  # fail
                            message = f"You don't have any {item}s."

                        else:  # success
                            contents = ", ".join([f'{loot[n].type} x{loot[n].amount}'
                                                  for n in range(len(loot))])
                            for item in loot:
                                container.add_inv(item)

                            if container_name == 'tile':
                                message = f'You throw {contents} on the ground.'
                            else:
                                message = f'You store: {contents} in {container_name}'
                    else:
                        message = f"You can't store in {container_name}."
                else:
                    message = f"There are no {container_name}s here."  # catches 'tile', needs to be fixed.
            else:
                message = "There's no storage here."

        elif command.lower() == 'chest':  # deprecated
            if len(args) > 0:
                if 'chest' in tile.tags:
                    contents = [f'{tile.chest.inv[n].type} x{tile.chest.inv[n].amount}'
                                for n in range(len(tile.chest.inv))]

                    if len(contents) == 0:
                        contents = ['Nothing']
                    if args[0].lower() in ('loot', 'take'):
                        # Loots a chest if there is one.
                        loot = tile.chest.loot()
                        for item in loot:
                            player.add_inv(item)

                        message = f'You found {", ".join(contents)}'

                    elif args[0].lower() in ('open', 'view'):
                        # Displays contents of a chest if there is one
                        message = f'Chest contains: {", ".join(contents)}'

                    elif args[0].lower() in ('store', 'place'):
                        # Stores an item in a chest
                        tile.chest.add_inv(player.inv.pop(player.inv.index(player.search_inv(args[1]))))  # unfinished
                        message = f'You place {args[1]} into the chest'

                else:
                    message = 'There is no chest.'
            else:
                message = 'Invalid argument(s). Proper Usage: ~cave chest [loot:store:open] {args}'

        elif command.lower() in ('inv', 'inventory', 'items'):
            # displays the players inventory
            if len(player.inv) > 0:
                inventory = [f'{n.type} x{n.amount}' for n in player.inv]
                message = f'You have {", ".join(inventory)}'
            else:
                message = 'You have nothing.'

        elif command.lower() == 'use':
            # uses an item from the players inventory
            #
            if args:
                item = player.search_inv(args[0].lower())
                direction_list = ('north', 'east', 'south', 'west',
                                  'up', 'right', 'down', 'left')
                direction = None
                target = None

                if len(args) > 1:
                    if args[1].lower() in direction_list:
                        direction = direction_list[direction_list.index(args[1].lower()) % 4]

                if item:
                    message, information = item.use(player, direction, target)
                    if information:
                        await self.inform(player, tile, information)

                else:
                    message = f"You don't have {args[0].lower()}"

            else:
                message = "Improper usage: ~cave use [item] {direction}"

        elif command.lower() == 'read':
            if args:
                item = player.search_inv(args[0].lower())
                if item and args[0].lower() in Item.readables:
                    message = item.read()
                else:
                    message = tile.read()
            else:
                message = tile.read()

        elif command.lower() == 'write':
            # adds a message to object.messages, defaulting to tile if none given
            if args:
                # parse args
                obj = player.search_inv(args[0].lower())
                if obj and args[0].lower() in Item.readables:
                    message = obj.write(' '.join(args[1:len(args)]))
                else:
                    message = tile.write(' '.join(args))
                    await self.inform(player, tile, f'{player.name} wrote something on the wall.')

        elif command.lower() in ('say', 'talk', 'message', 'tell', 'speak'):
            if len(args) == 0:
                args = ['']
            await self.inform(player, tile, f'{player.name} says, {" ".join(args)}')
            message = f'{" ".join(args)}'

        # Interact with Merchants
        elif command.lower() in ('merchant', 'shop', 'store'):
            print('unfinished')

        else:
            message = 'Invalid command.'

        await ctx.send(message)

    def lookup_player(self, user):
        # finds a player in a maze from the user attribute, returns it's index if found, None otherwise
        for player in self.cave.players:
            if user == player.user:
                return player
        return None

    async def inform(self, player, tile, message):
        # sends message to all players on a tile about what is happening
        players_to_message = tile.players

        if len(players_to_message) > 0:
            for p in players_to_message:
                if player != p:
                    await p.user.send(message)

    # noinspection PyShadowingNames
    @commands.command(name='print_maze')
    async def print_maze(self, ctx):
        maze = self.cave.print_maze()
        # await ctx.send(maze)
        with codecs.open('maze.txt', 'wb') as f:
            f.write(maze.encode('utf-8'))


def setup(bot):
    bot.add_cog(Cave(bot))
