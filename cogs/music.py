import discord
import audio_player
import os
from discord.ext import commands
import asyncio


class Music(commands.Cog):
    music_players = {}
    timeout_check = 60 * 5  # time to wait between timeout tests in seconds

    def __init__(self, bot):
        self.bot = bot
        self.timeout_is_running = False
        print("Music initialized")

    async def new_player(self, ctx):
        # bot connects to the voice client of the user who executed the command and creates a new playlist instance
        self.music_players[ctx.guild] = audio_player.Playlist(await ctx.author.voice.channel.connect())
        # start timeout loop if not running
        if not self.timeout_is_running:
            self.timeout_is_running = True
            await self.timeout_loop()

    async def timeout_loop(self):
        while len(self.music_players) > 0:  # breaks loop when all music_players are disconnected
            for mp in self.music_players.values():
                if mp is None:
                    continue
                if len(mp.vc.channel.members) <= 1:
                    await mp.vc.disconnect()
                    self.music_players[mp.vc.guild] = None
                    print("left empty call.")
            await asyncio.sleep(self.timeout_check)
        self.timeout_is_running = False

    @commands.command(name='join')
    async def join(self, ctx):
        """Adds bot to current VC
        :param ctx: Discord context"""
        if self.music_players.get(ctx.guild) is None:
            await self.new_player(ctx)

    @commands.command(name='leave')
    async def leave(self, ctx):
        """Kicks bot from VC
        :param ctx: Discord context"""
        player = self.music_players.get(ctx.guild)
        if player is not None:
            await player.vc.disconnect(force=True)
            self.music_players[ctx.guild] = None
            response = 'Alright, see ya.'
        else:
            response = 'I cannot leave until I have joined.'
        await ctx.send(response, delete_after=60)

    @commands.command(name='play')
    async def play_audio(self, ctx, *args):
        """Adds a song to the queue
        :param ctx: discord context
        :param args: audio source"""
        if ctx.author.voice.channel is None:
            await ctx.send('You must be in a voice channel to play music.')
            return

        player = self.music_players.get(ctx.guild)
        if player is None:
            await self.new_player(ctx)
            player = self.music_players.get(ctx.guild)

        if len(args) > 0:

            if args[0] in ("-folder", "-list", "-next"):
                source = " ".join(args[1:len(args)])
            elif args[0] == "-file":
                attachments = ctx.message.attachments
                if len(attachments):
                    source = attachments[0]
                else:
                    await ctx.send("Attachment not found.")
                    return
            else:
                source = " ".join(args)

            if player.search_results and source.isnumeric():
                # if search was run check for user selection
                index = int(source)
                if index >= len(player.search_results):
                    await ctx.send("Invalid index.")
                    return
                # if chosen index is valid, add the corresponding song
                source = "https://www.youtube.com/watch?v=" + str(player.search_results[index].get('id'))
                player.search_results = None

            if args[0] == "-folder":
                # adds all songs in the specified folder and sub folders
                player.add_folder(source)
            elif args[0] == "-list":
                # adds all songs from a text file of sources
                player.add_list(source)
            elif args[0] == "-next":
                # adds a song to the front of the queue
                player.add_next(source)
            elif args[0] == "-file":
                # grabs a song from an embed
                await player.add_upload(source)
            else:
                if len(source) > 0:
                    song = player.add_song(source)
                    if song == "s":
                        embed = discord.Embed(
                            title="Search results:",
                            color=discord.Color.green(),
                            description=f"{player.print_search()}Respond with '~play [n]' to add."
                        )
                        await ctx.send(embed=embed)
                        return
                    else:
                        embed = discord.Embed(
                            title=f"{song} added to the queue.",
                            color=discord.Color.blue()
                        )
                        await ctx.send(embed=embed)

        if not player.vc.is_playing():
            player.play()

    @commands.command(name='move')
    async def move(self, ctx, start: int, end: int):
        """Move a song in the queue
        :param ctx: discord context
        :param start: original index
        :param end: new index"""
        player = self.music_players.get(ctx.guild)
        if player:
            if player.move(start, end):
                await ctx.send(f"Moved {player.queue[end].title} to {end}")

    @commands.command(name='remove')
    async def remove(self, ctx, index: int):
        """Remove a song from the queue
        :param ctx: discord context
        :param index: position in queue"""
        player = self.music_players.get(ctx.guild)
        if player:
            if index == 0:
                player.vc.stop()
            else:
                player.remove(index)

    @commands.command(name='stop')
    async def stop(self, ctx):
        """Kicks bot and clears the queue
        :param ctx: Discord context"""
        player = self.music_players.get(ctx.guild)
        if player:
            player.queue = []
            player.vc.stop()
            await player.vc.disconnect()
            self.music_players[ctx.guild] = None
        else:
            await ctx.send("Player instance not found.")

    @commands.command(name='pause')
    async def pause(self, ctx):
        """Toggle pause
        :param ctx: Discord context"""
        player = self.music_players.get(ctx.guild)
        if not player:
            await ctx.send("Wait a minute, I'm not even in voice. What'r you tryin' to pull here?")
            return
        vc = player.vc
        if vc.is_playing():
            vc.pause()
            response = 'The player has been paused.'
        elif vc.is_paused():
            vc.resume()
            response = 'The player has been unpaused.'
        else:
            response = 'The playlist is empty.'
        await ctx.send(response)

    @commands.command(name='skip')
    async def skip(self, ctx):
        """Skip the current song
        :param ctx: Discord context"""
        player = self.music_players.get(ctx.guild)
        if player:
            await ctx.send(f"Skipped {player.get_current_song().title}.")
            player.vc.stop()

    @commands.command(name='list')
    async def print_list(self, ctx):
        """The next 10 songs in the queue
        :param ctx: Discord context"""
        player = self.music_players.get(ctx.guild)
        if player:
            response = player.print_queue()
        else:
            response = "Player instance not found."
        await ctx.send(response)

    @commands.command(name='autoplay')
    async def toggle_auto_play(self, ctx):
        """Toggle autoplay
        :param ctx: Discord context"""
        player = self.music_players.get(ctx.guild)
        if player:
            player.set_autoplay(not player.autoplay)
            await ctx.send(f'Autoplay set to {player.autoplay}')

    @commands.command(name='repeat')
    async def toggle_repeat(self, ctx):
        """Toggle repeat
        :param ctx: Discord context"""
        player = self.music_players.get(ctx.guild)
        if player:
            player.set_repeat(not player.repeat)
            await ctx.send(f'Repeat set to {player.repeat}')

    @commands.command(name='shuffle')
    async def shuffle_queue(self, ctx):
        """Toggle shuffle
        :param ctx: Discord context"""
        player = self.music_players.get(ctx.guild)
        if player:
            player.set_shuffle(not player.shuffle)
            await ctx.send(f'Shuffle set to {player.shuffle}')


def setup(bot):
    import audio_player
    bot.add_cog(Music(bot))


def teardown(bot):
    """loop = asyncio.new_event_loop()
    for player in Music.music_players.values():
        asyncio.run(cleanup(player.vc))
        Music.music_players[player.vc.guild] = None"""
    pass


async def cleanup(vc):
    await vc.disconnect()
