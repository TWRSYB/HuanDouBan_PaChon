import requests
from requests import Session

from Config.Config import OUTPUT_DIR
from Config.ReqConfig import HEADERS
from LogUtil.LogUtil import com_log
from MyUtil.MyUtil import filename_rm_invalid_chars
from MyUtil.RcdDataJson import rcd_data_json
from ReqUtil.BaseReqUtil import BaseReqUtil, ReqType


class ReqUtil(BaseReqUtil):

    def __init__(self, session: Session = None):
        super().__init__(session)
        if session:
            self.session = session
        else:
            self.session = requests.Session()
            self.session.headers = HEADERS
            self.session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=60))
            self.session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=60))

    def try_get_times(self, url, timeout=45, params=None, msg="", log=com_log, test_times: int = 5):
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
        req_type = ReqType(comment='get', fun='get', is_ajax=False)
        res = self.try_req_times(url=url, req_type=req_type, timeout=timeout, params=params, msg=msg, log=log,
                                 test_times=test_times)
        if res:
            log.info(
                f"{req_type.comment}请求成功: {msg}, url: {url}, params: {params} res: {res}")
            return res

    def try_ajax_get_times(self, url, timeout=45, params=None, msg="", log=com_log, test_times: int = 5):
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
        req_type = ReqType(comment='ajax_get', fun='get', is_ajax=True)
        dict_res = self.try_req_times(url, req_type=req_type, timeout=timeout, params=params, msg=msg, log=log,
                                      test_times=test_times)
        if dict_res:
            rcd_data_json.append_data_to_txt(
                txt_file=f"{OUTPUT_DIR}/Ajax_res/ajax_get_{filename_rm_invalid_chars(url)}.txt",
                data={'params': params, 'dict_res': dict_res}, msg=f"{req_type.comment}接口响应成功",
                log=log)
            log.info(
                f"{req_type.comment}成功: {msg}, url: {url}, params: {params} dict_res: {dict_res}")
            return dict_res

    def try_ajax_post_times(self, url, timeout=45, params=None, data=None, msg="", log=com_log, test_times: int = 5):
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
        req_type = ReqType(comment='ajax_post', fun='post', is_ajax=True)
        dict_res = self.try_req_times(url, req_type=req_type, timeout=timeout, params=params, data=data, msg=msg,
                                      log=log,
                                      test_times=test_times)
        if dict_res:
            rcd_data_json.append_data_to_txt(
                txt_file=f"{OUTPUT_DIR}/Ajax_res/ajax_post_{filename_rm_invalid_chars(url)}.txt",
                data={'params': params, 'data': data, 'dict_res': dict_res},
                msg=f"{req_type.comment}接口响应成功",
                log=log
            )
            log.info(
                f"{req_type.comment}成功: {msg}, url: {url}, params: {params}, data: {data}, dict_res: {dict_res}")
            return dict_res
