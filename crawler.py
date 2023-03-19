import pathlib
import requests
import config
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import time
import copy


# def scrape(ci, folderPath, downloadList, urls):
    # os.path.split(urls)
    # fileName = urls.split('/')[-1][0:-3]
    # saveName = os.path.join(folderPath, fileName + ".mp4")
    # if os.path.exists(saveName):
    #     # 跳過已下載
    #     print('當前目標: {0} 已下載, 故跳過...剩餘 {1} 個'.format(
    #         urls.split('/')[-1], len(downloadList)))
    #     downloadList.remove(urls)
    # else:
    #     response = requests.get(urls, headers=headers, timeout=10)
    #     if response.status_code == 200:
    #         content_ts = response.content
    #         if ci:
    #             content_ts = ci.decrypt(content_ts)  # 解碼
    #         with open(saveName, 'ab') as f:
    #             f.write(content_ts)
    #             # 輸出進度
    #         downloadList.remove(urls)
    #     print('\r當前下載: {0} , 剩餘 {1} 個, status code: {2}'.format(
    #         urls.split('/')[-1], len(downloadList), response.status_code), end='', flush=True)


# def scrape(ci, folderPath, downloadUrl):
#     print(f"{a}, {b}, {c}")
#     fileName = downloadUrl.split('/')[-1]
#     savePath = pathlib.Path(folderPath, fileName)
    
#     if savePath.exists():
#         # 跳過已下載
#         print('當前目標: {0} 已下載, 故跳過...'.format(downloadUrl.split('/')[-1]))
#     else:
#         response = requests.get(downloadUrl, headers=config.getHeader(), timeout=10)
#         if response.status_code == 200:
#             content_ts = response.content
#             if ci:
#                 content_ts = ci.decrypt(content_ts)  # 解碼
#             with open(savePath, 'ab') as f:
#                 f.write(content_ts)
#                 # 輸出進度
#         print('\r當前下載: {0} , 剩餘 {1} 個, status code: {2}'.format(
#             downloadUrl.split('/')[-1], response.status_code), end='', flush=True)

def scrape(ci, folderPath, downloadUrl):
    fileName = downloadUrl.split('/')[-1]
    savePath = pathlib.Path(folderPath, fileName)
    print(downloadUrl)
    if savePath.exists():
        # 跳過已下載
        print('當前目標: {0} 已下載, 故跳過...'.format(fileName))
    else:
        try:
            response = requests.get(downloadUrl, headers=config.getHeader())
            if response.status_code == 200:
                content_ts = response.content
                if ci:
                    content_ts = ci.decrypt(content_ts)  # 解碼
                with open(savePath, 'ab') as f:
                    f.write(content_ts)
                    # 輸出進度
            print('\r當前下載: {0} , 剩餘 {1} 個, status code: {2}'.format(
                fileName, response.status_code), end='', flush=True)
        except:
            print('error:')



def prepareCrawl(ci, folderPath, tsList):
    downloadQueue = copy.deepcopy(tsList)
    # Start time
    start_time = time.time()
    print('開始下載 ' + str(len(downloadQueue)) + ' 個檔案..', end='')
    print('預計等待時間: {0:.2f} 分鐘 視影片長度與網路速度而定)'.format(len(downloadQueue) / 150))

    # multiple threads start
    with ThreadPoolExecutor(max_workers=8) as executor:
        future = executor.map(partial(scrape, ci, folderPath), tsList)

    # End time
    end_time = time.time()
    print('\n花費 {0:.2f} 分鐘 爬取完成 !'.format((end_time - start_time) / 60))


# def startCrawl(ci, folderPath, downloadList):
#     # 同時建立及啟用 20 個執行緒
#     round = 0
#     with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
#         executor.submit(scrape)
#         round += 1
#         print(f', round {round}')