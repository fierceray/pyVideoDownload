#/usr/bin/env python3

# import public dependency
import requests
import m3u8
from pathlib import Path
import cloudscraper
from Crypto.Cipher import AES
import copy
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor

# local files
import config

# Change the BASE_DIR to put file into mass media drive
BASE_DIR = Path('./download')



target_url = "https://ap-drop-monst.mushroomtrack.com/bcdn_token=1VcPq7kjeFFTO_Ji94QrDozyWiuc9ttmDyiGiIwfRg4&expires=1679285187&token_path=%2Fvod%2F/vod/14000/14703/14703.m3u8"


# This URL is the target m3u8 file extracted from the website. https://jable.tv/videos/ipx-543/
# TODO To scrape the html file from website.

class VideoFile:
    def __init__(self, target_url):

        # TODO when scrape the web html file, need to identify the video name, and add to the
        self.video_name = 'IPX-543'

        # setup folder and file location
        self.target_url = target_url
        urlHandleList = self.target_url.split('/')
        folderName = urlHandleList[-2]
        self.folderPath = BASE_DIR / folderName
        # create folder if not exists
        Path(self.folderPath).mkdir(parents=True, exist_ok=True)

        # Since the download files are sharing the same base url, using the m3u8 url to get the base
        urlHandleList.pop()
        self.downloadUriBase = '/'.join(urlHandleList)

        # get m3u8 file and process the information
        response = cloudscraper.create_scraper(browser='chrome', delay=10).get(self.target_url)
        try:
            response.raise_for_status()
        except:
            print("Retrieve m3u8 file failed.....")
        else:
            m3u8obj = m3u8.loads(response.text)

            # Get the encryption key
            ci = ''
            for key in m3u8obj.keys:
                if key:
                    print(key.uri)
                    print(key.iv)
                    # 有加密
                    m3u8keyurl = self.downloadUriBase + '/' + key.uri  # 得到 key 的網址

                    # 得到 key的內容
                    headers = config.getHeader()
                    response = requests.get(m3u8keyurl, headers=headers, timeout=10)
                    contentKey = response.content

                    vt = key.iv.replace("0x", "")[:16].encode()  # IV取前16位

                    self.ci = AES.new(contentKey, AES.MODE_CBC, vt)  # 建構解碼器

                    # get the ts file URL list
                    self.tsList = []
                    for seg in m3u8obj.segments:
                        tsUrl = self.downloadUriBase + '/' + seg.uri
                        self.tsList.append(tsUrl)
                    print(len(self.tsList))

    def scrape(self, download_url):
        file_name = download_url.split('/')[-1]
        save_path = Path(self.folderPath, file_name)

        if save_path.exists():
            # Skip downloaded files
            print(f'Current target {0} exists already, skip....'.format(file_name))
        else:
            try:
                response = requests.get(download_url, headers=config.getHeader())
                response.raise_for_status()

                content_ts = response.content
                if self.ci:
                    content_ts = self.ci.decrypt(content_ts)  # decrypt by using ci
                with open(save_path, 'ab') as f:
                    f.write(content_ts)
                    # progress monitoring
                print(f'\rDownloading: {0} , pending {1} files, status code: {2}'.format(
                    file_name, len(self.downloadQueue), response.status_code), end='', flush=True)
            except:
                print('error: I am here')
        # Remove the current working one from the download queue.
        self.downloadQueue.remove(download_url)

    def crawl(self):
        self.downloadQueue = copy.deepcopy(self.tsList)
        # Start time
        start_time = time.time()
        print('開始下載 ' + str(len(self.downloadQueue)) + ' 個檔案..', end='')
        print('預計等待時間: {0:.2f} 分鐘 視影片長度與網路速度而定)'.format(len(self.downloadQueue) / 150))

        # multiple threads start
        with ThreadPoolExecutor(max_workers=8) as executor:
            future = executor.map(self.scrape, self.tsList)

        # End time
        end_time = time.time()
        print('\n花費 {0:.2f} 分鐘 爬取完成 !'.format((end_time - start_time) / 60))

    def merge(self):
        # 開始時間
        start_time = time.time()
        print('開始合成影片..')
        # TODO Use ffmpeg instead of direct insert

        video_ts = Path(self.folderPath, self.video_name + '.ts')
        video_mp4 = Path(self.folderPath, self.video_name + '.mp4')

        # Merge all ts files to one large ts file
        for ts_file in self.tsList:
            file = ts_file.split('/')[-1]
            file_path = Path(self.folderPath, file)
            if file_path.exists():
                with file_path.open(mode='rb') as f1:
                    with video_ts.open(mode='ab') as f2:
                        f2.write(f1.read())
            else:
                print(file + " 失敗 ")

        # use ffmpeg to convert to mp4
        if video_mp4.exists():
            if 'y' == input("The mp4 file already exists, overwrite? [y/n]:").lower():
                subprocess.run(['ffmpeg', '-hwaccel', 'cuvid', '-c:v', 'h264_cuvid', '-i', video_ts,
                                '-c:v', 'hevc_nvenc', '-preset', 'slow', '-rc', 'vbr', '-cq', '28', '-b:v',
                                '10M', '-maxrate', '12M', '-bufsize', '16M', '-c:a', 'copy', video_mp4])
                # ffmpeg -hwaccel cuvid -c:v h264_cuvid -i input.ts -c:v hevc_nvenc -preset slow -rc vbr -cq 28 -b:v 10M -maxrate 12M -bufsize 16M -c:a copy output.mp4


        end_time = time.time()
        print('花費 {0:.2f} 秒合成影片'.format(end_time - start_time))
        print('下載完成!')

    def cleanup(self):
        # TODO clean up the ts files and get the thumbnail
        print("cleanup in construction.....")
        for p in Path(self.folderPath).iterdir():
            print(p)

    def execute(self):
        self.crawl()
        self.merge()
        self.cleanup()
        return self.folderPath, self.video_name + '.mp4'

if __name__ == '__main__':
    video = VideoFile(target_url)
    video.execute()

