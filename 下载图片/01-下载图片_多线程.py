import gevent
from gevent import monkey
import urllib.request
import threading
import re
import time

monkey.patch_all()

request = urllib.request.urlopen("https://www.douyu.com/directory")
content = request.read()
content = content.decode()
print(content)
url_list = re.findall(r"https?://.+?gif", content)
print(url_list)


def my_downloader(url):
    #print("----------", url)
    file_name = str(int(time.time())) + ".gif"
    print("---------", url)
    request = urllib.request.urlopen(url)
    content = request.read()
    with open(file_name, "wb") as f:
        f.write(content)

    time.sleep(1)


for url in url_list:
    thread = threading.Thread(target=my_downloader, args=(url,))
    thread.start()

# for url in url_list:
#     gevent.spawn(my_downloader, url)



