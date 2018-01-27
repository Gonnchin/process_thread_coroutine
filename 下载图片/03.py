import gevent
from gevent import monkey
import urllib.request
import threading
import re
import time
import multiprocessing

monkey.patch_all()

url_list = list()


def my_downloader(son_url_list):
    """下载图片"""
    for url in son_url_list:
        # print(url)
        file_name = str(int(time.time())) + ".jpg"  # 构造文件名
        request = urllib.request.urlopen(url)  # 打开网址
        content = request.read()  # 读取网页信息
        with open(file_name, "wb") as f:  # 新建并打开本地文件
            f.write(content)  # 将网页信息写入

        time.sleep(1)


def create_thread():
    for i in range(10):
        thread = threading.Thread(target=create_gevent)
        thread.start()

def create_gevent():
    """创建多个协程"""
    list_num = 4  # 子列表的个数
    num = len(url_list)//4
    # 将列表分成多个子列表,让每个协程分别完成子列表里的任务
    for i in range(4):
        if i < list_num:
            son_url_list = url_list[i*num:(i+1)*num]
            g = gevent.spawn(my_downloader, son_url_list)
        elif i == list_num:
            son_url_list = url_list[i*num:]
            g = gevent.spawn(my_downloader, son_url_list)


def main():
    global url_list
    # 将网站上的信息取下来
    request = urllib.request.urlopen("https://www.douyu.com/directory")
    content = request.read()
    content = content.decode("utf-8")
    # print(content)
    url_list = re.findall(r'https?://.+?gif', content)
    # print(url_list)

    for i in range(2):
        process = multiprocessing.Process(target=create_thread)
        process.start()




