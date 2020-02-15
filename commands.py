#commands.py version 1.1.02
import json
players = []
save_on = False #save still broken, something with the maze dict not reinitiallizing properly

@bot.event
async def on_ready():
    print(f'{bot.user.name} is connected to the discord!')
    #loadData()
    await initialize_counting_game()
    await fanny_pack_friday()
    print('This is test text')



@bot.event
async def on_message_delete(message):
    guild = get_channel("Incomprehensible Games", "the-pentagon").guild
    if not message.author.bot:
        if message.guild == guild:
            channel = get_channel("Incomprehensible Games", "for-the-record")
            await channel.send(f"{message.author.name}: {message.content}")
            await channel.send(message.author.mention)



@bot.event
async def on_message(message):
    path = f'{dataPath}{message.author.name}.data'
    data = {}
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
    for word in message.content.split(' '):
        if word in data:
            data[word] += 1
        else:
            data[word] = 1
    with open(path, 'w') as f:
        json.dump(data, f)
        
    await bot.process_commands(message)



    ###################
    #  text commands  #
    ###################

@bot.command(name='random')
async def randomwords(ctx, number: int =1, List='r'):
    if List == 'r':
        response = [
            Random_Three_Words.metawords()
            for _ in range(number)
        ]
    elif List == 'c':
        response = [
            Cards_List.metawords()
            for _ in range(number)
        ]
    elif List == 't':
        response = [
            Official_Three_Words.metawords()
            for _ in range(number)
        ]
    else:
        response = []
    await ctx.send('\n'.join(response))

@bot.command(name='add')
async def addword(ctx, word):
    global dataPath
    with open(f'{dataPath}randwords.txt','a') as f:
        f.write(f'\n{word}')
        Random_Three_Words.load('randwords.txt')
    await ctx.send(f'Added: {word}.')

@bot.command(name='fpf')
async def fpf(ctx):
    await ctx.send(f'Only {int(next_friday())} more seconds until the next fanny pack friday')

@bot.command(name='message')
async def post(ctx, message, guild, channel):
    if ctx.author.name == "respen34":
        guild = discord.utils.get(bot.guilds, name=guild)
        channel = discord.utils.get(guild.channels, name=channel)
        await channel.send(message)





    ####################
    #  music commands  #
    ####################

@bot.command(name='join')
async def join(ctx):
    await new_player(ctx)

@bot.command(name='leave')
async def leave(ctx):
    player = get_player(ctx.guild)
    if player:
        response = 'Alright fine! I see how it is.'
        voice = players.pop(players.index(player))
        await voice.voice_client.disconnect()
    else:
        response = 'I have to be somewhere before I can leave you dunce!'
    await ctx.send(response, delete_after=60)

@bot.command(name='play')
async def playAudio(ctx, source=None, ftype='yt'):
    if ctx.author.voice.channel != None:
        if ctx.me.voice == None:
            await new_player(ctx)
        player = get_player(ctx.guild)
        if source:
            source = identifySource(source, ftype)
            if not(player.voice_client.is_playing()):
                player.play(source)
            else:
                player.addsong(source)
        elif player.autoplay:
            player.AutoPlay()
    else:
       await ctx.send('User is not in a voice channel, please join one and try again.')

@bot.command(name='pause')
async def pause(ctx):
    player = get_player(ctx.guild)
    if player:
        voice = player.voice_client
        if voice.is_playing():
            voice.pause()
            response = 'The player has been paused.'
        elif voice.is_paused():
            voice.resume()
            response = 'The player has been unpaused.'
        else:
            response = 'The playlist is empty.'
    else:
        response = "Wait a minute, I'm not even in voice. What'r you tryin' to pull here?"
    await ctx.send(response)

@bot.command(name='stop')
async def stop(ctx):
    player = get_player(ctx.guild)
    if player:
        player.voice_client.stop()
        await player.voice_client.disconnect()
    else:
        await ctx.send("You can't stop what you didn't start!")

@bot.command(name='skip')
async def skip(ctx):
    player = get_player(ctx.guild)
    if player:
        player.skip()

@bot.command(name='list')
async def playlist(ctx):
    player = get_player(ctx.guild)
    if player:
        response = str(player.playlist)
    else:
        response = "There is no playlist, because YOU DIDN'T INVITE ME!"
    await ctx.send(response)

@bot.command(name='autoplay')
async def Toggle_auto_play(ctx):
    player = get_player(ctx.guild)
    if player:
        player.autoplay = not(player.autoplay)
        await ctx.send(f'Autoplay set to {player.autoplay}')

@bot.command(name='repeat')
async def toggle_repeat(ctx):
    player = get_player(ctx.guild)
    if player:
        player.repeat = not(player.repeat)
        await ctx.send(f'Repeat mode: {player.repeat}.')

def identifySource(source, ftype='yt'):
    #tags the source input with characters telling the player what to do with them
    if ftype == 'yt' and 'youtube.com/watch?v=' in source:
        return((source, 'yt'))
    elif ftype == 'f' or (('.mp3' in source or '.flac' in source
                        or '.wav' in source or '.m4a' in source
                        or '.cda' in source) and ':\\' in source):
        return((source,'f'))
    else:
        return((source, 's'))

def get_player(guild):
    #returns the player running in the clients server, returning none if none is found
    for p in players:
       if p.voice_client.guild == guild:
           return(p)
    return(None)

async def new_player(ctx):
    if get_player(ctx.guild) == None:
        players.append(audioPlayer())
        await players[len(players)-1].join(ctx)
        return('New player initialized')
    else:
        return('Player already exists')




    #######################
    #  special functions  #
    #######################

def get_channel(guild, channel):
    guild = discord.utils.get(bot.guilds, name=guild)
    channel = discord.utils.get(guild.channels, name=channel)
    return(channel)

def next_friday():
    #returns the number of seconds until 1pm on the closest friday
    today = datetime.datetime.today()

    if today.weekday() == 4 and today.hour > 13 or (today.hour == 13 and (today.minute > 0 or today.second > 0)):
        day = 7
    else:
        day = (-today.weekday()-3)%7

    friday = datetime.datetime(today.year, today.month, today.day, 13, 0, 0, 0) + datetime.timedelta(days= day)
    return((friday - today).total_seconds())


async def fanny_pack_friday():
    #prints fanny pack friday meme once every friday at 1pm cst
    delay = next_friday()
    print(f'{delay} seconds until the next fanny pack friday!')
    await asyncio.sleep(delay)
    guild = discord.utils.get(bot.guilds, name='Incomprehensible Games')
    channel = discord.utils.get(guild.channels, name='image-surveillance')
    await channel.send('It is fanny pack friday!', file=discord.File(r'C:\Users\respen34\Videos\I miss you clifford.mp4'))
    print('I gotta tell ya, I just feel super about it.')
    await asyncio.sleep(10)
    await fanny_pack_friday()




    ###################
    #  Counting_Game  #
    ###################

@bot.command(name='#')
async def countingGame(ctx, number:int):
    global count
    topic, message = count.input(ctx, number)
    channel = get_channel(count.channel[0],count.channel[1])
    if topic:
        await channel.edit(topic = topic)
    if message:
        await ctx.send(message)
    with open(f'{dataPath}countinggame.dat', 'w+b') as file:
        pickle.dump(count, file)

async def initialize_counting_game():
    global count
    with open(f'{dataPath}countinggame.dat', 'r+b') as file:
        count = pickle.load(file)
    channel = get_channel(count.channel[0],count.channel[1])
    topic = channel.topic
    high_score = int(topic[11:len(topic)])
    async for message in channel.history(limit=20):
        if '~# ' in message.content:
            count_index = int(message.content[3:len(message.content)])
            last_player = message.author.name
            break
    if count_index > count.count_index:
        count.count_index = count_index
        count.last_player = last_player
        if count.count_index > count.high_score:
            count.high_score = count.count_index
    if count.high_score > high_score:
        await channel.edit(topic = f'highscore: {count.high_score}')

    with open(f'{dataPath}countinggame.dat', 'w+b') as file:
        pickle.dump(count, file)

class CountingGame():
    def __init__(self, guild, channel):
        self.count_index = 0
        self.high_score = 0
        self.last_player = None
        self.channel = (guild, channel)

    def input(self, ctx, number):
        channel = get_channel(self.channel[0],self.channel[1])
        last = discord.utils.get(channel.guild.members, name=self.last_player)
        if ctx.author != last and number == self.count_index + 1:
            self.count_index += 1
            self.last_player = ctx.author.name

            if self.count_index > self.high_score:
                self.high_score = self.count_index
                return(f'highscore: {self.high_score}', None)
            else:
                return(None,None)
        else:
            self.count_index = 0
            self.last_player = None
            message = f"Nice job, {ctx.author.name}, you ruined it."
            if self.high_score == self.count_index:
                message += f"\nNew high score: {high_score}"
            return(None, message)




    #####################
    #  Cave_Mover Game  #
    #####################

cave = None

@bot.command(name='cave')
async def Cave_Game(ctx, command=None, *args):
    player = lookup_player(ctx.author)
    if player == None and command.lower() != 'join':
        message = 'Create a player first with, ~cave join [name]'

    else:
        if player != None:
            tile = cave.maze[player.coords]



        if command.lower() == 'join':
            #creates a new character if one doesn't already exist
            if args:
                if lookup_player(ctx.author):
                    message = 'Player already exists.'
                else:
                    name = ' '.join(args)
                    cave.new_player(name[0:min([len(name),40])], ctx.author)
                    player = lookup_player(ctx.author)
                    tile = cave.maze[player.coords]
                    #print(cave.players[-1].user)
                    message = f'Welcome, {name}.'
                    await ctx.author.send(f'Welcome to the cave, {name}.' + '\n' + tile.description(player))
            else:
                message = 'Invalid argument(s). Proper Usage: ~cave join [name]'



        elif command.lower() in ('move','go','walk','run'):
            #move command. args: direction:
            if args:
                direction = args[0].lower()
                directions = {'north':0,'east':1,'south':2,'west':3,
                            'up':0, 'right':1, 'down':2, 'left':3}

                if direction in directions: #checks for a proper direction
                    previousTile = tile
                    directionIndex = directions[direction]
                    message = player.move(directionIndex)

                    if previousTile != cave.maze[player.coords]:#called on successful move
                        #inform players of enterance and departure
                        await inform(player, previousTile, f'{player.name} went {list(directions.keys())[directionIndex]}.')
                        await inform(player, cave.maze[player.coords], f'{player.name} entered from the {list(directions.keys())[(directionIndex + 2) % 4]}.')
                    #add entity move calls here{}
                else:
                    message = f'{direction} is not a direction.'

            else:
                message = f'You can move: {", ".join(tile.move_options())}'



        elif command.lower() in ('open', 'loot', 'take'):
            #adds items in container to player's inventory
            #usage: ~cave open {containerName} {item:all} {amount}

            #parse arguments:
            containerName, item, amount = [None for _ in range(3)]
            if len(args) > 0:
                containerName = args[0].lower()
            else:
                for name in ('chest', 'corpse', 'merchant', 'tile'):
                    if name in tile.lootables:
                        containerName = name
                        break

            if len(args) >= 2:
                item = args[1].lower()
            if len(args) >= 3:
                amount = int(args[2])



            #decide result:
            if containerName is not None:
                if containerName in tile.tags:
                    if containerName in tile.lootables:
                        #gets the container object associated with args[0]
                        container = tile.lootables[containerName]

                        loot = container.loot(item, amount)
                        if loot is str:#fail
                            message = loot

                        else:#success
                            contents = [f'{loot[n].type} x{loot[n].amount}'
                                        for n in range(len(loot))]

                            for item in loot:
                                player.add_inv(item)

                            message = f'You take: {", ".join(contents)}'

                    else:
                        message = f"You can't loot {containerName}."
                else:
                    message = f"There are no {containerName}s here." #needs fixing as tile doesn't pass through.
            else:
                message = "There's nothing to loot here."



        elif command.lower() in ('search'):
            if 'chest' in tile.lootables:
                    #Displays contents of a chest if there is one
                    contents = [f'{tile.chest.inv[n].type} x{tile.chest.inv[n].amount}'
                                for n in range(len(tile.chest.inv))]
                    if len(contents) == 0:
                        contents = ['Nothing']
                    message = f'Chest contains: {", ".join(contents)}'
            else:
                message = 'There is nothing to search.'




        elif command.lower() in ('store', 'place'):
            #adds items in player's inventory to container
            #usage: ~cave store {containerName} {item} {amount}

            #parse arguments:
            containerName, item, amount = [None for _ in range(3)]
            
            if len(args) > 0:
                containerName = args[0].lower()
            else:
                for name in ('chest', 'corpse', 'merchant', 'tile'):
                    if name in tile.lootables:
                        containerName = name
                        break

            if len(args) >= 2:
                item = args[1].lower()
            if len(args) >= 3:
                amount = int(args[2])

            #decide result:
            if containerName is not None:
                if containerName in tile.tags:
                    if containerName in tile.lootables:
                        #gets the container object associated with args[0]
                        container = tile.lootables[containerName]

                        loot = player.loot(item, amount)
                        if loot is str:#fail
                            message = f"You don't have any {item}s."

                        else:#success
                            contents = ", ".join([f'{loot[n].type} x{loot[n].amount}'
                                        for n in range(len(loot))])
                            for item in loot:
                                container.add_inv(item)

                            if containerName == 'tile':
                                message = f'You throw {contents} on the ground.'
                            else:
                                message = f'You store: {contents} in {containerName}'
                    else:
                        message = f"You can't store in {containerName}."
                else:
                    message = f"There are no {containerName}s here."#catches 'tile', needs to be fixed.
            else:
                message = "There's no storage here."



        elif command.lower() in ('chest'): #depricated
            if len(args) > 0:
                if 'chest' in tile.tags:
                    contents = [f'{tile.chest.inv[n].type} x{tile.chest.inv[n].amount}'
                                for n in range(len(tile.chest.inv))]

                    if len(contents) == 0:
                        contents = ['Nothing']
                    if args[0].lower() in ('loot', 'take'):
                        #Loots a chest if there is one.
                        loot = tile.chest.loot()
                        for item in loot:
                            player.add_inv(item)

                        message = f'You found {", ".join(contents)}'

                    elif args[0].lower() in ('open', 'view'):
                        #Displays contents of a chest if there is one
                        message = f'Chest contains: {", ".join(contents)}'

                    elif args[0].lower() in ('store', 'place'):
                        #Stores an item in a chest
                        tile.chest.add_inv(player.inv.pop(player.inv.index(player.search_inv(args[1])))) #unfinished
                        message = f'You place {args[1]} into the chest'

                else:
                    message = 'There is no chest.'
            else:
                message = 'Invalid argument(s). Proper Usage: ~cave chest [loot:store:open] {args}'




        elif command.lower() in ('inv', 'inventory', 'items'):
            #displays the players inventory
            if len(player.inv) > 0:
                inventory = [f'{n.type} x{n.amount}' for n in player.inv]
                message = f'You have {", ".join(inventory)}'
            else:
                message = 'You have nothing.'




        elif command.lower() in ('use'):
            #uses an item from the players inventory
            #
            if args:
                item = player.search_inv(args[0].lower())
                directionList = ('north', 'east', 'south', 'west',
                                 'up', 'right', 'down', 'left')
                direction = None
                target = None

                if len(args) > 1:
                    if args[1].lower() in directionList:
                        direction = directionList[directionList.index(args[1].lower()) % 4]

                if item:
                    message, information = item.use(player, direction, target)
                    if information:
                        await inform(player,tile,information)

                else:
                    message = f"You don't have {args[0].lower()}"

            else:
                message = "Improper usage: ~cave use [item] {direction}"



        elif command.lower() in ('read'):
            if args:
                item = player.search_inv(args[0].lower())
                if item and args[0].lower() in Item.readables:
                    message = item.read()
                else:
                    message = tile.read()
            else:
                message = tile.read()


        elif command.lower() in ('write'):
            #adds a message to object.messages, defaulting to tile if none given
            if args:
                #parse args
                obj = player.search_inv(args[0].lower())
                if obj and args[0].lower() in Item.readables:
                    message = obj.write(' '.join(args[1:len(args)]))
                else:
                    message = tile.write(' '.join(args))
                    await inform(player, tile, f'{player.name} wrote something on the wall.')


        elif command.lower() in ('say', 'talk', 'message', 'tell', 'speak'):
            if len(args) == 0:
                args = ['']
            await inform(player, tile, f'{player.name} says, {" ".join(args)}')
            message = f'{" ".join(args)}'


        #Interact with Merchants
        elif command.lower() in ('merchant', 'shop', 'store'):
            print('unfinished')


        else:
            message = 'Invalid command.'

        await ctx.send(message)

        if save_on:#save state to file
            saveData()


def lookup_player(user):
    #finds a player in a maze from the user attribute, returns it's index if found, None otherwise
    for player in cave.players:
        if user == player.user:
            return(player)
    return(None)


async def inform(player, tile, message):
    #sends message to all players on a tile about what is happening
    players = tile.players

    if len(players) > 0:
        for p in players:
            if player != p:
                await p.user.send(message)
 


@bot.command(name='print_maze')
async def printmaze(ctx):
    maze = cave.print_maze()
    #await ctx.send(maze)
    with codecs.open('maze.txt', 'wb') as f:
            f.write(maze.encode('utf-8'))





def saveData():#save the state of the game
    users = [player.user for player in cave.players]
    for player in cave.players:
        player.user = player.user.name
    with open(f'{dataPath}cave.dat', 'w') as f:
        f.write(jsonpickle.encode(cave))
    n = 0
    for user in users:
        cave.players[n].user = user
        n += 1
    print(cave.players)
    for player in cave.players:
        print(player.user)




def loadData():
    global cave
    with open(f'{dataPath}cave.dat', 'r') as f:
        cave = jsonpickle.decode(f.read())
    for player in cave.players:
        for guild in bot.guilds:
            user = discord.utils.get(guild.members, name=player.user)
            if user:
                player.user = user
                print(user)




if os.path.exists(f'{dataPath}cave.dat'):
    loadData()

else:
    cave = maze()
    if save_on:
        with open(f'{dataPath}cave.dat', 'x') as f:
            print("new cave initialized")
        saveData()


    ############################
    #  Cards Against Humanity  #
    ############################

