# music_grabber.py
import os


def musicGrabber(startingPath: str, destination):
    driveList = [startingPath]

    for drive in driveList:
        dirlist = os.listdir(drive)
        for item in dirlist:
            file = f'{drive}\\{item}'
            if os.path.isdir(file):
                driveList.append(file)
            elif '.mp3' in item or '.flac' in item or '.wav' in item:
                with open(destination, 'a') as d:
                    try:
                        d.write(file + '\n')
                        print(item)
                    except UnicodeEncodeError:
                        pass
