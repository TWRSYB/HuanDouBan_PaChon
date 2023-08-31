import re
import threading
import traceback
from os import makedirs

import requests
from requests import Session

from Config.Config import OUTPUT_DIR, PIC_DIR_MOVIE_TRAILER_STUDIO_FANHAO
from Dao.MovieDao import MovieVo
from LogUtil.LogUtil import com_log

# 创建一个互斥锁
from MyUtil.MyUtil import filename_rm_invalid_chars
from MyUtil.RcdDataJson import rcd_data_json
from ReqUtil.BaseReqUtil import BaseReqUtil, ReqType

lock = threading.Lock()


class SaveTrailerUtil(BaseReqUtil):
    def __init__(self, session: Session = None, test_times: int = 5):
        super().__init__(session)
        if session:
            self.session = session
        else:
            self.session = requests.Session()
            self.session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=15, pool_maxsize=360))
            # self.session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=15, pool_maxsize=360))
        self.test_times = test_times

    def get_then_save_trailer_async(self, movie_vo: MovieVo, log):
        threading.Thread(target=self.get_then_save_trailer, args=(movie_vo, log)).start()

    def get_then_save_trailer(self, movie_vo: MovieVo, log=com_log):
        save_dir = f"{PIC_DIR_MOVIE_TRAILER_STUDIO_FANHAO}/{filename_rm_invalid_chars(movie_vo.studio_nm)}"
        save_name = f"{movie_vo.studio_nm}_{movie_vo.number}"
        url = movie_vo.trailer
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
        req_type = ReqType(comment='get预告片', fun='get', is_ajax=False)
        res = self.try_req_times(url=url, req_type=req_type, timeout=150, log=log)

        if res:
            try:
                suffix = url.split('.')[-1]
                chars_cant_in_filename = r'[\\/:"*?<>|]+'
                trailer_path = f"{save_dir}/{re.sub(chars_cant_in_filename, '-', str(save_name))}.{suffix}"
                with open(trailer_path, 'wb') as trailer:
                    trailer.write(res.content)
                log.info(f"保存预告片成功: {trailer_path}, url:{url}")
            except Exception as e:
                log.error(f"保存预告片发生异常:"
                          f"\n\t异常: {e}"
                          f"\n\tmovie: {movie_vo}"
                          f"{traceback.format_exc()}")
        elif res is not None and res.status_code == 404:
            with lock:
                rcd_data_json.append_data_to_txt(f"{OUTPUT_DIR}/jsondatas/trailer_remnant_404.txt",
                                                 data={'id': movie_vo.id, 'url': url, 'movie': movie_vo},
                                                 log=log)
            log.error(f"没有获取到预告片, 响应404:"
                      f"\n\tmovie: {movie_vo}"
                      f"\n\tsave_dir: {save_dir}, save_name: {save_name}")
        else:
            with lock:
                rcd_data_json.append_data_to_txt(f"{OUTPUT_DIR}/jsondatas/trailer_remnant.txt",
                                                 data={'id': movie_vo.id, 'url': url, 'movie': movie_vo},
                                                 log=log)
            log.error(f"没有获取到预告片:"
                      f"\n\tmovie: {movie_vo}"
                      f"\n\tsave_dir: {save_dir}, save_name: {save_name}")
