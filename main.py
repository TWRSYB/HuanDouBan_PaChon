import json
import time
from typing import List, Tuple

from Config import StartPoint
from Config.Config import URL_HOST_API, API_PATH_ACTOR_LIST, JSON_DATA_ACTOR, \
    PIC_DIR_ACTOR_AVATAR, API_PATH_ACTOR_DETAIL
from Dao.ActorDao import ActorVo, ActorDao
from GetMovie import get_actor_movie
from LogUtil import LogUtil
from LogUtil.LogUtil import process_log, com_log
from MyUtil.RcdDataJson import rcd_data_json
from ReqUtil.ReqUtil import ReqUtil
from ReqUtil.SavePicUtil import SavePicUtil
from SpcUtil.SpcUtil import set_cid_for_vo

req_util = ReqUtil()
save_pic_util = SavePicUtil()

actor_dao = ActorDao()


def get_actor_list_page(cid, page_num) -> List[ActorVo]:
    actor_list: List[ActorVo] = []
    params = {
        'cid': cid,
        'page': page_num,
        'pageSize': '50',

    }
    res = req_util.try_ajax_get_times(url=f"{URL_HOST_API}{API_PATH_ACTOR_LIST}", params=params,
                                      msg=f"获取演员列表: 第{page_num}页")
    if res:
        dict_res = json.loads(res.text)
        print(dict_res)

        if dict_res.get('code') == 200:
            if str(dict_res.get('data').get('pageSize')) != '50':
                com_log.error(f"获取演员列表, 响应的pageSize不是50: {dict_res}, 第{page_num}页 cid: {cid}")
            for i, dict_actor in enumerate(dict_res.get('data').get('actorList')):
                LogUtil.LOG_PROCESS_ACTOR_ORDER = i + 1
                LogUtil.LOG_PROCESS_MOVIE_PAGE = 0
                LogUtil.LOG_PROCESS_MOVIE_ORDER = 0
                if StartPoint.START_POINT_ACTOR_ORDER > 1:
                    process_log.process1(f"跳过 获取演员信息: 第{i + 1}个 第{page_num}页")
                    StartPoint.START_POINT_ACTOR_ORDER -= 1
                    continue
                process_log.process2(f"获取演员信息: 第{i + 1}个 第{page_num}页 Start")
                actor_id = dict_actor.get('id')

                actor_vo = save_actor(actor_id, cid)
                actor_list.append(actor_vo)

                process_log.process2(f"获取演员信息: 第{i + 1}个 第{page_num}页 End")
        else:
            com_log.error(f"获取演员列表接口报错: 第{page_num}页"
                          f"\n\t接口响应结果: {dict_res}")

    return actor_list


def save_actor(actor_id, cid) -> ActorVo:
    """
    进一步获取并保存演员的信息
    :param cid:
    :param actor_id:
    :return:
    """

    actor_vo = None
    data = {
        'id': actor_id
    }

    res = req_util.try_ajax_post_times(f'{URL_HOST_API}{API_PATH_ACTOR_DETAIL}', data=data,
                                       msg=f"获取演员信息, 演员ID: {actor_id}")
    if res:
        dict_res = json.loads(res.text)
        print(dict_res)

        if dict_res.get('code') == 200:
            dict_actor = dict_res.get('data')
            name = dict_actor.get('name')
            photo = dict_actor.get('photo')
            sex = dict_actor.get('sex')
            social_accounts = dict_actor.get('social_accounts')
            social_accounts = ','.join(
                [social_account for social_account in social_accounts]) if social_accounts else ''
            movie_sum = dict_actor.get('movie_sum')
            like_sum = dict_actor.get('like_sum')
            actor_vo = ActorVo(id=actor_id, name=name, photo=photo, sex=sex, social_accounts=social_accounts,
                               movie_sum=movie_sum, like_sum=like_sum)
            alias_list = dict_actor.get('names')
            alias = ','.join(alias_list)
            actor_vo.alias = alias

            set_cid_for_vo(actor_vo, cid)

            com_log.info(f"获取到演员: {actor_vo}")

            # 演员入库并保存JSON ↓↓↓
            insert_result = actor_dao.insert(actor_vo, log=com_log)
            if insert_result == 1:
                rcd_data_json.add_data_to_json(json_file=JSON_DATA_ACTOR, data=actor_vo)
            elif isinstance(insert_result, Tuple):
                print(insert_result)
                actor_vo = ActorVo(*insert_result[0])
                set_cid_for_vo(actor_vo, cid)
                update_result = actor_dao.update_by_id(actor_vo)
                if update_result == 1:
                    rcd_data_json.update_data_to_json(json_file=JSON_DATA_ACTOR, data=actor_vo,
                                                      update_by_list=[('id', actor_vo.id)], msg=f"演员")
            # 演员入库并保存JSON ↑↑↑

            # 保存演员头像 ↓↓↓
            if actor_vo.photo:
                places: List[Tuple[str, str]] = [(f"{PIC_DIR_ACTOR_AVATAR}", f"{actor_vo.id}_{actor_vo.name}")]
                save_pic_util.save_pic_multi_places(url=f"{actor_vo.photo}", places=places,
                                                    msg=f"获取演员头像: 演员{actor_vo}")
            # 保存演员头像 ↑↑↑

            # 获取演员影片信息 ↓↓↓
            if cid in [2, 3, 4, 10]:
                get_actor_movie(actor_vo)
            # 获取演员影片信息 ↑↑↑
    return actor_vo


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
            process_log.process1(f"跳过 获取演员列表: 第{i}页")
            StartPoint.START_POINT_ACTOR_PAGE -= 1
            continue
        process_log.process1(f"获取演员列表: 第{i}页 Start")
        actor_list = get_actor_list_page(cid, i)
        process_log.process1(f"获取演员列表成功: 第{i}页 结果: {actor_list}")
        process_log.process1(f"获取演员列表: 第{i}页 End")
        if not actor_list:
            process_log.process1(f"获取演员列表第{i}页 结果为空, 不再获取下一页")
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


# 按间距中的绿色按钮以运行脚本。
def test_get_actor_list_page():
    get_actor_list_page(cid=10, page_num=1)


if __name__ == '__main__':
    start_time = time.time()
    start()
    # test_get_actor_list_page()
    end_time = time.time()
    duration = end_time - start_time
    duration_minutes = duration / 60
    print("程序持续时间：", duration_minutes, "分钟")
