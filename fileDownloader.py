import requests
import m3u8
from pathlib import Path
import cloudscraper
from Crypto.Cipher import AES
import config
import crawler
import merge

target_url = "https://ap-drop-monst.mushroomtrack.com/bcdn_token=KsvYYA3b74XJrmXVU5_qspYqXxvNYJLhpW5G15NM_9U&expires=1679261492&token_path=%2Fvod%2F/vod/14000/14703/14703.m3u8"
# This URL is the target m3u8 file extracted from the website. https://jable.tv/videos/ipx-543/
# TODO To scrape the html file from website.


r = cloudscraper.create_scraper(browser='chrome', delay=10).get(target_url)

# Change the BASE_DIR to put file into mass media drive
BASE_DIR = Path('./download')

urlHandleList = target_url.split('/')
dirName = urlHandleList[-2]

folderPath = BASE_DIR / dirName

Path(folderPath).mkdir(parents=True, exist_ok=True)

# TODO use the dirName to generate folder and file in the corresponding location

# Since the download files are sharing the same base url, using the m3u8 url to get the base
temp = target_url.split('/')
temp.pop()
downloadUriBase = '/'.join(temp)
print(downloadUriBase)
m3u8obj = m3u8.loads(r.text)

for key in m3u8obj.keys:
    if key:
        print(key.uri)
        print(key.iv)
        # 有加密
        m3u8keyurl = downloadUriBase + '/' + key.uri  # 得到 key 的網址

        # 得到 key的內容
        headers = config.getHeader()
        response = requests.get(m3u8keyurl, headers=headers, timeout=10)
        contentKey = response.content

        vt = key.iv.replace("0x", "")[:16].encode()  # IV取前16位

        ci = AES.new(contentKey, AES.MODE_CBC, vt)  # 建構解碼器
    else:
        ci = ''

    print(vt)

    # use download URI base and the ts file to generate the list recording each file location

    tsList = []
    for seg in m3u8obj.segments:
        tsUrl = downloadUriBase + '/' + seg.uri
        tsList.append(tsUrl)
    print(len(tsList))

    # use download URI base and the ts file to generate the list recording each file location

    tsList = []
    for seg in m3u8obj.segments:
        tsUrl = downloadUriBase + '/' + seg.uri
        tsList.append(tsUrl)
    print(len(tsList))

    # 開始爬蟲並下載mp4片段至資料夾
    crawler.prepareCrawl(ci, folderPath, tsList)

    # Merge
    merge.mergeMp4(folderPath, tsList)