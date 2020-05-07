# maze.py version 0.3.07
# rework with a maze dictionary instead of list, player.maze to reference current maze.
import random as r
import math as m


# Super Classes
class Container:

    def __init__(self):
        self.inv = []
        # I want to change this to a dict eventually.

    def contents(self):
        contents = [f'{item.type} x{item.amount}' for item in self.inv]
        return contents

    def add_inv(self, item):
        # adds an item to self.inv appending to the end if it's the first of its type
        item_reference = self.search_inv(item.type)
        if item_reference is not None:
            item_reference.amount += item.amount
        else:
            self.inv.append(item)

    def search_inv(self, item_type):
        # searches self.inv for the first instance of item and returns it returning none if not in the list
        for item in self.inv:
            if item.type == item_type:
                return item
        return None

    def loot(self, item_type=None, amount=None):
        if item_type is None:
            contents = self.inv
            self.inv = []
            return contents
        item = self.search_inv(item_type)
        if item is not None:
            if amount is None:
                amount = item.amount

            if amount >= item.amount or amount == 0:
                return [self.inv.pop(self.inv.index(item))]

            elif item.amount > amount > 0:
                item.amount -= amount
                return [Item(item.type, amount)]

            else:
                return ()

        else:
            return f'There is no {item_type}'


class Item:
    readables = {'book': '', 'tome_of_fire': 'Warning: contents may be hot.',
                 'wormhole_scroll': 'FTL travel in a scroll!', 'map': 'You are here.',
                 'sword': 'Made in china.', 'dagger': 'Made in china.',
                 'health_potion': 'For external use only.', 'gold': 'No cash value.',
                 'match': 'Easy strike matches. Lights every time*(with probability .3)',
                 'bomb': 'Keep out of reach of children.'}

    def __init__(self, item_type, amount, special=None):
        self.type = item_type
        self.amount = amount
        self.special = special

        self.messages = self.readables.get(self.type)

    def write(self, message):
        if self.type in ('book'):
            self.messages += '\n' + message
            return "You write in the book."
        elif self.type in ('tome_of_fire'):
            return "The ink magically runs off the page."
        else:
            return f"You can't write on {self.type}"

    def read(self):
        if self.type in self.readables:
            return f"It says: {self.messages}"
        else:
            return f"There's nothing to read on {self.type}"

    def use(self, player, direction, target):
        tile = player.maze.maze[player.coords]
        inform = None

        if self.type in ('map'):
            radius = 2 * min(self.amount - 1, 10) + 1
            x, y = tile.coords
            maze = player.maze.print_maze(y + radius, y - radius, x - radius, x + radius)
            message = f"You're at: {player.coords}" + '\n' + maze

        elif self.type in ('sword'):  # cornwall found the first one after 1000 tiles, I found the second after 8.
            messages = ('Do you like my sword?', 'I can swing my sword!',
                        'I have the power of god and anime on my side!')
            message = r.choice(messages)

        elif self.type in ('dagger'):
            messages = ('Stab, stab, stab.', 'I draw my double daggers and attack the nearest enemy.')
            message = r.choice(messages)

        elif self.type in ('match'):
            self.amount -= 1
            if self.amount <= 0:
                player.inv.remove(self)
            message = r.choice(("It sparks but doesn't light.", "You light a match.", "The match breaks."))
            if 'gas' in tile.tags and 'light' in message:
                message += '\nThe room is engulfed in a fireball.\n' + player.damage(50)
                inform = 'The room is engulfed in a fireball.\n'
                tile.tags.remove('gas')

        elif self.type in ('rope'):
            player.damage(100)
            message = "You hang yourself."
            inform = f"{player.name} hanged themself."

        elif self.type in ('health_potion'):
            self.amount -= 1
            player.health = min(player.health + 50, 125)
            if player.health > 100:
                message = "You feel better than ever."
            else:
                message = "You feel better."

        elif self.type in ('wormhole_scroll'):
            coords = (player.coords[0] + r.randint(-1, 1) * r.randint(10, 50),
                      player.coords[1] + r.randint(-1, 1) * r.randint(10, 50))
            player.tile.players.remove(player)
            if coords in player.maze.maze:
                player.coords = coords
                player.tile = player.maze.maze[coords]
            else:
                player.coords = coords
                player.maze.maze[coords] = Tile(r.randint(0, 14), coords, [(coords[0] + n, coords[1] + m)
                                                                           for n, m in
                                                                           ((0, 1), (1, 0), (0, -1), (-1, 0))],
                                                len(player.maze.maze))
                player.tile = player.maze.maze[coords]

                player.tile.players.append(player)
            message = 'You are teleported far away.\n' + player.tile.description(player)
            inform = f'{player.name} disappeared.'

        elif self.type in ('bomb'):
            match = player.search_inv('match')
            if match:
                match.amount -= 1
                if match.amount <= 0:
                    player.inv.remove(match)

                self.amount -= 1
                if self.amount <= 0:
                    player.inv.remove(self)

                if direction:  # blow up wall
                    direction_index = ('north', 'east', 'south', 'west').index(direction)
                    tile_list = [tile]
                    reference_tile = player.maze.maze.get(tile.reference[direction_index])
                    if reference_tile:
                        tile_list.append(reference_tile)

                    for tile in tile_list:
                        option_list = [d for d in player.maze.tileTypes[tile.type]]
                        if not option_list[direction_index]:
                            option_list[direction_index] = True
                        tile.type = player.maze.tileTypes.index(tuple(option_list))
                        direction_index = (direction_index + 2) % 4

                    message = f'You blow up the {direction} wall.'
                    inform = f'{player.name} blew up the {direction} wall.'

                    if 'gas' in tile.tags:
                        message += '\nThe room is ingulfed in a fireball.\n' + player.damage(50)
                        tile.tags.remove('gas')
                        inform += '\nThe room is ingulfed in a fireball.\n'

                else:  # bomb attack: todo, a more robust aiming system also damaging other players and enemies.
                    message = 'The bomb goes off in the middle of the room.\n' + player.damage(50)
                    inform += 'The bomb goes off in the middle of the room.\n'
            else:  # no matches
                message = 'You need matches to light the fuse.'

        else:
            message = 'This is an unfinished item, it will have a use soon ;)\
            \nIf you have an idea for a use for this item, let me know and I might add it.'

        return message, inform


#
# Entity Objects
#
class Player(Container):
    # basic player object for interacting with maze class
    def __init__(self, name, *, health=100, level=1, coords=(0, 0), user=None, maze=None, tile=None):
        super().__init__()
        self.name = name

        self.coords = coords
        self.health = health
        self.level = level

        self.inv = [Item('map', 1), Item('bomb', 1), Item('wormhole_scroll', 1)]  # temporary starting inv

        self.user = user
        self.maze = maze  # the associated maze object
        self.tile = tile

        self.pets = []

    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            return self.kill()
        elif self.health <= 25:
            return "You are seriously injured."
        elif self.health <= 50:
            return "You are wounded."
        elif self.health <= 75:
            return "You are hurt."
        elif self.health <= 100:
            return "You barely felt that."
        else:
            return "You feel fine."

    def kill(self):
        self.user = None
        self.tile.lootables['corpse'] = self
        self.tile.tags.append('corpse')
        self.tile.corpse = self
        self.tile.players.remove(self)
        self.maze.players.remove(self)
        return "You are dead."

    def add_exp(self, amount):
        # amount: int, the amount of exp to add
        # level up every 100 exp
        old = m.floor(self.level)
        self.level += amount / 100
        if old != m.floor(self.level):
            return f"Level up! New level:{m.floor(self.level)}"
        return ''

    def move(self, direction):
        # direction: int between 0 and 3 in [left, up, right, down]
        tile = self.maze.maze[self.coords]
        message = []

        if self.maze.tileTypes[tile.type][direction]:
            reference_coords = tile.reference[direction]

            if reference_coords in self.maze.maze:
                new_tile = self.maze.maze[reference_coords]

                if self.maze.tileTypes[new_tile.type][(direction + 2) % 4]:  # move success, old tile

                    self.coords = reference_coords
                    new_tile.players.append(tile.players.pop(tile.players.index(self)))

                    message.append(new_tile.description(self))

                else:  # move failed, path blocked
                    # update type
                    move_options = [d for d in self.maze.tileTypes[tile.type]]
                    move_options[direction] = False
                    tile.type = self.maze.tileTypes.index(tuple(move_options))

                    message.append('You found a cave-in. You will have to go another way.')

            else:  # move success, new tile
                self.coords = self.maze.generate_next(direction, self.coords)
                new_tile = self.maze.maze[self.coords]

                new_tile.players.append(tile.players.pop(tile.players.index(self)))
                exp = self.add_exp(1)
                message.append('You move into the darkness...')
                if exp:
                    message.append(exp)
                message.append(new_tile.description(self))
        else:  # move failed, direction not an option
            message.append("You can't go that way.")
        self.tile = self.maze.maze[self.coords]
        return "\n".join(message)


class Enemy(Container):  # new addition, needs testing, needs ai, possible genetic learning during play_next.
    def __init__(self, enemy_type, tile):
        super().__init__()
        self.type = enemy_type
        self.tile = tile
        stat_dict = {'mimic': [50, 4, 2, 4, 0, self.bite]}
        default = [100, 3, 3, 3, 0, self.bite]  # hp, str, dex, con, lck, *abilities
        self.stats = stat_dict.get(self.type, default)

        self.target = None
        self.mood = 0

    # attacks
    def bite(self):
        # dmg: 5 * str +- 5
        message = f"{self.type} used bite"
        return message + '/n' + self.target.damage(5 * self.stats[1] + r.randrange(-5, 5))


#
# Tile Objects
#
class Tile(Container):
    # basic object holding the state of a tile of the maze
    def __init__(self, tile_type, coords, reference_list, number, is_exit=False, probabilities=()):
        """tileType: an integer representing the shape of the tile
        coords: a 2-tuple representing the global position on the maze dict
        reference_list(legacy): a list of references to adjacent tile
        probabilities(unused): list of probabilities of special types"""

        super().__init__()
        self.type = tile_type
        self.coords = coords
        self.reference = reference_list  # list of coords of adjacent tiles
        self.number = number

        self.players = []
        self.messages = []  # List of message strings

        self.lootables = {'tile': self}  # Dict of lootable objects on the tile
        self.enemies = []
        # self.inv = []
        self.corpse = None

        self.tags = []

        if self.type <= 3 and r.random() <= .95:
            self.chest = Chest()
            self.tags.append('chest')
            self.lootables[
                'chest'] = self.chest  # possible option to prevent looting of non-lootable special conditions
        elif self.type <= 3:
            self.chest = Chest()
            self.tags.append('chest')
            self.tags.append('mimic')

        if self.type in (10, 11, 12, 13) and r.random() <= .025:
            self.tags.append('merchant')
            self.merchant = Merchant()

        if r.random() <= .01:
            self.tags.append('gas')

        if self.type in (4, 5) and r.random() <= .01:
            self.tags.append('pit-norope')

        if self.type == 14 and r.random() <= .01:
            self.tags.append('firepit-unlit')

    def move_options(self):
        tile = Maze.tileTypes[self.type]
        direction_list = ['north', 'east', 'south', 'west']
        options = [direction_list[n] for n in range(4) if tile[n]]
        return options

    def write(self, message):
        self.messages.append(message)
        return "You write your message on the wall."

    def read(self):
        if len(self.messages) == 0:
            return "It says nothing."
        else:
            return 'It says: ' + '\n'.join(self.messages)

    def description(self, player):
        # unfinished
        if 'corpse' in self.tags:
            corpse_name = self.corpse.name
        else:
            corpse_name = ''
        if 'chest' in self.tags:
            chest_type = self.chest.type
        else:
            chest_type = ''

        descriptions = {'chest': f"There's a {chest_type} chest.",
                        'merchant': "It seems a merchant has set up shop here.",
                        'gas': "Something smells funny.",
                        'corpse': f"You found {corpse_name}'s body.",
                        'pit-norope': "A bottomless pit blocks your path.",
                        'pit-rope': "A rope hangs over a bottomless pit.",
                        'firepit-unlit': "There's an unlit campfire here.",
                        'firepit-lit': "A campfire burns brightly in this room."}

        messages = []
        for tag in self.tags:
            messages.append(descriptions.get(tag, f'There is a {tag}.'))

        if self.messages:
            messages.append("There's writing on the wall.")

        if len(self.players) > 1:
            players = [p.name for p in self.players if p != player]

            if len(players) >= 2:
                messages.append(f'You see {", ".join(players[0:-2])} and {players[-1]}')

            else:
                messages.append(f'You see {", ".join(players)}')

        messages.append(f'You can move: {", ".join(self.move_options())}')

        return '\n'.join(messages)


class Chest(Container):
    def __init__(self):
        super().__init__()
        self.name = 'chest'
        self.wood_loot_table = [Item('gold', r.randint(1, 10)),
                                Item('rope', r.randint(1, 2)),
                                Item('bomb', 1),
                                Item('match', r.randint(1, 3)),
                                Item('health_potion', 1),
                                Item('book', 1),
                                Item('map', 1),
                                Item('key', 1)]

        self.iron_loot_table = [Item('gold', r.randint(10, 20)),
                                Item('rope', r.randint(3, 5)),
                                Item('bomb', r.randint(2, 3)),
                                Item('match', r.randint(3, 5)),
                                Item('health_potion', r.randint(2, 3)),
                                Item('book', 2),
                                Item('chain_shirt', 1),
                                Item('arrow', r.randint(2, 6)),
                                Item('dagger', r.randint(1, 2))]

        self.gold_loot_table = [Item('gold', r.randint(50, 100)),
                                Item('bomb', 4),
                                Item('health_potion', r.randint(4, 5)),
                                Item('tome_of_fire', 1),
                                Item('wormhole_scroll', 1),
                                Item('sword', 1),
                                Item('helmet', 1),
                                Item('tower_shield', 1),
                                Item('circle_shield', 1),
                                Item('bow', 1)]

        amount = r.choices((1, 2, 3, 4), [0.75, 0.125, 0.0625, 0.03])[0]
        index = r.choices([0, 1, 2], [0.85, 0.14, 0.01])[0]
        self.loot_table = [self.wood_loot_table, self.iron_loot_table, self.gold_loot_table][index]
        self.type = ('wood', 'iron', 'gold')[index]
        self.inv = r.choices(self.loot_table, k=amount)


class Merchant(Container):
    def __init__(self):
        super().__init__()
        self.inv = [Item('gold', 500),
                    Item('map', 5),
                    Item('match', 30),
                    Item('health_potion', 5),
                    Item('bomb', 5),
                    Item('rope', 10)]
        self.name = 'merchant'
        self.mood = r.random()  # value between -1 and 1 represents agreeableness 1 being agreeable -1 being aggressive
        # will affect the bartering system: .5 is the default value

        self.cost = {'gold': 1, 'map': 30 - round(5 * self.mood), 'match': 2 - round(self.mood),
                     'bomb': 15 - round(3 * self.mood),
                     'rope': 5 - round(2 * self.mood), 'sword': 50 - round(7 * self.mood)}

    def buy(self, player, item_type, amount=None, offer=None):
        item = self.search_inv(item_type)
        if item:
            if offer is None:
                if item.amount >= int(amount) > 0:
                    # buy at listed price
                    print('unfinished')

                else:
                    message = f"I don't have that much, I only have {item.amount}."
                    self.mood = max(0.0, self.mood - .05)

            else:
                # when offer is given, mood determines whether it will be accepted, rejected or countered.
                print('unfinished')

        else:
            message = f"I don't have {item_type}."
            self.mood = max(0, self.mood - .05)


class Maze:
    """#######################################################
        A maze that grows as players explore it a la Subterra
        length: after how many tiles should it generate a new layer
        difficulty and probabilities: extra parameters to be implemented later
       #######################################################"""
    # (left dead, right dead, up dead, down dead,
    tileTypes = ((False, False, False, True), (False, True, False, False), (True, False, False, False),
                 (False, False, True, False), (False, True, False, True), (True, False, True, False),
                 (True, False, False, True), (True, True, False, False), (False, False, True, True),
                 (False, True, True, False), (True, False, True, True), (True, True, True, False),
                 (True, True, False, True), (False, True, True, True), (True, True, True, True))

    tileCharacters = (u'\u2561', u'\u255e', u'\u2568',
                      u'\u2565', u'\u2550', u'\u2551',
                      u'\u255d', u'\u255a', u'\u2557',
                      u'\u2554', u'\u2563', u'\u2560',
                      u'\u2569', u'\u2566', u'\u256c')

    def __init__(self, length=1000, difficulty=None, probabilities=None):
        self.len = length
        self.players = []
        self.maze = {(0, 0): Tile(14, (0, 0), [(0, 1), (1, 0), (0, -1), (-1, 0)], 0)}

    def generate_next(self, direction, old_coords):
        tile = self.maze[old_coords]
        coords = tile.reference[direction]

        reference_list = [(coords[0] + n, coords[1] + m)
                          for n, m in ((0, 1), (1, 0), (0, -1), (-1, 0))]
        inverse_direction = reference_list.index(old_coords)
        if self.tileTypes[tile.type][direction]:
            tile_options = [n for n in range(15)
                            if self.tileTypes[n][inverse_direction]]
        else:
            tile_options = [n for n in range(15)]

        for d in range(4):
            ref = self.maze.get(reference_list[d])
            if ref:
                is_ref_clear = self.tileTypes[ref.type][(d + 2) % 4]
                print(is_ref_clear)
                if not is_ref_clear:
                    n = 0
                    while n < len(tile_options):
                        op = tile_options[n]
                        if self.tileTypes[op][d]:
                            tile_options.remove(op)
                            print(f'{op} removed')
                        else:
                            n += 1

        tile_type = r.choice(tile_options)
        print(tile_options)
        self.maze[coords] = Tile(tile_type, coords, reference_list, len(self.maze))
        return coords

    def new_player(self, name, user=None):
        self.players.append(Player(name, user=user, maze=self, tile=self.maze[(0, 0)]))
        player = self.players[len(self.players) - 1]
        self.maze[player.coords].players.append(player)

    def print_maze(self, top=0, bottom=0, left=0, right=0):
        maze = ''
        if (top, bottom, left, right) == (0, 0, 0, 0):
            for tile in list(self.maze.values()):
                if tile.coords[0] < left:
                    left = tile.coords[0]

                if tile.coords[0] > right:
                    right = tile.coords[0]

                if tile.coords[1] > top:
                    top = tile.coords[1]

                if tile.coords[1] < bottom:
                    bottom = tile.coords[1]

        for h in range(top, bottom - 1, -1):
            for w in range(left, right + 1):
                coords = (w, h)
                if coords in self.maze:
                    maze += self.tileCharacters[self.maze[coords].type]
                else:
                    maze += u'\u2592'
            maze += '\n'
        return maze
