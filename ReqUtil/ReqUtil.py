import json
import traceback

import requests
from requests import Session

from Config.Config import HEADERS, OUTPUT_DIR
from LogUtil.LogUtil import com_log
from MyUtil.MyUtil import filename_rm_invalid_chars
from MyUtil.RcdDataJson import rcd_data_json


class ReqUtil:
    def __init__(self, session: Session = None, test_times: int = 5):
        if session:
            self.session = session
        else:
            self.session = requests.Session()
            self.session.headers = HEADERS
            self.session.timeout = 15  # 设置超时时间为10秒
            self.session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=60))
            self.session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=60))
        self.test_times = test_times

    def try_get_req_times(self, url, params=None, msg="", log=com_log):
        for i in range(self.test_times):
            res = None
            try:
                res = self.session.get(url=url, params=params)
                if res.status_code == 200:
                    log.info(
                        f"get请求成功: {msg}, url: {url}, params: {params} res: {res}")
                    return res
                if i < self.test_times - 1:
                    log.warning(f"get请求响应错误: 第{i + 1}次 msg: {msg} res: {res}"
                                f"\n\turl: {url}, params: {params}")
                else:
                    log.error(f"get请求响应错误!!! 第{i + 1}次 msg: {msg}"
                              f"\n\turl: {url}, params: {params}")
            except Exception as e:
                if i < self.test_times - 1:
                    log.warning(f"get请求出现异常: 第{i + 1}次 msg: {msg} res: {res}"
                                f"\n\t异常: {e}"
                                f"\n\turl: {url}, params: {params}")
                else:
                    log.error(f"get请求出现异常!!! 第{i + 1}次 msg: {msg} res: {res}"
                              f"\n\t异常: {e}"
                              f"\n\turl: {url}, params: {params}")

    def try_ajax_get_times(self, url, params=None, msg="", log=com_log):
        for i in range(self.test_times):
            res = None
            try:
                res = self.session.get(url=url, params=params)
                if res.status_code == 200:
                    dict_res = json.loads(res.text)
                    if dict_res.get('code') == 200:
                        rcd_data_json.append_data_to_txt(
                            txt_file=f"{OUTPUT_DIR}/jsondatas/ajax_get_{filename_rm_invalid_chars(url)}.txt",
                            data={'params': params, 'dict_res': dict_res}, msg="ajax_get_接口响应成功", log=log)
                        log.info(
                            f"ajax get请求成功: {msg}, url: {url}, params: {params}"
                            f" res: {res}")
                        return res
                    else:
                        if i < self.test_times - 1:
                            log.warning(
                                f"ajax get请求响应错误: 第{i + 1}次 msg: {msg} res: {res}"
                                f"\n\turl: {url}, params: {params}")
                        else:
                            log.error(f"ajax get请求响应错误!!! 第{i + 1}次 msg: {msg}"
                                      f"\n\turl: {url}, params: {params}")
            except Exception as e:
                if i < self.test_times - 1:
                    log.warning(f"ajax get请求出现异常: 第{i + 1}次 msg: {msg} res: {res}"
                                f"\n\t异常: {e}"
                                f"\n\turl: {url}, params: {params}")
                else:
                    log.error(f"ajax get请求出现异常!!! 第{i + 1}次 msg: {msg} res: {res}"
                              f"\n\t异常: {e}"
                              f"\n\turl: {url}, params: {params}"
                              f"{traceback.format_exc()}")

    def try_ajax_post_times(self, url, params=None, data=None, msg="", log=com_log):
        for i in range(self.test_times):
            res = None
            try:
                res = self.session.post(url=url, params=params, data=data)
                if res.status_code == 200:
                    dict_res = json.loads(res.text)
                    rcd_data_json.append_data_to_txt(
                        txt_file=f"{OUTPUT_DIR}/jsondatas/ajax_post_{filename_rm_invalid_chars(url)}.txt",
                        data={'params': params, 'data': data, 'dict_res': dict_res}, msg="ajax_post_接口响应成功", log=log
                    )
                    if dict_res.get('code') == 200:
                        log.info(
                            f"ajax post请求成功: {msg}, url: {url}, params: {params}, data: {data},"
                            f" res: {res}")
                        return res
                    else:
                        if i < self.test_times - 1:
                            log.warning(f"ajax post请求成功, 但接口响应错误: 第{i + 1}次 msg: {msg}"
                                        f"\n\t{f'dict_res: {dict_res}' if res else ''}"
                                        f"\n\turl: {url}, params: {params}, data: {data}")
                        else:
                            log.error(f"ajax post请求成功, 但接口响应错误!!! 第{i + 1}次 msg: {msg}"
                                      f"\n\t{f'dict_res: {dict_res}' if res else ''}"
                                      f"\n\turl: {url}, params: {params}, data: {data}")
                if i < self.test_times - 1:
                    log.warning(f"ajax post请求响应错误: 第{i + 1}次 msg: {msg} res: {res}"
                                f"\n\turl: {url}, params: {params}, data: {data}")
                else:
                    log.error(f"ajax post请求响应错误!!! 第{i + 1}次 msg: {msg}"
                              f"\n\turl: {url}, params: {params}, data: {data}")
            except Exception as e:
                if i < self.test_times - 1:
                    log.warning(f"ajax post请求出现异常: 第{i + 1}次 msg: {msg} res: {res}"
                                f"\n\t异常: {e}"
                                f"\n\turl: {url}, params: {params}, data: {data}")
                else:
                    log.error(f"ajax post请求出现异常!!! 第{i + 1}次 msg: {msg} res: {res}"
                              f"\n\t异常: {e}"
                              f"\n\turl: {url}, params: {params}, data: {data}")

    def get_once(self, url, params=None, msg="", log=com_log):
        res = None
        try:
            res = self.session.get(url=url, params=params)
            if res.status_code == 200:
                log.info(f"get请求成功: {msg}, url: {url}, params: {params} res: {res}")
                return res
            else:
                log.error(f"get请求响应错误!!! msg: {msg} res: {res}"
                          f"\n\turl: {url}, params: {params}")
        except Exception as e:
            log.error(f"get请求出现异常!!! msg: {msg}"
                      f"\n\t异常: {e}"
                      f"\n\turl: {url}, params: {params} res: {res}")
