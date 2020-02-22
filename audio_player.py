# audio_player.py
import subprocess
import discord
import youtube_dl
import random


def identify_source(source, file_type='yt'):
    # tags the source input to tell the player what to do with it
    if file_type == 'yt' and 'youtube.com/watch?v=' in source:
        return source, 'yt'
    elif file_type == 'f' or (('.mp3' in source or '.flac' in source
                               or '.wav' in source or '.m4a' in source
                               or '.cda' in source) and ':\\' in source):
        return source, 'f'
    else:
        return source, 's'


class Playlist:
    def __init__(self):
        self.queue = []
        self.current = None

    def play(self):
        # generator
        while len(self.queue) > 0:
            self.current = yield self.queue.pop(0)


class AudioPlayer:
    def __init__(self):
        print('New player initialized')
        self.playlist = []
        self.currently_playing = None
        self.repeat = False
        self.voice_client = None
        self.autoplay_is_on = True
        self.autoPlaylist = None
        self.auto_is_playing = False

    def play(self, source):
        """takes the path to an audio file and plays it
            in the discord voice channel"""
        print(f'playing {source[0]}')
        if source[1] == 's':
            source = self.search(source[0])
        if source[1] == 'yt':
            source = [self.download(source[0]), 'd']
        self.currently_playing = source
        audio_stream = discord.FFmpegPCMAudio(source[0])
        self.voice_client.play(audio_stream, after=lambda e: self._play_next())

    def _play_next(self):
        # print(len(self.playlist))
        if self.repeat:
            self.playlist.insert(0, self.currently_playing[0])
        if len(self.playlist) > 0:
            self.play(self.playlist.pop(0))
        elif self.autoplay_is_on:
            self.auto_play()

    def add_song(self, source):
        self.playlist.append(source)
        print(f'{source[0]} added.')
        if self.auto_is_playing:
            self.skip()
            self.auto_is_playing = False

    def skip(self):
        self.voice_client.stop()
        '''if len(self.playlist)>0:
            self.play(self.playlist.pop(0))
        else:
            self.currently_playing = None
            if self.autoplay:
                self.AutoPlay()'''

    def download(self, video_url):
        title = f'{self.voice_client.guild.id}'

        ydl_opts = {
            'quiet': 'True',
            'noplaylist': 'True',
            'outtmpl': f'{title}.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        return f'{title}.mp3'

    def search(self, query):
        title = f'{self.voice_client.guild.id}'
        print('searching')
        command = ['youtube-dl', f'ytsearch1:"{query}"', '-x', '--audio-format', 'mp3', f'-o{title}.%(ext)s']
        subprocess.run(command)
        return f'{title}.mp3', 'd'

    async def join(self, ctx):
        self.voice_client = await ctx.author.voice.channel.connect()

    def auto_play(self):
        if self.autoPlaylist is None:
            with open('playlist.txt') as f:
                self.autoPlaylist = f.read().replace("'", '').replace('"', '').split('\n')
                self.autoPlaylist = list(set(self.autoPlaylist))
                for n in range(len(self.autoPlaylist)):
                    self.autoPlaylist[n] = identify_source(self.autoPlaylist[n])
            random.shuffle(self.autoPlaylist)
            print("autoPlaylist initialized.")

        self.repeat = False
        self.auto_is_playing = True
        if len(self.autoPlaylist) > 0:
            self.play(self.autoPlaylist.pop())
        else:
            self.autoPlaylist = None
            self.auto_play()
