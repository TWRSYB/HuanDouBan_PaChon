import threading
import time
import concurrent.futures


def worker():
    """子线程函数"""
    print("Worker started")
    # do some work...
    time.sleep(5)  # 模拟耗时操作
    print("Worker finished")


i2_list = []


def get_movie_detail_async(i):
    """获取影片详情"""
    print(f"Starting thread for movie {i}")
    # do some work...
    t = threading.Thread(target=worker)
    t.start()
    print(f"Thread for movie {i} started")
    return i * 2


# 创建线程池
with concurrent.futures.ThreadPoolExecutor() as executor:
    # 开启多个线程获取影片详情
    futures = [executor.submit(get_movie_detail_async, i=i) for i in range(10)]

print("Main thread resumed")

# 处理结果
for future in concurrent.futures.as_completed(futures):
    i2_list.append(future.result())

print(i2_list)
