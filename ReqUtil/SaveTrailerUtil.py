import re
import threading
import time
import traceback
from os import makedirs
from typing import List, Tuple

import requests
from requests import Session

from Config import GlobleData
from Config.Config import OUTPUT_DIR, PIC_DIR_MOVIE_TRAILER_STUDIO_FANHAO
from Dao.MovieDao import MovieVo
from LogUtil.LogUtil import com_log

# 创建一个互斥锁
from MyUtil.MyUtil import filename_rm_invalid_chars
from MyUtil.RcdDataJson import rcd_data_json

lock = threading.Lock()


class SaveTrailerUtil:
    def __init__(self, session: Session = None, test_times: int = 5):
        if session:
            self.session = session
        else:
            self.session = requests.Session()
            # self.session.timeout = 25  # 设置超时时间为10秒
            self.session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=15, pool_maxsize=360))
            # self.session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=15, pool_maxsize=360))
        self.test_times = test_times

    def get_then_save_trailer_async(self, url, save_dir, save_name, movie_vo: MovieVo, log):
        threading.Thread(target=self.get_then_save_trailer, args=(url, save_dir, save_name, movie_vo, log)).start()

    def get_then_save_trailer(self, url, save_dir, save_name,  movie_vo: MovieVo, log=com_log):
        # save_dir = f"{PIC_DIR_MOVIE_TRAILER_STUDIO_FANHAO}/{filename_rm_invalid_chars(movie_vo.studio_nm)}"
        # save_name = f"{movie_vo.studio_nm}_{movie_vo.number}"
        # url = movie_vo.trailer
        makedirs(save_dir, exist_ok=True)
        invalid_url_list = []
        if url in invalid_url_list:
            log.warning(f"预告片连接无效: url: {url}")
            return

        # 如果url中再次嵌套了http(s)://, 则取嵌套的url
        match_nest_http = re.match(r'http.+(http[s]?://.+)', url)
        if match_nest_http:
            log.warning(f"发现了嵌套url的情况: url: {url}")
            url = match_nest_http.group(1)


        res = self.try_get_trailer_times(url=url, log=log)

        if res:
            try:
                suffix = url.split('.')[-1]
                chars_cant_in_filename = r'[\\/:"*?<>|]+'
                trailer_path = f"{save_dir}/{re.sub(chars_cant_in_filename, '-', str(save_name))}.{suffix}"
                with open(trailer_path, 'wb') as trailer:
                    trailer.write(res.content)
                log.info(f"保存预告片成功: {trailer_path}, url:{url}")
                # with lock:
                #     rcd_data_json.delete_data_from_json_dict(f"{OUTPUT_DIR}/jsondatas/trailer_remnant.json",
                #                                              delete_key=movie_vo.id,
                #                                              log=com_log)
                #     print(GlobleData.TRAILER_REMNANT)
                #     del GlobleData.TRAILER_REMNANT[movie_vo.id]
                return True
            except Exception as e:
                log.error(f"保存预告片发生异常:"
                          f"\n\t异常: {e}"
                          f"\n\tmovie: {movie_vo}"
                          f"{traceback.format_exc()}")
        elif res is not None and res.status_code == 404:
            with lock:
                rcd_data_json.append_data_to_txt(f"{OUTPUT_DIR}/jsondatas/trailer_remnant_404.txt",
                                                 data={'url': url, 'save_dir': save_dir, 'save_name': save_name},
                                                 log=log)
            log.error(f"没有获取到预告片, 响应404:"
                      f"\n\tmovie: {movie_vo}"
                      f"\n\tsave_dir: {save_dir}, save_name: {save_name}")
        else:
            with lock:
                rcd_data_json.append_data_to_txt(f"{OUTPUT_DIR}/jsondatas/trailer_remnant.txt",
                                                 data={'url': url, 'save_dir': save_dir, 'save_name': save_name},
                                                 log=log)
            log.error(f"没有获取到预告片:"
                      f"\n\tmovie: {movie_vo}"
                      f"\n\tsave_dir: {save_dir}, save_name: {save_name}")

    def try_get_trailer_times(self, url, msg="", log=com_log):
        for i in range(self.test_times):
            res = None
            try:
                res = self.session.get(url=url, timeout=200)
                if res.status_code == 200:
                    log.info(f"get预告片成功: {msg}, url: {url}")
                    return res
                if i < self.test_times - 1:
                    log.warning(f"get预告片响应错误: 第{i + 1}次 msg: {msg} res: {res}"
                                f"\n\turl: {url}")
                else:
                    log.error(f"get预告片响应错误!!! 第{i + 1}次 msg: {msg} res: {res}"
                              f"\n\turl: {url}")
                    if res.status_code == 404:
                        log.error(f"get预告片响应404: {msg}, url: {url}")
                        return res
            except Exception as e:
                if i < self.test_times - 1:
                    log.warning(f"get预告片出现异常: 第{i + 1}次 msg: {msg} res: {res}"
                                f"\n\t异常: {e}"
                                f"\n\turl: {url}")
                else:
                    log.error(f"get预告片出现异常!!! 第{i + 1}次 msg: {msg} res: {res}"
                              f"\n\t异常: {e}"
                              f"\n\turl: {url}")