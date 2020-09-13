# audio_player.py
import subprocess
import discord
import youtube_dl
import youtube_search
import random
import mutagen
import os
import json
from dotenv import load_dotenv

load_dotenv()
MUSIC_DIR = os.getenv("MUSIC_DIR")


def identify_source(source):
    # tags the source input to tell the player what to do with it
    if 'youtube.com/watch?v=' in source or 'youtu.be/':
        return 'yt'
    elif os.path.exists(source) and ('.mp3' in source or '.flac' in source or '.wav' in source or '.m4a' in source):
        return 'f'
    else:
        return 's'


class Playlist:
    class Song:
        def __init__(self, source, source_type=None):
            self.source = source
            self.type = source_type
            if not source_type:
                self.type = identify_source(source)
            self.title = source
            self.artist = "unknown"
            self.downloaded = False
            if self.type == "f":
                self.downloaded = True
                self.get_info()

        def get_info(self):
            if self.type in ("f", "u"):
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

        def cleanup(self):
            if self.type == "u":
                if os.path.exists(self.source):
                    os.remove(self.source)

    def __init__(self, voice_client):
        self.queue = []  # list of Song objects to be played
        self.vc = voice_client  # the current voice_client connection
        self.auto_queue = self.get_auto_playlist()
        self.repeat = False
        self.shuffle = False
        self.autoplay = True
        self.search_results = None

    def play_next(self):
        if not len(self.queue):
            # if queue is empty break
            return
        if not self.repeat:
            # remove last played
            self.queue[0].cleanup()
            self.queue.pop(0)
        try:
            self.play()
        except discord.ClientException:
            return

    def play(self):
        if not len(self.queue):
            if not self.autoplay:
                # if not autoplay, end audio stream
                return
            # pick a new track at random from auto_queue
            while len(self.queue) == 0:
                self.add_song(self.auto_queue.pop(random.randint(0, len(self.auto_queue) - 1)))
            if len(self.auto_queue) == 0:
                self.auto_queue = self.get_auto_playlist()

        # (alt version) if self.shuffle and not self.repeat:
        # repeat takes priority
        # below shuffle takes priority, if repeat and shuffle are both on it will shuffle the playlist without delete
        if self.shuffle and len(self.queue) > 1:
            # move a random song in queue to the front
            self.queue.insert(0, self.queue.pop(random.randint(1, len(self.queue) - 1)))

        if not self.queue[0].downloaded:
            if not self.download(self.queue[0]):  # clean this up at some point
                # download failed
                print()
                self.play()
                return
        source = self.queue[0].source
        if os.path.exists(source):
            print(f">playing {source}")
            self.vc.play(discord.FFmpegPCMAudio(source), after=lambda e: self.play_next())
            # print(f"downloading next...")
            # downloads next song in queue
            if not self.shuffle and len(self.queue) > 1:
                self.download(self.queue[1])
        else:
            print(f"[source not found]: {source}")
            self.play_next()

    def get_current_song(self):
        if len(self.queue) > 0:
            return self.queue[0]
        else:
            return None

    def add_song(self, source):
        song = self.Song(source)
        if song.type == "s":
            self.search(source)
            return "s"
        self.queue.append(song)
        # if next up, pre-download
        if len(self.queue) == 2:
            self.download(self.queue[1])
        return song.title

    def add_next(self, source):
        if len(self.queue) > 1:
            self.queue.insert(1, self.Song(source))
            self.download(self.queue[1])
        else:
            self.add_song(source)

    def add_folder(self, folder):
        if ":\\" not in folder:
            folder = f'{MUSIC_DIR}\\{folder}'
        if not os.path.exists(folder):
            return f"[Path not found]: {folder}"
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
        # todo: add playlist from youtube or text file or written list of sources separated by ','
        pass

    async def add_upload(self, attachment):
        # todo: work in progress version, allows user to upload a small mp3 and play it on the bot
        # has a few incompatibilities with the download function
        title = attachment.filename
        if ".mp3" in title or ".wav" in title or ".flac" in title:
            await attachment.save(title)
            self.queue.append(self.Song(title, "u"))

    def move(self, start, end):
        if start < len(self.queue) and end < len(self.queue):
            self.queue.insert(end, self.queue.pop(start))
            return True
        return False

    def remove(self, index):
        if index < len(self.queue):
            self.queue.pop(index)

    def set_repeat(self, repeat):
        self.repeat = repeat

    def set_shuffle(self, shuffle):
        self.shuffle = shuffle

    def set_autoplay(self, autoplay):
        self.autoplay = autoplay

    def gen_title(self):
        if len(self.queue) != 0:
            if self.queue[0].source == "song.mp3":
                return "song1"
        return "song"

    def download(self, song):
        title = self.gen_title()
        # print(f"downloading {song.source}, {song.type}")
        try:
            if song.type == "s":
                command = ['youtube-dl', f'ytsearch1:"{song.source}"',
                           '-x', '-q', '--audio-format', 'mp3', f'-o{title}.%(ext)s']
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

    def download_next(self):
        if len(self.queue) > 1:
            self.download(self.queue[1])

    def search(self, search_terms):
        self.search_results = youtube_search.YoutubeSearch(search_terms, max_results=5).to_dict()

    def print_search(self):
        if not self.search_results:
            return ""
        output_string = ""
        for n in range(len(self.search_results)):
            output_string += f"{n}. {self.search_results[n].get('title')}\n"
        return output_string

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
        to_return = ""
        for n in range(10):
            if n >= len(self.queue):
                break
            song = self.queue[n]
            to_return += f"{n}. {song.title} by {song.artist} \n"
        return to_return
