import json

from Config import StartPoint
from Config.Config import JSON_DATA_LABEL
from Config.ReqConfig import URL_HOST_API, API_PATH_LABEL_LIST
from Dao.LabelDao import LabelVo, LabelDao
from LogUtil import LogUtil
from LogUtil.LogUtil import process_log, com_log
from MyUtil.RcdDataJson import rcd_data_json
from ReqUtil.ReqUtil import ReqUtil
from SpcUtil.SpcUtil import set_cid_for_vo

req_util = ReqUtil()

label_dao = LabelDao()


def save_label(parent_id, dict_label, cid):
    label_vo: LabelVo = LabelVo(id=dict_label['id'], name=dict_label['name'], parent_id=parent_id)
    set_cid_for_vo(label_vo, cid)

    # 保存Label ↓↓↓
    insert_result = label_dao.insert(label_vo)
    # 插入成功则将数据添加到JSON文件中
    if insert_result == 1:
        rcd_data_json.add_data_to_json_list(json_file=JSON_DATA_LABEL, data=label_vo)
    # 插入时数据已经存在则更新数据
    elif isinstance(insert_result, tuple):
        label_vo = LabelVo(*insert_result[0])
        set_cid_for_vo(label_vo, cid)
        update_result = label_dao.update_by_id(label_vo)
        if update_result == 1:
            rcd_data_json.update_data_to_json(json_file=JSON_DATA_LABEL, data=label_vo,
                                              update_by_list=[('id', label_vo.id)])

    # 保存Label ↑↑↑

    # 保存子标签 ↓↓↓
    if dict_label.get('children'):
        for i, child in enumerate(dict_label.get('children')):
            LogUtil.LOG_PROCESS_ACTOR_ORDER = i + 1
            LogUtil.LOG_PROCESS_MOVIE_PAGE = 0
            LogUtil.LOG_PROCESS_MOVIE_ORDER = 0
            if StartPoint.START_POINT_ACTOR_ORDER > 1:
                process_log.process1(f"跳过 获取 子Label 信息: 第{i + 1}个, 父Label: {dict_label['name']}")
                StartPoint.START_POINT_ACTOR_ORDER -= 1
                continue
            save_label(parent_id=label_vo.id, dict_label=child, cid=cid)
    # 保存子标签 ↑↑↑


def get_label_page(cid):
    params = {
        'cid': cid,
    }
    dict_res = req_util.try_ajax_get_times(url=f"{URL_HOST_API}/{API_PATH_LABEL_LIST}", params=params,
                                           msg=f"获取Label列表: cid: {cid}")
    if dict_res:
        for i, dict_label in enumerate(dict_res.get('data')):
            LogUtil.LOG_PROCESS_ACTOR_PAGE = i
            LogUtil.LOG_PROCESS_ACTOR_ORDER = 0
            LogUtil.LOG_PROCESS_MOVIE_PAGE = 0
            LogUtil.LOG_PROCESS_MOVIE_ORDER = 0
            if StartPoint.START_POINT_ACTOR_PAGE > 1:
                process_log.process1(f"跳过 获取 父Label 及其子元素: Label: {dict_label['name']}")
                StartPoint.START_POINT_ACTOR_PAGE -= 1
                continue
            save_label('无', dict_label, cid)
    else:
        com_log.error(f"获取Label列表失败: cid: {cid}")


def get_cid_data(cid):
    get_label_page(cid)
    process_log.process1(f"获取 Label 列表完成: cid: {cid}")


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
