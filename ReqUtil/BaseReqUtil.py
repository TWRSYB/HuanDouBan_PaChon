import json
import traceback

import requests
from requests import Session

from Config.Config import OUTPUT_DIR
from Config.ReqConfig import HEADERS
from LogUtil.LogUtil import com_log
from MyUtil.MyUtil import filename_rm_invalid_chars
from MyUtil.RcdDataJson import rcd_data_json


class ReqType:
    def __init__(self, comment: str, fun='get', is_ajax=False):
        self.comment = comment
        self.fun = fun
        self.is_ajax = is_ajax


class BaseReqUtil:

    def __init__(self, session: Session = None):
        if session:
            self.session = session
        else:
            self.session = requests.Session()
            self.session.headers = HEADERS
            self.session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=60))
            self.session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=60))

    def try_req_times(self, url, req_type: ReqType, timeout=45, params=None, data=None, msg="", log=com_log,
                      test_times: int = 5):
        """
        尝试请求多次
        :param url: url
        :param req_type: 请求类型
        :param timeout: 超时时间(秒), 默认30
        :param params: 参数
        :param data: 数据
        :param msg: msg
        :param log: log
        :param test_times: 尝试次数, 默认5次
        :return: Response
        """
        # 尝试多次请求
        for i in range(test_times):
            res = None
            try:
                # 发送请求 ↓↓↓
                if req_type.fun == 'get':
                    res = self.session.get(url=url, params=params, timeout=timeout)
                elif req_type.fun == 'post':
                    res = self.session.post(url=url, params=params, data=data, timeout=timeout)
                else:
                    log.error(f"请求类型{req_type}的fun不再[get,post]内, 无法发送请求")
                    return
                # 发送请求 ↑↑↑

                # 请求结果处理 ↓↓↓
                # 请求成功 ↓↓↓
                if res.status_code == 200:
                    if not req_type.is_ajax:
                        return res
                    else:
                        dict_res = json.loads(res.text)
                        if dict_res.get('code') == 200:
                            return dict_res
                        elif i < test_times - 1:
                            log.warning(
                                f"{req_type.comment}请求成功, 但接口响应错误: 第{i + 1}次 msg: {msg} dict_res: {dict_res}"
                                f"\n\turl: {url}, params: {params}")
                        else:
                            log.error(
                                f"{req_type.comment}请求成功, 但接口响应错误!!! 第{i + 1}次 dict_res: {dict_res}"
                                f"\n\turl: {url}, params: {params}")
                # 请求成功 ↑↑↑

                # 请求失败但未达到尝试次数 ↓↓↓
                elif i < test_times - 1:
                    log.warning(f"{req_type.comment}请求响应错误: 第{i + 1}次 msg: {msg} res: {res}"
                                f"\n\turl: {url}, params: {params}")
                # 请求失败但未达到尝试次数 ↑↑↑

                # 请求失败且已经达到尝试次数 ↓↓↓
                # 响应状态码为 404 ↓↓↓
                elif res.status_code == 404:
                    log.error(f"{req_type.comment}请求响应错误404!!! 第{i + 1}次 msg: {msg} res: {res}"
                              f"\n\turl: {url}, params: {params}")
                    return res
                # 响应状态码为 404 ↑↑↑
                else:
                    log.error(f"{req_type.comment}请求响应错误!!! 第{i + 1}次 msg: {msg} res: {res}"
                              f"\n\turl: {url}, params: {params}")
                # 请求失败且已经达到尝试次数 ↑↑↑
                # 请求结果处理 ↑↑↑
            except Exception as e:
                if i < test_times - 1:
                    log.warning(f"{req_type.comment}请求出现异常: 第{i + 1}次 msg: {msg} res: {res}"
                                f"\n\t异常: {e}"
                                f"\n\turl: {url}, params: {params}")
                else:
                    log.error(f"{req_type.comment}请求出现异常!!! 第{i + 1}次 msg: {msg} res: {res}"
                              f"\n\t异常: {e}"
                              f"\n\turl: {url}, params: {params}"
                              # f"{traceback.format_exc()}"
                              )
