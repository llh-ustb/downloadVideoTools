# using youtube_dl to download video form youtube or bilibili or others Free Admission video
# arges:
#      videoWebSite: contain video url txt tile
#      savePath: where to save video,note(this floder should be empty)
#      videoFormat: 'best' (video and audio)
#                   'bestvideo' (only video)
#
# function audioVideo using ffmpeg to conbine video and audio file
#
# if we want to download the best quality video with audio from youtube,
# we shoud download video and audio separately and then merge them using function audioVideo()
#
import youtube_dl
import logging
import os
import re
import subprocess


class Logger(logging.Logger):

    def __init__(self):
        self.log = open('log.log', 'aw')

    def debug(self, msg):
        self.log.writelines(msg)

    def warning(self, msg):
        self.log.writelines(msg)

    def error(self, msg):
        self.log.writelines(msg)


class Download():

    def __init__(self, url, savePath, videoFormat='best', log=False):
        self.url = url
        self.savePath = savePath
        self.videoFormat = videoFormat
        self.finishedCount = 0
        self.log = log
        pass

    def parserUrl(self):
        self.parsedUrl = []
        num = 0
        if (os.path.isfile(self.url)):
            with open(self.url, 'r') as op:
                for i in op.readlines():
                    self.parsedUrl.append(i)
                    num += 1
            self.fileLength = num
        else:
            self.parsedUrl.append(self.url)

    def download(self, url):
        if not os.path.exists(self.savePath):
            os.mkdir(self.savePath)
        ydl_opts = {
            'outtmpl': self.savePath + '\\' + '%(id)s.%(ext)s',
            'format': self.videoFormat,
            'ignoreerrors': True,
            'progress_hooks': [self.my_hook],
            # 'logger':Logger() #regist logger
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)

    def my_hook(self, d):
        if d['status'] == 'finished':
            self.finishedCount += 1
            print('-----------------Done downloading : {}'.format(d['filename']))
            print('-----------------finished count :{}/{}'.format(self.finishedCount, self.fileLength))
            print()

    def check(self):
        checkingFlag = True
        print('checking...')
        while checkingFlag:
            unfinishedUrl = []
            fileList = os.listdir(self.savePath)
            for file in fileList:
                t = file.split('.')[-1]
                if (t == 'part' or t == 'withytdl'):
                    s = r'.*{}'.format(file.split('.')[0])
                    rs = re.compile(s)
                    reFind = [re.findall(rs, j) for j in self.parsedUrl]
                    validURl = [i for i in reFind if i != []]
                    if validURl == []:
                        pass
                    else:
                        unfinishedUrl.append(validURl[0][0])
            unfinishedUrl = list(set(unfinishedUrl))
            if unfinishedUrl != []:
                print('----------continue downloading unfinshed video')
                self.download(unfinishedUrl)
            else:
                checkingFlag = False
                print('----------finished----------')

    def start(self):
        self.parserUrl()
        self.download(self.parsedUrl)
        self.check()


def audioVideo(videoFile, audioFile, out_file):
    try:
        cmd = "ffmpeg -i %s -i %s  %s" % (videoFile, audioFile, out_file)
        res = subprocess.call(cmd, shell=True)

        if res != 0:
            return False
        return True
    except Exception:
        return False

def main():
    videoWebSite = r'url.txt'  # url.txt or url
    download = Download(videoWebSite, savePath=r'F:\ibeikedownload\videos', videoFormat='best')
    download.start()
    # audioVideo('NJt8tkSY2wo.mp4','NJt8tkSY2wo.webm','out.mp4')

if __name__=='main':
    main()
