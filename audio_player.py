#audio_player.py
class playlist():
    def __init__(self):
        self.queue = []
        self.current = None

    def play(self):
        #generator
        while len(self.queue) > 0:
            self.current = yield(self.queue.pop(0))




class audioPlayer():
    def __init__(self):
        print('New player initialized')
        self.playlist = []
        self.currently_playing = None
        self.repeat = False
        self.voice_client = None
        self.autoplay = True
        self.autoPlaylist = None
        self.auto_is_playing = False

    def play(self, source):
        '''takes the path to an audio file and plays it
            in the discord voice channel'''
        print(f'playing {source[0]}')
        if source[1] == 's':
            source = self.search(source[0])
        if source[1] == 'yt':
            source = [self.download(source[0]), 'd']
        self.currently_playing = source
        audioStream = discord.FFmpegPCMAudio(source[0])
        self.voice_client.play(audioStream, after = lambda e: self._play_next())

    def _play_next(self):
        print(len(self.playlist))
        if self.repeat:
            self.playlist.insert(0, self.currently_playing[0])
        if len(self.playlist) > 0:
            self.play(self.playlist.pop(0))
        elif self.autoplay:
            self.AutoPlay()

    def addsong(self, source):
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
        global dataPath
        title = f'{dataPath}{self.voice_client.guild.id}'
        
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

        return(f'{title}.mp3')
    
    def search(self, query):
        global dataPath
        title = f'{dataPath}{self.voice_client.guild.id}'
        print('searching')
        command = ['youtube-dl',f'ytsearch1:"{query}"', '-x','--audio-format', 'mp3',f'-o{title}.%(ext)s']
        subprocess.run(command)
        return((f'{title}.mp3', 'd'))
    
    async def join(self, ctx):
        self.voice_client = await ctx.author.voice.channel.connect()

    def AutoPlay(self):
        if self.autoPlaylist == None:
            with open(f'{dataPath}playlist.txt') as f:
                self.autoPlaylist = f.read().replace("'",'').replace('"','').split('\n')
                self.autoPlaylist = list(set(self.autoPlaylist))
                for n in range(len(self.autoPlaylist)):
                    self.autoPlaylist[n] = identifySource(self.autoPlaylist[n])
            random.shuffle(self.autoPlaylist)
            print("autoPlaylist initialized.")
            
        self.repeat = False
        self.auto_is_playing = True
        if len(self.autoPlaylist) > 0:
            self.play(self.autoPlaylist.pop())
        else:
            self.autoPlaylist = None
            self.AutoPlay()
