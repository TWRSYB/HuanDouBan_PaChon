import json
import traceback

import requests
from requests import Session

from Config.Config import HEADERS, OUTPUT_DIR
from LogUtil.LogUtil import com_log
from MyUtil.MyUtil import filename_rm_invalid_chars
from MyUtil.RcdDataJson import rcd_data_json


class ReqUtil:

    req_type_annotations = {1: 'get', 2: 'ajax_get', 3: 'ajax_post'}

    def __init__(self, session: Session = None):
        if session:
            self.session = session
        else:
            self.session = requests.Session()
            self.session.headers = HEADERS
            self.session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=60))
            self.session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=60))

    def try_get_times(self, url, timeout=30, params=None, msg="", log=com_log, test_times: int = 5):
        """
        发送普通get请求
        :param url: url
        :param timeout: 超时时间(秒), 默认30
        :param params: 参数
        :param msg: msg
        :param log: log
        :param test_times: 尝试次数, 默认5次
        :return: Response
        """
        req_type = 1
        res = self.__try_req_times(url=url, req_type=req_type, timeout=timeout, params=params, msg=msg, log=log,
                                   test_times=test_times)
        if res:
            log.info(
                f"{self.req_type_annotations[req_type]}请求成功: {msg}, url: {url}, params: {params} res: {res}")
            return res

    def try_ajax_get_times(self, url, timeout=30, params=None, msg="", log=com_log, test_times: int = 5):
        """
        发送Ajax get请求
        :param url: url
        :param timeout: 超时时间(秒), 默认30
        :param params: 参数
        :param msg: msg
        :param log: log
        :param test_times: 尝试次数, 默认5次
        :return: Dict
        """
        req_type = 2
        res = self.__try_req_times(url, req_type=req_type, timeout=timeout, params=params, msg=msg, log=log,
                                   test_times=test_times)
        if res:
            dict_res = json.loads(res.text)
            rcd_data_json.append_data_to_txt(
                txt_file=f"{OUTPUT_DIR}/Ajax_res/ajax_get_{filename_rm_invalid_chars(url)}.txt",
                data={'params': params, 'dict_res': dict_res}, msg=f"{self.req_type_annotations[req_type]}接口响应成功",
                log=log)
            log.info(
                f"{self.req_type_annotations[req_type]}成功: {msg}, url: {url}, params: {params} res: {res}")
            return dict_res

    def try_ajax_post_times(self, url, timeout=30, params=None, data=None, msg="", log=com_log, test_times: int = 5):
        """
        发送Ajax post请求
        :param url: url
        :param timeout: 超时时间(秒), 默认30
        :param params: 参数
        :param data: 数据
        :param msg: msg
        :param log: log
        :param test_times: 尝试次数, 默认5次
        :return: Dict
        """
        req_type = 3
        res = self.__try_req_times(url, req_type=req_type, timeout=timeout, params=params, data=data, msg=msg, log=log,
                                   test_times=test_times)
        if res:
            dict_res = json.loads(res.text)
            rcd_data_json.append_data_to_txt(
                txt_file=f"{OUTPUT_DIR}/jsondatas/ajax_post_{filename_rm_invalid_chars(url)}.txt",
                data={'params': params, 'data': data, 'dict_res': dict_res},
                msg=f"{self.req_type_annotations[req_type]}接口响应成功",
                log=log
            )
            log.info(
                f"{self.req_type_annotations[req_type]}成功: {msg}, url: {url}, params: {params}, data: {data}, res: {res}")
            return dict_res

    def __try_req_times(self, url, req_type, timeout=30, params=None, data=None, msg="", log=com_log,
                        test_times: int = 5):
        """
        尝试请求多次
        :param url: url
        :param req_type: 请求类型 {1: 'get', 2: 'ajax_get', 3: 'ajax_post'}
        :param timeout: 超时时间(秒), 默认30
        :param params: 参数
        :param data: 数据
        :param msg: msg
        :param log: log
        :param test_times: 尝试次数, 默认5次
        :return: Response
        """
        for i in range(test_times):
            res = None
            try:
                if req_type in [1, 2]:
                    res = self.session.get(url=url, params=params, timeout=timeout)
                elif req_type in [3]:
                    res = self.session.post(url=url, params=params, data=data, timeout=timeout)
                if res.status_code == 200 and req_type in [1]:
                    return res
                if res.status_code == 200 and req_type in [2, 3] and json.loads(res.text).get('code') == 200:
                    return res
                if i < test_times - 1:
                    log.warning(f"{self.req_type_annotations[req_type]}请求响应错误: 第{i + 1}次 msg: {msg} res: {res}"
                                f"\n\turl: {url}, params: {params}")
                else:
                    if res.status_code == 404:
                        log.error(f"{self.req_type_annotations[req_type]}请求响应错误404!!! 第{i + 1}次 msg: {msg}"
                                  f"\n\turl: {url}, params: {params}")
                        return res
                    log.error(f"{self.req_type_annotations[req_type]}请求响应错误!!! 第{i + 1}次 msg: {msg}"
                              f"\n\turl: {url}, params: {params}")
            except Exception as e:
                if i < test_times - 1:
                    log.warning(f"{self.req_type_annotations[req_type]}请求出现异常: 第{i + 1}次 msg: {msg} res: {res}"
                                f"\n\t异常: {e}"
                                f"\n\turl: {url}, params: {params}")
                else:
                    log.error(f"{self.req_type_annotations[req_type]}请求出现异常!!! 第{i + 1}次 msg: {msg} res: {res}"
                              f"\n\t异常: {e}"
                              f"\n\turl: {url}, params: {params}"
                              f"{traceback.format_exc()}")
