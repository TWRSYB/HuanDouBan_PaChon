import re
import threading
import traceback
from typing import List, Tuple

import requests
from requests import Session

from LogUtil.LogUtil import com_log
from ReqUtil.BaseReqUtil import BaseReqUtil, ReqType
from ReqUtil.ReqUtil import ReqUtil


class SavePicUtil(BaseReqUtil):
    def __init__(self, session: Session = None, test_times: int = 5):
        super().__init__(session)
        if session:
            self.session = session
        else:
            self.session = requests.Session()
            # self.session.timeout = 25  # 设置超时时间为10秒
            self.session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=15, pool_maxsize=360))
            self.session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=15, pool_maxsize=360))
        self.test_times = test_times

    def save_pic(self, url, save_dir, save_name, msg='', is_async=False, timeout=45, test_times=5, log=com_log):
        """
        保存图片
        :param test_times:
        :param timeout:
        :param url: 图片url
        :param save_dir: 保存目录
        :param save_name: 保存图片名称
        :param msg: 消息
        :param is_async: 是否异步获取图片
        :param log: 日志输出位置
        :return: None
        """
        places: List[Tuple[str, str]] = [(save_dir, save_name)]
        self.save_pic_multi_places(url, places, msg, is_async, timeout, test_times, log)

    def save_pic_multi_places(self, url, places: List[Tuple[str, str]], msg='', is_async=False, timeout=45, test_times=5, log=com_log):
        """
        保存图片到多个目录
        :param test_times:
        :param timeout:
        :param url: 图片url
        :param places: 保存的地点
        :param msg: 消息
        :param is_async: 是否异步获取图片
        :param log: 日志输出位置
        :return: None
        """
        if is_async:
            threading.Thread(target=self.__get_then_save_pic, args=(url, places, timeout, test_times, msg, log)).start()
        else:
            self.__get_then_save_pic(url, places, timeout, test_times, msg, log)

    def __get_then_save_pic(self, url: str, places, timeout, test_times, msg, log):
        """
        获取然后保存图片
        :param url: 图片url
        :param places: 保存地点
        :param msg: msg
        :param log: 日志输出位置
        :return: None
        """
        invalid_url_list = []
        if url in invalid_url_list:
            log.warning(f"图片连接无效: url: {url}, msg: {msg}")
            return

        # 如果url中再次嵌套了http(s)://, 则取嵌套的url
        match_nest_http = re.match(r'http.+(http[s]?://.+)', url)
        if match_nest_http:
            log.warning(f"发现了嵌套url的情况: url: {url}")
            url = match_nest_http.group(1)

        match_invalid_subfix = re.match(r'(.+\.jpg)\?\d+$', url)
        if match_invalid_subfix:
            log.warning(f"发现了url以.jpg?xx结尾的情况: url: {url}")
            url = match_invalid_subfix.group(1)

        # res = self.try_get_pic_times(url=url, msg=msg, log=log)
        req_type = ReqType(comment='get图片', fun='get', is_ajax=False)
        res = self.try_req_times(url=url, req_type=req_type, timeout=timeout, msg=msg, log=log,
                                 test_times=test_times)
        # # 图片获取失败, 尝试别的一些办法
        # if not res:
        #     # 尝试替换https为http
        #     if url.startswith('https:'):
        #         test_url = url.replace('https:', 'http:')
        #         log.error(f"图片请求失败, 尝试https-->http重试 url: {url}"
        #                   f"\n\ttest_url: {test_url}")
        #         res = self.try_get_pic_times(url=test_url, msg=msg, log=log)
        #         if res:
        #             log.error(f"图片使用http请求成功: test_url: {test_url}")

        if res:
            try:
                suffix = url.split('.')[-1]
                for place in places:
                    chars_cant_in_filename = r'[\\/:"*?<>|]+'
                    pic_path = f"{place[0]}/{re.sub(chars_cant_in_filename, '-', str(place[1]))}.{suffix}"
                    with open(pic_path, 'wb') as pic:
                        pic.write(res.content)
                    log.info(f"保存图片成功: {pic_path}, msg: {msg}, url:{url}")
            except Exception as e:
                log.error(f"保存图片发生异常: msg: {msg}"
                          f"\n\t异常: {e}"
                          f"\n\turl:{url}"
                          f"{traceback.format_exc()}")
