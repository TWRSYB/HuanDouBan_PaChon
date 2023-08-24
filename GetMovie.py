import json
import re
import concurrent.futures
import threading
from os import makedirs
from typing import List, Tuple, Dict

from lxml import etree

from Config import StartPoint
from Config.Config import URL_HOST, API_PATH_ACTOR_MOVIE, URL_HOST_API, PAGE_PATH_MOVIE, JSON_DATA_ISSUER, \
    JSON_DATA_DIRECTOR, PIC_DIR_MOVIE_GALLERY_PIC_ID_FANHAO, PIC_DIR_MOVIE_COVER_PIC_ID_FANHAO, \
    PIC_DIR_MOVIE_TRAILER_ID_FANHAO, PIC_DIR_MOVIE_COVER_PIC_STUDIO_FANHAO, PIC_DIR_MOVIE_GALLERY_PIC_STUDIO_FANHAO, \
    PIC_DIR_MOVIE_TRAILER_STUDIO_FANHAO
from Dao.DirectorDao import DirectorVo, DirectorDao
from Dao.IssuerDao import IssuerVo, IssuerDao
from Dao.MagnetDao import MagnetVo, MagnetDao
from Dao.MovieDao import MovieVo, MovieDao
from LogUtil import LogUtil
from LogUtil.LogUtil import com_log, process_log, async_log, save_pic_log
from MyUtil.MyUtil import dict_to_obj2
from MyUtil.RcdDataJson import rcd_data_json
from MyUtil.StrToContainerUtil import StrToContainer, tran_dict_by_param_dict
from MyUtil.XpathUtil import xpath_util
from ReqUtil.ReqUtil import ReqUtil
from ReqUtil.SavePicUtil import SavePicUtil

req_util = ReqUtil()
save_pic_util = SavePicUtil()

set_issuer_id = set()
set_director_id = set()
set_series_id = set()

# 创建一个互斥锁
lock = threading.Lock()

# def get_from_param_dict(param_key, param_dict):
#     param_value = param_dict.get(param_key)
#     return param_value if param_value else param_key


def get_movie_detail(dict_movie, log=com_log, movie_order=0) -> MovieVo:
    # 创建需要的dao, 不使用共享资源, 保证多线程时的线程安全 ↓↓↓
    movie_dao = MovieDao()
    issuer_dao = IssuerDao()
    director_dao = DirectorDao()
    magnet_dao = MagnetDao()
    # 创建需要的dao, 不使用共享资源, 保证多线程时的线程安全 ↑↑↑

    movie_vo = MovieVo(**dict_movie)

    res = req_util.try_get_req_times(f"{URL_HOST}{PAGE_PATH_MOVIE}/{movie_vo.id}",
                                     msg=f"获取影片页面 movie_order: {movie_order}, movie_vo: {movie_vo}",
                                     log=log)
    if res:
        # 解析 Vue js ↓↓↓
        etree_res = etree.HTML(res.text)
        script_text = etree_res.xpath("/html/body/script[not(@src)]/text()")[0].replace(r'\u002F', '/')
        match = re.match(r'window.__NUXT__=\(function\((.+)\){return {layout:"default",data:\[{movieDetail:({.+}),'
                         r'query:{.+}\((.+)\)\);',
                         script_text)
        key_list = match.group(1).split(',')
        value_list = StrToContainer(the_str=f"[{match.group(3)}]").get_monomer()
        param_dict = {key: value_list[i] for i, key in enumerate(key_list)}

        movie_detail_str = match.group(2)
        movie_detail_dict = StrToContainer(the_str=movie_detail_str).get_monomer()
        tran_dict_by_param_dict(movie_detail_dict, param_dict)
        log.info(f"获取到影片页面的 Vue 数据 movie_detail_dict: {movie_detail_dict}")
        # 解析 Vue js ↑↑↑

        movie_time = movie_detail_dict.get('time')
        trailer = movie_detail_dict.get('trailer')

        # 解析 xpath 影片信息 ↓↓↓
        card_info = etree_res.xpath("//ul[@class='c-m-u']")[0]
        # 解析 xpath 影片信息 ↑↑↑

        # 获取影片时长和发行日期 ↓↓↓
        duration = xpath_util.get_unique(element=card_info,
                                         xpath="./li/span[@class='label' and text()='时长：']/../span[@class='cont']/text()"
                                         ).strip()

        issue_date = xpath_util.get_unique(element=card_info,
                                           xpath="./li/span[@class='label' and text()='日期：']/../span["
                                                 "@class='cont']/text()"
                                           ).strip()
        # 获取影片时长和发行日期 ↑↑↑

        # 获取片商, 发行, 系列, 导演信息 ↓↓↓
        studio_nm = xpath_util.get_unique(element=card_info, xpath="./li/div/span/a[contains(@href,'studios')]/text()")
        studio_id = xpath_util.get_unique(element=card_info, xpath="./li/div/span/a[contains(@href,'studios')]/@href"
                                          ).split('/')[-1]

        director_nm = xpath_util.get_unique(element=card_info,
                                            xpath="./li/div/span/a[contains(@href,'director')]/text()")
        director_id = xpath_util.get_unique(element=card_info, xpath="./li/div/span/a[contains(@href,'director')]/@href"
                                            ).split('/')[-1]
        issuer_nm = xpath_util.get_unique(element=card_info,
                                          xpath="./li/div/span[@class='label' and text()='发行：']/../span[@class='cont']/text()"
                                          ).strip()

        series_nm = xpath_util.get_unique(element=card_info, xpath="./li/div/span/a[contains(@href,'series')]/text()")
        series_id = xpath_util.get_unique(element=card_info, xpath="./li/div/span/a[contains(@href,'series')]/@href"
                                          ).split('/')[-1]
        # 获取片商, 发行, 系列, 导演信息 ↑↑↑

        # 获取评价人数 ↓↓↓
        evaluators_num = xpath_util.get_unique(element=card_info, xpath="./li/span/em[2]/text()"
                                               ).replace('由', '').replace('人评价', '')
        # 获取评价人数 ↑↑↑

        # 获取标签列表 ↓↓↓
        label_list = card_info.xpath("./li/div/span//a[contains(@href,'label')]/text()")
        label_href_list = card_info.xpath("./li/div/span//a[contains(@href,'label')]/@href")
        labels = ','.join(label_list)
        label_ids = ','.join([label_href.split('/')[-1] for label_href in label_href_list])
        # 获取标签列表 ↑↑↑

        # 获取演员列表 ↓↓↓
        actor_list = card_info.xpath("./li/div/span//a[contains(@href,'actor')]/text()")
        actor_href_list = card_info.xpath("./li/div/span//a[contains(@href,'actor')]/@href")
        actors = ','.join(actor_list)
        actor_ids = ','.join([actor_href.split('/')[-1] for actor_href in actor_href_list])
        # 获取演员列表 ↑↑↑

        # 为影片对象赋值并保存 ↓↓↓
        movie_vo.time = movie_time
        movie_vo.trailer = trailer
        movie_vo.duration = duration
        movie_vo.issue_date = issue_date
        movie_vo.studio_nm = studio_nm
        movie_vo.studio_id = studio_id
        movie_vo.director_nm = director_nm
        movie_vo.director_id = director_id
        movie_vo.issuer_nm = issuer_nm
        movie_vo.series_nm = series_nm
        movie_vo.series_id = series_id
        movie_vo.evaluators_num = evaluators_num
        movie_vo.labels = labels
        movie_vo.label_ids = label_ids
        movie_vo.actors = actors
        movie_vo.actor_ids = actor_ids

        log.info(f"获取到影片信息: {movie_vo}")

        # 为影片对象赋值并保存 ↑↑↑

        # 发行商入库 ↓↓↓
        if issuer_nm:
            if (studio_id, issuer_nm) not in set_issuer_id:
                issuer_vo = IssuerVo(id_studio=studio_id, name=issuer_nm)
                insert_result = issuer_dao.insert(issuer_vo, log=log)
                if insert_result == 1:
                    rcd_data_json.append_data_to_txt(txt_file=JSON_DATA_ISSUER, data=issuer_vo, msg="发行商", log=log)
                    set_issuer_id.add((studio_id, issuer_nm))
        # 发行商入库 ↑↑↑

        # 导演入库 ↓↓↓
        if director_id:
            if director_id not in set_director_id:
                director_vo = DirectorVo(director_id, director_nm)
                insert_result = director_dao.insert(director_vo, log=log)
                if insert_result == 1:
                    rcd_data_json.append_data_to_txt(txt_file=JSON_DATA_DIRECTOR, data=director_vo, msg="导演", log=log)
                    set_issuer_id.add((studio_id, issuer_nm))
        # 导演入库 ↑↑↑

        # 封面图保存 ↓↓↓
        places: List[Tuple[str, str]] = [(PIC_DIR_MOVIE_COVER_PIC_ID_FANHAO, f"{movie_vo.id}_{movie_vo.number}"),
                                         (PIC_DIR_MOVIE_COVER_PIC_STUDIO_FANHAO,
                                          f"{movie_vo.studio_nm}_{movie_vo.number}")]
        if movie_vo.big_cove:
            save_pic_util.save_pic_multi_places(url=movie_vo.big_cove, places=places, msg=f"影片封面图大, 影片: {movie_vo}",
                                                log=save_pic_log, is_async=True)
        elif movie_vo.small_cover:
            save_pic_util.save_pic_multi_places(url=movie_vo.small_cover, places=places, msg=f"影片封面图小, 影片: {movie_vo}",
                                                log=save_pic_log, is_async=True)
        # 封面图保存 ↑↑↑

        # # 预告片保存 ↓↓↓
        # if trailer:
        #     places: List[Tuple[str, str]] = []
        #     places.append((PIC_DIR_MOVIE_TRAILER_ID_FANHAO, f"{movie_vo.id}_{movie_vo.number}"))
        #     places.append((PIC_DIR_MOVIE_TRAILER_STUDIO_FANHAO, f"{movie_vo.studio_nm}_{movie_vo.number}"))
        #     if movie_vo.big_cove:
        #         save_pic_util.save_pic_multi_places(url=trailer, places=places,
        #                                             msg=f"影片预告片, 影片: {movie_vo}", log=log)
        # # 预告片保存 ↑↑↑

        # 预览图保存 ↓↓↓
        big_gallery_list = re.findall(r',big_img:"(.+?)"}', script_text)
        if big_gallery_list:
            dir_id_fanhao = f"{PIC_DIR_MOVIE_GALLERY_PIC_ID_FANHAO}/{movie_vo.id}_{movie_vo.number}"
            dir_studio_fanhao = f"{PIC_DIR_MOVIE_GALLERY_PIC_STUDIO_FANHAO}/{movie_vo.studio_nm}_{movie_vo.number}"
            makedirs(dir_id_fanhao, exist_ok=True)
            makedirs(dir_studio_fanhao, exist_ok=True)
            for i, big_gallery in enumerate(big_gallery_list):
                places: List[Tuple[str, str]] = [
                    (dir_id_fanhao, f"{movie_vo.id}_{movie_vo.number}_{str(i + 1).zfill(3)}"),
                    (dir_studio_fanhao, f"{movie_vo.studio_nm}_{movie_vo.number}_{str(i + 1).zfill(3)}")]
                save_pic_util.save_pic_multi_places(url=big_gallery, places=places,
                                                    msg=f"影片预览图, 影片: {movie_vo}", log=save_pic_log, is_async=True)
        # 预览图保存 ↑↑↑

        # 保存磁力链接 ↓↓↓

        flux_linkage: List[Dict] = movie_detail_dict.get('flux_linkage')
        if flux_linkage:
            for flux_link in flux_linkage:
                magnet_name = flux_link.get('name')
                magnet_url = flux_link.get('url')
                magnet_meta = flux_link.get('meta')
                magnet_time = flux_link.get('time')
                magnet_hashcode = magnet_url.split('&')[0].split(':')[-1]
                magnet_file_list = magnet_meta.split(', ')
                magnet_size = ''
                magnet_file_num = ''
                for file_info in magnet_file_list:
                    if file_info.endswith("B"):
                        magnet_size = file_info
                    elif file_info.endswith("個文件"):
                        magnet_file_num = file_info
                magnet_vo = MagnetVo(id_fanhao=movie_vo.number, id_hashcode=magnet_hashcode,
                                     name=magnet_name,
                                     url=magnet_url, time=magnet_time, size=magnet_size,
                                     file_num=magnet_file_num)
                insert_result = magnet_dao.insert(magnet_vo, log=log)
                if insert_result == 1:
                    # 在访问共享资源之前获取锁
                    lock.acquire()
                    # 访问共享资源
                    try:
                        rcd_data_json.json_file_magnet.write(f"{magnet_vo}\n")
                        log.info(f"json写入文件成功 magnet JSON: {magnet_vo}")
                    except Exception as e:
                        log.error(f"json写入文件出现异常 magnet JSON: {magnet_vo}"
                                  f"\n\t异常: {e}")
                    # 完成操作后释放锁
                    lock.release()
        # 保存磁力链接 ↑↑↑
    insert_result = movie_dao.insert(movie_vo, log=log)
    if insert_result == 1:
        # 在访问共享资源之前获取锁
        lock.acquire()
        # 访问共享资源
        try:
            rcd_data_json.json_file_movie.write(f"{movie_vo}\n")
            log.info(f"json写入文件成功 movie JSON: {movie_vo}")
        except Exception as e:
            log.error(f"json写入文件出现异常 movie JSON: {movie_vo}"
                      f"\n\t异常: {e}")
        # 完成操作后释放锁
        lock.release()

    return movie_vo


def get_movie_detail_async(args):
    dict_movie, actor_id, page_num, i = args
    process_log.process4(f"获取影片信息: 第{i + 1}个 第{page_num}页 演员: {actor_id} Start")
    movie_vo = get_movie_detail(dict_movie, log=async_log, movie_order=i + 1)
    process_log.process4(f"获取影片信息: 第{i + 1}个 第{page_num}页 演员: {actor_id} End")
    return movie_vo


def get_actor_movie_page(actor_id, page_num):
    movie_list: List = []

    data = {
        'filter': 9,  # 过滤: 0-全部, 1-有字幕, 2-可下载, 3-含短评  试了下,没有更多码值
        'id': actor_id,
        'page': page_num,
        'pageSize': 50,
        'sort': "1",  # 排序: 1-发布日期, 2-磁链更新  试了下,没有更多码值
        # 'cid': '2',

    }
    res = req_util.try_ajax_post_times(url=f"{URL_HOST_API}{API_PATH_ACTOR_MOVIE}", data=data,
                                       msg=f"获取演员影片列表: 第{page_num}页 演员: {actor_id}")

    if res:
        dict_res = json.loads(res.text)

        if dict_res.get('code') == 200:
            if str(dict_res.get('data').get('pageSize')) != '50':
                com_log.error(f"获取演员影片列表, 响应的pageSize不是50: {dict_res}, 第{page_num}页 演员:"
                              f" {actor_id}")
            # for i, dict_movie in enumerate(dict_res.get('data').get('list')):
            #     LogUtil.LOG_PROCESS_MOVIE_ORDER = i + 1
            #     if StartPoint.START_POINT_MOVIE_ORDER > 1:
            #         process_log.process4(f"跳过 获取影片信息: 第{i + 1}个 第{page_num}页 演员: {actor_id}")
            #         StartPoint.START_POINT_MOVIE_ORDER -= 1
            #         continue
            #     process_log.process4(f"获取影片信息: 第{i + 1}个 第{page_num}页 演员: {actor_id} Start")
            #     movie_vo = get_movie_detail(dict_movie)
            #     movie_list.append(movie_vo)
            #     process_log.process4(f"获取影片信息: 第{i + 1}个 第{page_num}页 演员: {actor_vo} End")

            # 创建线程池, 异步多线程获取影片信息(整页开始)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # 开启多个线程获取影片详情
                futures = [executor.submit(get_movie_detail_async, args=(dict_movie, actor_id, page_num, i))
                           for i, dict_movie in enumerate(dict_res.get('data').get('list'))]
            # 等待所有线程完成并获取结果
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    movie_list.append(future.result())
    return movie_list


def get_actor_movie(actor_id):
    for i in range(1, 100):
        LogUtil.LOG_PROCESS_MOVIE_PAGE = i
        LogUtil.LOG_PROCESS_MOVIE_ORDER = 0
        if StartPoint.START_POINT_MOVIE_PAGE > 1:
            process_log.process3(f"跳过 获取演员影片列表: 第{i}页 演员: {actor_id}")
            StartPoint.START_POINT_MOVIE_PAGE -= 1
            continue
        process_log.process3(f"获取演员影片列表: 第{i}页 演员: {actor_id} Start")
        movie_list = get_actor_movie_page(actor_id, i)
        com_log.info(f"获取演员影片列表完成: 第{i}页 演员: {actor_id} 结果: {movie_list}")
        process_log.process3(f"获取演员影片列表: 第{i}页 演员: {actor_id} End")
        if not movie_list:
            process_log.process3(f"获取演员影片列表第{i}页没有数据, 不再获取下一页了")
            break


def test_get_actor_movie():
    get_actor_movie(1065)


def test_get_movie_detail():
    dict_movie = {"id": 480766, "name": " 初老の小説家に飼われた編集者の妻 川上ゆう パンティと生写真付き", "number": "NACR-545",
                  "release_time": "2022-05-20 00:00:00", "created_at": "2022-07-31T08:21:25.000000Z", "is_download": 2,
                  "is_subtitle": 1, "is_short_comment": 1, "is_hot": 1, "is_new_comment": 2, "is_flux_linkage": 2,
                  "comment_num": 0, "score": 9,
                  "small_cover": "https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/small_cover.jpg",
                  "big_cove": "https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/big_cover.jpg",
                  "duration": "2分钟", "issue_date": "2022-05-20", "studio_nm": "プラネットプラス",
                  "studio_id": "28", "director_nm": "桜人", "director_id": "122", "issuer_nm": " ", "series_nm": "",
                  "series_id": "", "evaluators_num": "106", "labels": "已婚婦女,中出,自慰,口交,熟女,單體作品",
                  "label_ids": "89,192,197,200,377,6784", "actors": "川上ゆう♀,栗原良♂,矢野慎二♂",
                  "actor_ids": "1065,3524,3290"}

    # movie_vo: MovieVo = dict_to_obj2(MovieVo, dict_movie)

    get_movie_detail(dict_movie)


if __name__ == '__main__':
    test_get_actor_movie()
    # test_get_movie_detail()
