import json
from typing import List

from Config import StartPoint
from Config.Config import JSON_DATA_STUDIO
from Config.ReqConfig import URL_HOST_API, API_PATH_STUDIO_LIST
from Dao.StudioDao import StudioVo, StudioDao
from LogUtil import LogUtil
from LogUtil.LogUtil import process_log, com_log
from MyUtil.RcdDataJson import rcd_data_json
from ReqUtil.ReqUtil import ReqUtil
from SpcUtil.SpcUtil import set_cid_for_vo

req_util = ReqUtil()

studio_dao = StudioDao()


def save_studio(studio_vo, cid):
    # 保存 studio ↓↓↓
    insert_result = studio_dao.insert(studio_vo)
    if insert_result == 1:
        rcd_data_json.add_data_to_json_list(json_file=JSON_DATA_STUDIO, data=studio_vo, msg=f"厂商")
    elif isinstance(insert_result, tuple):
        studio_vo = StudioVo(*insert_result[0])
        set_cid_for_vo(studio_vo, cid)
        update_result = studio_dao.update_by_id(studio_vo)
        if update_result == 1:
            rcd_data_json.update_data_to_json(json_file=JSON_DATA_STUDIO, data=studio_vo,
                                              update_by_list=[('id', studio_vo.id)], msg=f"厂商")
    # 保存 studio ↑↑↑


def get_studio_page(page_num, cid) -> List[StudioVo]:
    studio_list: List[StudioVo] = []
    params = {
        'cid': cid,  # 0-全部, 1-有码  2-无码  3-  10-国产  更多: 4-不知道(可以获取到一个3590,春菜はな) 5,6,7,8,9,11,12-没有
        'page': page_num,
        'pageSize': '50',

    }
    dict_res = req_util.try_ajax_get_times(url=f"{URL_HOST_API}/{API_PATH_STUDIO_LIST}", params=params,
                                           msg=f"获取 studio列表: 第{page_num}页 cid: {cid}")
    if dict_res:
        if str(dict_res.get('data').get('pageSize')) != '50':
            com_log.error(f"获取 studio 列表, 响应的pageSize不是50: {dict_res}, 第{page_num}页 cid: {cid}")
        for i, dict_studio in enumerate(dict_res.get('data').get('filmCompaniesList')):
            LogUtil.LOG_PROCESS_ACTOR_ORDER = i + 1
            LogUtil.LOG_PROCESS_MOVIE_PAGE = 0
            LogUtil.LOG_PROCESS_MOVIE_ORDER = 0
            if StartPoint.START_POINT_ACTOR_ORDER > 1:
                process_log.process1(f"跳过 获取 studio 信息: 第{i + 1}个 第{page_num}页")
                StartPoint.START_POINT_ACTOR_ORDER -= 1
                continue
            studio_vo = StudioVo(**dict_studio)
            set_cid_for_vo(studio_vo, cid)
            com_log.info(f"获取到 studio: {studio_vo}  cid: {cid} 第{page_num}页 第{i + 1}个")
            studio_list.append(studio_vo)
            save_studio(studio_vo, cid)
    else:
        com_log.error(f"获取 studio列表失败: 第{page_num}页 cid: {cid}")

    return studio_list


def get_cid_data(cid):
    """
    获取不同cid的数据
    :param cid:
    :return:
    """
    for i in range(1, 200):
        LogUtil.LOG_PROCESS_ACTOR_PAGE = i
        LogUtil.LOG_PROCESS_ACTOR_ORDER = 0
        LogUtil.LOG_PROCESS_MOVIE_PAGE = 0
        LogUtil.LOG_PROCESS_MOVIE_ORDER = 0
        if StartPoint.START_POINT_ACTOR_PAGE > 1:
            process_log.process1(f"跳过 studio 列表: 第{i}页")
            StartPoint.START_POINT_ACTOR_PAGE -= 1
            continue
        process_log.process1(f"获取 studio 列表: cid:{cid} 第{i}页 Start")
        studio_list = get_studio_page(i, cid)
        process_log.process1(f"获取 studio 列表成功: cid:{cid} 第{i}页 结果: {studio_list}")
        process_log.process1(f"获取 studio 列表: cid:{cid} 第{i}页 End")
        if not studio_list:
            process_log.process1(f"获取 studio 列表 cid:{cid} 第{i}页 结果为空, 不再获取下一页")
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
