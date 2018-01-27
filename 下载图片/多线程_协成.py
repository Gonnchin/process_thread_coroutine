import gevent
from gevent import monkey
import urllib.request
import threading
import re
import time

monkey.patch_all()

url_list = list()


def my_downloader(son_url_list):
    """下载图片"""
    print('------------4')
    for url in son_url_list:
        print(url)
        file_name = str(int(time.time())) + ".jpg"  # 构造文件名
        request = urllib.request.urlopen(url)  # 打开网址
        print('--------------5')
        content = request.read()  # 读取网页信息
        with open(file_name, "wb") as f:  # 新建并打开本地文件
            f.write(content)  # 将网页信息写入

        time.sleep(1)


def create_gevent():
    """创建多个协程"""
    num = len(url_list)//4
    # 将列表分成多个子列表,让每个协程分别完成子列表里的任务
    print('------------------2')
    for i in range(4):
        if i <= 4:
            son_url_list = url_list[i*num:(i+1)*num]
            g = gevent.spawn(my_downloader, son_url_list)
            print('---------------------3')


def main():
    global url_list
    # 将网站上的信息取下来
    request = urllib.request.urlopen("https://www.douyu.com/directory")
    content = request.read()
    content = content.decode("utf-8")
    print(content)
    url_list = re.findall(r"https?://.+?gif", content)
    print('------------------------1')
    print(url_list)

    for i in range(2):
        num = len(url_list) // 2
        # 将列表分成多个子列表,让每个线程分别完成子列表里的任务
        for i in range(2):
            if i <= 2:
                thread_url_list = url_list[i * num:(i + 1) * num]
                thread = threading.Thread(target=create_gevent, args=thread_url_list)
                thread.start()


if __name__ == "__main__":
    main()



