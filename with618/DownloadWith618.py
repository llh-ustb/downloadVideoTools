# a tools for download vip video from aiqiyi , tengxun or others
# paramers :
#          url :website for watching videos e.g. aiqiyi website
#          savePath :where to save download .ts file. Note(this floder should be empty)
# output video will be saved in ../savePath

import requests
import subprocess
import re
import threading
from concurrent.futures import ThreadPoolExecutor
import logging
import os
import time
import json

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Download618:

    def __init__(self,url,savePath):
        self.url=url
        self.savePath=savePath
        self.downUrl=[]
    def download(self,url):
        if url==0:
            time.sleep(1)
        else:
            urlResponse=requests.get(url)
            if os.path.exists(self.savePath+'/{}'.format(url[-10:])):
                pass
            with open(self.savePath+'/{}'.format(url[-10:]),'wb') as vo:
                    vo.write(urlResponse.content)
                    logger.info('%s'%url)
            lenDownloadFile=len(os.listdir('v'))
            logger.info('finished number : %s/%s'%(lenDownloadFile,self.urlLength))

    def getWebData(self):
        jx618Url='http://jx.618g.com/?url='+self.url
        logger.info('jx618Url : %s'%jx618Url)
        post=requests.post(jx618Url)
        #从jx618url里提取.m3u8为后缀的网址，并用其来提取视频播放网址
        jx618Content=post.content
        r1=r'https://.*?.m3u8'
        rs1=re.compile(r1)
        find=re.findall(rs1,jx618Content.decode('utf-8'))
        m3618Url=find[0]#获取到了.m3u8为后缀的网址
        logger.info('m3u8Url : %s'%m3618Url)
        m3618UrlRespone=requests.get(m3618Url)    #使用获取到的地址拼接一个新的地址用于获取真实视频的视频地址
        du=m3618Url[:-10] + m3618UrlRespone.text.split('\n')[-1]
        duRespone=requests.get(du,headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"})
        with open('du.txt','w') as f:
            f.write(duRespone.text)
        #validUrl包含真实的播放文件名即以.ts为后缀的文件
        findTsFileName='\n.*.ts'
        findTsFileNameComplie=re.compile(findTsFileName)
        validDownUrl=re.findall(findTsFileNameComplie,duRespone.text)
        for vdurl in validDownUrl:
            self.downUrl.append(du[:-10]+vdurl[1:])
        self.urlLength=len(self.downUrl)
        logger.info("there are %s .ts files"%self.urlLength)

    def start(self,threadNum):
        self.getWebData()
        pool=ThreadPoolExecutor(max_workers=threadNum)
        for durl in self.downUrl:
            _=pool.submit(self.download,durl)
        for t in range(40):
            _=pool.submit(self.poolWait,t)
        pool.shutdown(wait=True)

    def poolWait(self,t):
        time.sleep(1)
def concatVideo(videoListFile,outputName):
    logger.info('start concat...')
    try:
        cmd="ffmpeg -f concat -safe 0 -i {} -c copy {}".format(videoListFile,outputName)
        res = subprocess.call(cmd, shell=True)
        if res != 0:
            return False
        return True
    except Exception:
        return False

# url='https://www.bilibili.com/bangumi/play/ep277173'
# savePath='v/'
# downloader=Download618(url,savePath)
# downloader.start()
# time.sleep(4)
# absPath=os.path.abspath(savePath)
jsonOpen=open('DownloadWith618Conf.json','r')
jsonData=json.load(jsonOpen)

for js in jsonData['downloadInfo']:
    url = js['url']
    savePath = js['savePath']
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    downloader = Download618(url, savePath)
    downloader.start(jsonData['threadingPoolWorkers'])
    time.sleep(4)
    absPath = os.path.abspath(savePath)
    while True:
        if(len(threading.enumerate())==1):
            logger.info('download finished')
            videoList=os.listdir(savePath)
            videoList=[ 'file '+'\''+absPath+'\\'+vl+'\'\n' for vl in videoList]
            with open( os.path.abspath(absPath+'/../'+'videoListFile.txt'),'w') as of:
                of.writelines(videoList)
            concatVideo(os.path.abspath(absPath+'/../'+'videoListFile.txt'),js['outputName'])
            break
        else:
            logger.debug('unfinished')
