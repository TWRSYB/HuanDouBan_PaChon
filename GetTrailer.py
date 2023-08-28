import json
import threading
import time
from os import makedirs
from typing import List, Tuple

from Config import GlobleData
from Config.Config import PIC_DIR_MOVIE_TRAILER_STUDIO_FANHAO, OUTPUT_DIR
from Dao.MovieDao import MovieDao, MovieVo
from LogUtil import LogUtil
from LogUtil.LogUtil import process_log, async_log, com_log
from MyUtil.MyUtil import filename_rm_invalid_chars
from MyUtil.RcdDataJson import rcd_data_json
from ReqUtil.SaveTrailerUtil import SaveTrailerUtil

movie_dao = MovieDao()
save_trailer_util = SaveTrailerUtil()
lock = threading.Lock()


def get_movie_list(i):
    where = f"where trailer != ''"
    order_by = f"""order by 
            CASE 
                WHEN id REGEXP '^[0-9]+$' THEN CAST(id AS SIGNED)
                ELSE NULL
            END
        """
    limit = f"limit {i * 100},100"
    args = None
    select_result_tuple = movie_dao.select_with_condition(where=where, order_by=order_by, limit=limit, args=args)

    movie_list = [MovieVo(*result) for result in select_result_tuple]
    for movie_vo in movie_list:
        with lock:
            rcd_data_json.add_data_to_json_dict(f"{OUTPUT_DIR}/jsondatas/trailer_remnant.json",
                                                key=movie_vo.id, value=movie_vo,
                                                log=com_log)
            GlobleData.TRAILER_REMNANT[movie_vo.id] = movie_vo
            print(GlobleData.TRAILER_REMNANT)
        # save_trailer_util.get_then_save_trailer(movie_vo=movie_vo, log=async_log)
        save_trailer_util.get_then_save_trailer_async(movie_vo=movie_vo, log=async_log)
        time.sleep(1)  # 模拟耗时操作
    return movie_list


def start():
    for i in range(1000):
        LogUtil.LOG_PROCESS_MOVIE_PAGE = i + 1
        LogUtil.LOG_PROCESS_MOVIE_ORDER = 0
        process_log.process1(f"获取有预告片影片列表: 第{i * 100 + 1}-{(i + 1) * 100} Start")
        movie_list = get_movie_list(i)
        time.sleep(60)  # 模拟耗时操作
        process_log.process2(f"获取有预告片影片列表: 第{i * 100 + 1}-{(i + 1) * 100} 结果: {movie_list}")
        process_log.process2(f"截止获取下一页, 还有{len(GlobleData.TRAILER_REMNANT)}个预告片在请求中")
        process_log.process1(f"获取有预告片影片列表: 第{i * 100 + 1}-{(i + 1) * 100} End")
        if not movie_list:
            process_log.process1(f"获取有预告片影片列表: 第{i * 100 + 1}-{(i + 1) * 100} 结果为空, 不再获取下一页")
            break


def get_remnant():
    with open(file=r"D:\10.temp\06.黄豆瓣数据爬取\01.TEMP-wait10\jsondatas\trailer_remnant.txt", mode='r', encoding='utf-8') as f:
        lines = f.readlines()
        # print(lines)
        # print(len(lines))
    for i, line in enumerate(lines):
        LogUtil.LOG_PROCESS_MOVIE_ORDER = i+1
        # if i>0 and i % 100 == 0:
        #     time.sleep(100)  # 模拟耗时操作
        dict_line = eval(line)
        save_trailer_util.get_then_save_trailer_async(url=dict_line['url'], save_dir=dict_line['save_dir'], save_name=dict_line['save_name'], movie_vo=None, log=async_log)



if __name__ == '__main__':
    # start()
    get_remnant()
