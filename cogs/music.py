import discord
import audio_player
from discord.ext import commands


class Music(commands.Cog):
    music_players = {}

    def __init__(self, bot):
        self.bot = bot
        print("Music initialized")

    async def new_player(self, ctx):
        # bot connects to the voice client of the user who executed the command and creates a new playlist instance
        self.music_players[ctx.guild] = audio_player.Playlist(await ctx.author.voice.channel.connect())

    @commands.command(name='join')
    async def join(self, ctx):
        """
        adds bot to current voice chat
        :param ctx: Discord context
        :return:
        """
        if self.music_players.get(ctx.guild) is None:
            await self.new_player(ctx)

    @commands.command(name='leave')
    async def leave(self, ctx):
        """
        kicks bot from voice chat
        :param ctx: Discord context
        :return:
        """
        player = self.music_players.get(ctx.guild)
        if player is not None:
            await player.vc.disconnect()
            self.music_players[ctx.guild] = None
            response = 'Alright, see ya.'
        else:
            response = 'I cannot leave until I have joined.'
        await ctx.send(response, delete_after=60)

    @commands.command(name='play')
    async def play_audio(self, ctx, *args):
        """
        Plays audio in voice.
        :param ctx: discord context
        :param args: audio source
        :return:
        """
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
                source = "https://www.youtube.com" + player.search_results[index].get('link')
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
                        await ctx.send(f"Search results:\n{player.print_search()}Respond with '~play [n]' to add.")
                        return
                    else:
                        await ctx.send(f" Added: {song} to the queue.")

        if not player.vc.is_playing():
            player.play()

    @commands.command(name='move')
    async def move(self, ctx, start: int, end: int):
        player = self.music_players.get(ctx.guild)
        if player:
            if player.move(start, end):
                await ctx.send(f"Moved {player.queue[end].title} to {end}")

    @commands.command(name='remove')
    async def remove(self, ctx, index: int):
        """
        removes a song from the queue at the given index.
        :param ctx: discord context
        :param index: position in queue
        :return:
        """
        player = self.music_players.get(ctx.guild)
        if player:
            if index == 0:
                player.vc.stop()
                return
            player.remove(index)

    @commands.command(name='stop')
    async def stop(self, ctx):
        """
        stops bot and clears playlist
        :param ctx: Discord context
        :return:
        """
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
        """
        pauses/unpauses current audio stream
        :param ctx: Discord context
        :return:
        """
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
        """
        skips currently playing song
        :param ctx: Discord context
        :return:
        """
        player = self.music_players.get(ctx.guild)
        if player:
            await ctx.send(f"Skipped {player.get_current_song().title}.")
            player.vc.stop()

    @commands.command(name='list')
    async def print_list(self, ctx):
        """
        lists the first 10 songs in the queue
        :param ctx: Discord context
        :return:
        """
        player = self.music_players.get(ctx.guild)
        if player:
            response = player.print_queue()
        else:
            response = "Player instance not found."
        await ctx.send(response)

    @commands.command(name='autoplay')
    async def toggle_auto_play(self, ctx):
        """
        Toggles autoplay
        :param ctx: Discord context
        :return:
        """
        player = self.music_players.get(ctx.guild)
        if player:
            player.set_autoplay(not player.autoplay)
            await ctx.send(f'Autoplay set to {player.autoplay}')

    @commands.command(name='repeat')
    async def toggle_repeat(self, ctx):
        """
        Toggles repeat
        :param ctx: Discord context
        :return:
        """
        player = self.music_players.get(ctx.guild)
        if player:
            player.set_repeat(not player.repeat)
            await ctx.send(f'Repeat set to {player.repeat}')

    @commands.command(name='shuffle')
    async def shuffle_queue(self, ctx):
        """
        Toggles shuffle
        :param ctx: Discord context
        :return:
        """
        player = self.music_players.get(ctx.guild)
        if player:
            player.set_shuffle(not player.shuffle)
            await ctx.send(f'Shuffle set to {player.shuffle}')


def setup(bot):
    bot.add_cog(Music(bot))
