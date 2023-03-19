import pathlib
import time
def mergeMp4(folderPath, tsList):
	# 開始時間
    start_time = time.time()
    print('開始合成影片..')

    for i in range(len(tsList)):
        file = tsList[i].split('/')[-1]
        full_path = pathlib.Path(folderPath, file)
        video_name = pathlib.Path(folderPath, 'aa.mp4')
        if full_path.exists():
            with full_path.open(mode='rb') as f1:
                with video_name.open(mode='ab') as f2:
                    f2.write(f1.read())
        else:
            print(file + " 失敗 ")
    end_time = time.time()
    print('花費 {0:.2f} 秒合成影片'.format(end_time - start_time))
    print('下載完成!')

