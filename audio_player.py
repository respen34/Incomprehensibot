# audio_player.py
import subprocess
import discord
import youtube_dl
import random
import mutagen
import os
import json


def identify_source(source):
    # tags the source input to tell the player what to do with it
    if 'youtube.com/watch?v=' in source:
        return 'yt'
    elif ':\\' in source and ('.mp3' in source or '.flac' in source or '.wav' in source or '.m4a' in source):
        return 'f'
    else:
        return 's'


def search(query):
    title = 'song'
    print('searching')
    command = ['youtube-dl', f'ytsearch1:"{query}"', '-x', '--audio-format', 'mp3', f'-o{title}.%(ext)s']
    subprocess.run(command)
    return f'{title}.mp3'


def download(video_url):
    title = 'song'
    ydl_opts = {
        'quiet': 'True', 'noplaylist': 'True', 'outtmpl': f'{title}.%(ext)s',
        'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio',
                                                        'preferredcodec': 'mp3',
                                                        'preferredquality': '192', },
                                                       {'key': "FFmpegMetadataPP"}],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    return f'{title}.mp3'


class Playlist:
    class Song:
        def __init__(self, source):
            self.source = source
            self.type = identify_source(source)
            self.title = source
            self.artist = "unknown"
            self.downloaded = False
            if self.type == "f":
                self.downloaded = True
                self.get_info()

        def get_info(self):
            if self.type == "f":
                if not os.path.exists(self.source):
                    return
                song = mutagen.File(self.source, None, True)
                if song is None:
                    return
                tags = song.tags
                if tags is None:
                    return
                else:
                    if '.flac' in self.source:
                        artist = tags.get("ARTIST")
                        title = tags.get("TITLE")
                    else:
                        artist = tags.get("artist")
                        title = tags.get("title")

                    if artist is not None and len(artist) > 0:
                        self.artist = artist[0]
                    if title is not None and len(title) > 0:
                        self.title = title[0]

    def __init__(self, voice_client):
        self.queue = []
        self.auto_queue = self.get_auto_playlist()
        self.repeat = False
        self.autoplay = True
        self.vc = voice_client

    def play_next(self):
        if not self.repeat:
            self.queue.pop(0)
        self.play()

    def play(self):

        if not len(self.queue):
            if not self.autoplay:
                return
            while len(self.queue) == 0:
                self.add_song(self.auto_queue.pop(random.randint(0, len(self.auto_queue) - 1)))
            if len(self.auto_queue) == 0:
                self.auto_queue = self.get_auto_playlist()

        if not self.queue[0].downloaded:
            if not self.download(self.queue[0]):  # clean this up at some point
                self.play()
                return
        source = self.queue[0].source
        if os.path.exists(source):
            print(f"playing {source}")
            self.vc.play(discord.FFmpegPCMAudio(source), after=lambda e: self.play_next())
            # print(f"downloading next...")
            # downloads next song in queue
            if len(self.queue) > 1:
                self.download(self.queue[1])
        else:
            print(f"couldn't play source {source}")
            self.play_next()

    def get_current_song(self):
        if len(self.queue) > 0:
            return self.queue[0]
        else:
            return None

    def add_song(self, source):
        self.queue.append(self.Song(source))
        # if next up, predownloads
        if len(self.queue) == 2:
            self.download(self.queue[1])

    def add_folder(self, folder):
        if ":\\" not in folder:
            folder = f'C:\\Users\\respen34\\Music\\{folder}'
        if not os.path.exists(folder):
            return f"Path not found: {folder}"
        dir_list = [folder]

        playlist = []
        for drive in dir_list:
            current_dir = os.listdir(drive)
            for item in current_dir:
                file = f'{drive}\\{item}'
                if os.path.isdir(file):
                    dir_list.append(file)
                elif '.mp3' in item or '.flac' in item or '.wav' in item:
                    playlist.append(self.Song(file))

        self.queue.extend(playlist)

    def add_list(self, path):
        pass

    def set_repeat(self, repeat):
        self.repeat = repeat

    def gen_title(self):
        if len(self.queue) != 0:
            if self.queue[0].source == "song.mp3":
                return "song1"
        return "song"

    def download(self, song):
        title = self.gen_title()
        print(f"downloading {song.source}, {song.type}")
        try:
            if song.type == "s":
                command = ['youtube-dl', f'ytsearch1:"{song.source}"',
                           '-x', '--audio-format', 'mp3', f'-o{title}.%(ext)s']
                subprocess.run(command)
                song.source = f'{title}.mp3'
            elif song.type == "yt":
                ydl_opts = {
                    'quiet': 'True', 'noplaylist': 'True', 'outtmpl': f'{title}.%(ext)s',
                    'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio',
                                                                    'preferredcodec': 'mp3',
                                                                    'preferredquality': '192', }, ],
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([song.source])
                song.source = f'{title}.mp3'
            song.downloaded = True
            return True
        except:
            print(f"{song.source} failed to download")
            self.queue.remove(song)
            return False

    @staticmethod
    def get_auto_playlist():
        playlist = []
        if not os.path.exists("autoplay.json"):
            with open("autoplay.json", "w") as f:
                json.dump(playlist, f)
        with open("autoplay.json") as f:
            playlist = json.load(f)
            # print(playlist)
        if len(playlist) == 0:
            dir_list = [r"C:\Users\respen34\Music"]
            playlist = []
            for drive in dir_list:
                current_dir = os.listdir(drive)
                for item in current_dir:
                    file = f'{drive}\\{item}'
                    if os.path.isdir(file):
                        dir_list.append(file)
                    elif '.mp3' in item or '.flac' in item or '.wav' in item:
                        playlist.append(file)
        with open("autoplay.json", "w") as f:
            json.dump(playlist, f)
        return playlist

    def print_queue(self):
        toReturn = ""
        for n in range(10):
            if n >= len(self.queue):
                break
            song = self.queue[n]
            toReturn += f"{n}. {song.title} by {song.artist} \n"
        return toReturn


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
            self.play_next(self.playlist.pop(0))
        else:
            self.currently_playing = None
            if self.autoplay:
                self.AutoPlay()'''

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
