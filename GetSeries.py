import json
from typing import List

from Config import StartPoint
from Config.Config import URL_HOST_API, API_PATH_SERIES_LIST, JSON_DATA_SERIES
from Dao.SeriesDao import SeriesVo, SeriesDao
from LogUtil import LogUtil
from LogUtil.LogUtil import process_log, com_log
from MyUtil.RcdDataJson import rcd_data_json
from ReqUtil.ReqUtil import ReqUtil
from SpcUtil.SpcUtil import set_cid_for_vo

req_util = ReqUtil()

series_dao = SeriesDao()


def save_series(series_vo, cid):
    # 保存 series ↓↓↓
    insert_result = series_dao.insert(series_vo)
    if insert_result == 1:
        rcd_data_json.add_data_to_json(json_file=JSON_DATA_SERIES, data=series_vo, msg=f"厂商")
    elif isinstance(insert_result, tuple):
        series_vo = SeriesVo(*insert_result[0])
        set_cid_for_vo(series_vo, cid)
        update_result = series_dao.update_by_id(series_vo)
        if update_result == 1:
            rcd_data_json.update_data_to_json(json_file=JSON_DATA_SERIES, data=series_vo,
                                              update_by_list=[('id', series_vo.id)], msg=f"厂商")
    # 保存 series ↑↑↑


def get_series_page(page_num, cid) -> List[SeriesVo]:
    series_list: List[SeriesVo] = []
    params = {
        'cid': cid,  # 0-全部, 1-有码  2-无码  3-  10-国产  更多: 4-不知道(可以获取到一个3590,春菜はな) 5,6,7,8,9,11,12-没有
        'page': page_num,
        'pageSize': '50',

    }
    res = req_util.try_ajax_get_times(url=f"{URL_HOST_API}/{API_PATH_SERIES_LIST}", params=params,
                                      msg=f"获取 series列表: 第{page_num}页 cid: {cid}")
    if res:
        dict_res = json.loads(res.text)
        if dict_res.get('code') == 200:
            if str(dict_res.get('data').get('pageSize')) != '50':
                com_log.error(f"获取 series 列表, 响应的pageSize不是50: {dict_res}, 第{page_num}页 cid: {cid}")
            for i, dict_series in enumerate(dict_res.get('data').get('seriesList')):
                LogUtil.LOG_PROCESS_ACTOR_ORDER = i + 1
                LogUtil.LOG_PROCESS_MOVIE_PAGE = 0
                LogUtil.LOG_PROCESS_MOVIE_ORDER = 0
                if StartPoint.START_POINT_ACTOR_ORDER > 1:
                    process_log.process1(f"跳过 获取 series 信息: 第{i + 1}个 第{page_num}页")
                    StartPoint.START_POINT_ACTOR_ORDER -= 1
                    continue
                series_vo = SeriesVo(**dict_series)
                set_cid_for_vo(series_vo, cid)
                com_log.info(f"获取到 series: {series_vo}  cid: {cid} 第{page_num}页 第{i + 1}个")
                series_list.append(series_vo)
                save_series(series_vo, cid)
        else:
            com_log.error(f"获取 series列表接口报错: cid: {cid}"
                          f"\n\t接口返回: {dict_res}")

    return series_list


def get_cid_data(cid):
    """
    获取不同cid的数据
    :param cid:
    :return:
    """
    for i in range(1, 500):
        LogUtil.LOG_PROCESS_ACTOR_PAGE = i
        LogUtil.LOG_PROCESS_ACTOR_ORDER = 0
        LogUtil.LOG_PROCESS_MOVIE_PAGE = 0
        LogUtil.LOG_PROCESS_MOVIE_ORDER = 0
        if StartPoint.START_POINT_ACTOR_PAGE > 1:
            process_log.process1(f"跳过 series 列表: 第{i}页")
            StartPoint.START_POINT_ACTOR_PAGE -= 1
            continue
        process_log.process1(f"获取 series 列表: cid:{cid} 第{i}页 Start")
        series_list = get_series_page(i, cid)
        process_log.process1(f"获取 series 列表成功: cid:{cid} 第{i}页 结果: {series_list}")
        process_log.process1(f"获取 series 列表: cid:{cid} 第{i}页 End")
        if not series_list:
            process_log.process1(f"获取 series 列表 cid:{cid} 第{i}页 结果为空, 不再获取下一页")
            break


def start():
    for i, cid in enumerate([1, 2, 3, 4, 10]):  # 0-全部, 1-有码  2-无码  3-欧美  4-FC2  10-国产
        LogUtil.LOG_PROCESS_CID_ORDER = i + 1
        LogUtil.LOG_PROCESS_ACTOR_PAGE = 0
        LogUtil.LOG_PROCESS_ACTOR_ORDER = 0
        LogUtil.LOG_PROCESS_MOVIE_PAGE = 0
        LogUtil.LOG_PROCESS_MOVIE_ORDER = 0
        if StartPoint.START_POINT_CID_ORDER > 1:
            process_log.process1(f"跳过 获取cid的数据: cid:{cid}")
            StartPoint.START_POINT_CID_ORDER -= 1
            continue
        process_log.process1(f"获取cid的数据: cid:{cid} Start")
        get_cid_data(cid)
        process_log.process1(f"获取cid的数据: cid:{cid} End")


if __name__ == '__main__':
    start()
