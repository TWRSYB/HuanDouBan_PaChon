import re
import concurrent.futures
import threading
import time
from os import makedirs
from typing import List, Tuple, Dict

from lxml import etree

from Config import StartPoint
from Config.Config import JSON_DATA_ISSUER, \
    JSON_DATA_DIRECTOR, PIC_DIR_MOVIE_COVER_PIC_STUDIO_FANHAO, PIC_DIR_MOVIE_GALLERY_PIC_STUDIO_FANHAO, \
    PIC_DIR_MOVIE_TRAILER_STUDIO_FANHAO, JSON_DATA_MOVIE_DETAIL
from Config.ReqConfig import URL_HOST, PAGE_PATH_MOVIE, URL_HOST_API, API_PATH_ACTOR_MOVIE
from Dao.DirectorDao import DirectorVo, DirectorDao
from Dao.IssuerDao import IssuerVo, IssuerDao
from Dao.MagnetDao import MagnetVo, MagnetDao
from Dao.MovieDao import MovieVo, MovieDao
from LogUtil import LogUtil
from LogUtil.LogUtil import com_log, process_log, async_log, pic_log
from MyUtil.MyUtil import filename_rm_invalid_chars
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


def get_movie_detail(movie_id, log=com_log, movie_order=0) -> MovieVo:
    # 创建需要的dao, 不使用共享资源, 保证多线程时的线程安全 ↓↓↓
    movie_dao = MovieDao()
    issuer_dao = IssuerDao()
    director_dao = DirectorDao()
    magnet_dao = MagnetDao()
    # 创建需要的dao, 不使用共享资源, 保证多线程时的线程安全 ↑↑↑

    # movie_vo = MovieVo(**dict_movie)

    res = req_util.try_get_times(f"{URL_HOST}{PAGE_PATH_MOVIE}/{movie_id}",
                                 msg=f"获取影片页面 movie_order: {movie_order}, movie_id: {movie_id}",
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

        print(movie_detail_dict)
        with lock:
            rcd_data_json.update_dict_json(json_file=JSON_DATA_MOVIE_DETAIL, new_entry={movie_id: movie_detail_dict},
                                           log=log)

        # 从mdd中获取影片信息 ↓↓↓
        # id = movie_detail_dict.get('id'),
        number = movie_detail_dict.get('number')
        name = movie_detail_dict.get('name')
        movie_time = movie_detail_dict.get('time')
        release_time = movie_detail_dict.get('release_time')
        small_cover = movie_detail_dict.get('small_cover')
        big_cove = movie_detail_dict.get('big_cove')
        trailer = movie_detail_dict.get('trailer')

        gallery_map_list: List[Dict] = movie_detail_dict.get('map')

        score = movie_detail_dict.get('score')
        score_people = movie_detail_dict.get('score_people')

        comment_num = movie_detail_dict.get('comment_num')
        flux_linkage_num = movie_detail_dict.get('flux_linkage_num')

        flux_linkage_list: List[Dict] = movie_detail_dict.get('flux_linkage')

        flux_linkage_time = movie_detail_dict.get('flux_linkage_time')
        created_at = movie_detail_dict.get('created_at')

        labels: List[Dict] = movie_detail_dict.get('labels')
        label_names = ''
        label_ids = ''
        if labels:
            label_names = ','.join([label.get('name') for label in labels])
            label_ids = ','.join([label.get('id') for label in labels])

        actors: List[Dict] = movie_detail_dict.get('actors')
        actor_names = ''
        actor_ids = ''
        if actors:
            actor_names = ','.join([actor.get('name') for actor in actors])
            actor_ids = ','.join([actor.get('id') for actor in actors])

        director: List[Dict] = movie_detail_dict.get('director')
        director_name = ''
        director_id = ''
        if director:
            director_name = director[0].get('name')
            director_id = director[0].get('id')

        studio_list: List[Dict] = movie_detail_dict.get('company')
        studio_name = ''
        studio_id = ''
        if studio_list:
            studio_name = studio_list[0].get('name')
            studio_id = studio_list[0].get('id')

        series: List[Dict] = movie_detail_dict.get('series')
        series_name = ''
        series_id = ''
        if series:
            series_name = series[0].get('name')
            series_id = series[0].get('id')

        # 从mdd中获取影片信息 ↑↑↑

        # xpath获取发行商信息 ↓↓↓
        card_info = etree_res.xpath("//ul[@class='c-m-u']")[0]
        issuer_name = xpath_util.get_unique(element=card_info,
                                            xpath="./li/div/span[@class='label' and text()='发行：']/../span[@class='cont']/text()"
                                            ).strip()
        # xpath获取发行商信息 ↑↑↑

        # 创建movie对象 ↓↓↓
        movie_vo = MovieVo(movie_id, number, name, movie_time, release_time, small_cover, big_cove, trailer,
                           score, score_people, comment_num, flux_linkage_num, flux_linkage_time, created_at,
                           label_names, label_ids, actor_names, actor_ids, director_name, director_id,
                           studio_name, studio_id, series_name, series_id, issuer_name)
        log.info(f"获取到影片信息: {movie_vo}")
        # 创建movie对象 ↑↑↑

        # 发行商入库 ↓↓↓
        if issuer_name:
            if (studio_id, issuer_name) not in set_issuer_id:
                issuer_vo = IssuerVo(id_studio=studio_id, name=issuer_name)
                insert_result = issuer_dao.insert(issuer_vo, log=log)
                if insert_result == 1:
                    rcd_data_json.append_data_to_txt(txt_file=JSON_DATA_ISSUER, data=issuer_vo, msg="发行商", log=log)
                    set_issuer_id.add((studio_id, issuer_name))
        # 发行商入库 ↑↑↑

        # 导演入库 ↓↓↓
        if director_id:
            if director_id not in set_director_id:
                director_vo = DirectorVo(director_id, director_name)
                insert_result = director_dao.insert(director_vo, log=log)
                if insert_result == 1:
                    rcd_data_json.append_data_to_txt(txt_file=JSON_DATA_DIRECTOR, data=director_vo, msg="导演", log=log)
                    set_director_id.add((studio_id, director_id))
        # 导演入库 ↑↑↑

        # 封面图保存 ↓↓↓
        get_and_save_cover(movie_vo)
        # 封面图保存 ↑↑↑

        # 预告片保存 ↓↓↓
        get_and_save_trailer(movie_vo)
        # 预告片保存 ↑↑↑

        # 预览图保存 ↓↓↓
        gallery_url_list = []
        if gallery_map_list:
            for gallery_map in gallery_map_list:
                if gallery_map.get('big_img'):
                    gallery_url_list.append(gallery_map.get('big_img'))
                elif gallery_map.get('img'):
                    gallery_url_list.append(gallery_map.get('img'))
            if gallery_url_list:
                dir_gallery_studio_fanhao = f"{PIC_DIR_MOVIE_GALLERY_PIC_STUDIO_FANHAO}/{filename_rm_invalid_chars(movie_vo.studio_name if movie_vo.studio_name else '_NoStudio')}/{filename_rm_invalid_chars(movie_vo.number)}"
                makedirs(dir_gallery_studio_fanhao, exist_ok=True)
                for i, gallery_url in enumerate(gallery_url_list):
                    places: List[Tuple[str, str]] = [
                        (dir_gallery_studio_fanhao, f"{movie_vo.number}_{str(i + 1).zfill(3)}")]
                    save_pic_util.save_pic_multi_places(url=gallery_url, places=places,
                                                        msg=f"影片预览图, movie_vo: {movie_vo}, places: {places}",
                                                        log=pic_log, is_async=True)
        # 预览图保存 ↑↑↑

        # 保存磁力链接 ↓↓↓
        if flux_linkage_list:
            for flux_link in flux_linkage_list:
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


def get_and_save_cover(movie_vo, log=pic_log):
    if movie_vo.big_cove or movie_vo.small_cover:
        dir_cover_studio = f"{PIC_DIR_MOVIE_COVER_PIC_STUDIO_FANHAO}/{filename_rm_invalid_chars(movie_vo.studio_name if movie_vo.studio_name else '_NoStudio')}"
        makedirs(dir_cover_studio, exist_ok=True)
        places: List[Tuple[str, str]] = [(dir_cover_studio, f"{movie_vo.studio_name}_{movie_vo.number}")]
        if movie_vo.big_cove:
            save_pic_util.save_pic_multi_places(url=movie_vo.big_cove, places=places,
                                                msg=f"影片封面图大, movie_vo: {movie_vo}",
                                                log=pic_log, is_async=True)
        elif movie_vo.small_cover:
            save_pic_util.save_pic_multi_places(url=movie_vo.small_cover, places=places,
                                                msg=f"影片封面图小, movie_vo: {movie_vo}",
                                                log=pic_log, is_async=True)


def get_and_save_trailer(movie_vo, log=pic_log):
    if movie_vo.trailer:
        dir_trailer_studio = f"{PIC_DIR_MOVIE_TRAILER_STUDIO_FANHAO}/{filename_rm_invalid_chars(movie_vo.studio_name if movie_vo.studio_name else '_NoStudio')}"
        makedirs(dir_trailer_studio, exist_ok=True)
        places: List[Tuple[str, str]] = [(dir_trailer_studio, f"{movie_vo.studio_name}_{movie_vo.number}")]
        save_pic_util.save_pic_multi_places(url=movie_vo.trailer, places=places, timeout=200,
                                            msg=f"影片预告片, movie_vo: {movie_vo}", log=log, is_async=True)


def get_movie_detail_async(args):
    movie_id, actor_id, page_num, i = args
    process_log.process4(f"获取影片信息: 第{i + 1}个 第{page_num}页 演员: {actor_id} Start")
    movie_vo = get_movie_detail(movie_id=movie_id, log=async_log, movie_order=i + 1)
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
    dict_res = req_util.try_ajax_post_times(url=f"{URL_HOST_API}{API_PATH_ACTOR_MOVIE}", data=data,
                                            msg=f"获取演员影片列表: 第{page_num}页 演员: {actor_id}")

    if dict_res:
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
        #     movie_vo = get_movie_detail(dict_movie.get('id'))
        #     movie_list.append(movie_vo)
        #     process_log.process4(f"获取影片信息: 第{i + 1}个 第{page_num}页 演员: {actor_vo} End")

        # 创建线程池, 异步多线程获取影片信息(整页开始)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 开启多个线程获取影片详情
            futures = [executor.submit(get_movie_detail_async, args=(dict_movie.get('id'), actor_id, page_num, i))
                       for i, dict_movie in enumerate(dict_res.get('data').get('list'))]
        # 等待所有线程完成并获取结果
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                movie_list.append(future.result())
    else:
        com_log.error(f"获取演员影片列表失败: 第{page_num}页 演员: {actor_id}")
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
    # get_movie_detail(480766)
    影片页面_响应错误_movie_dict, 影片页面_响应错误_movie_list = read_movie_from_file(
        r'D:\34.Temp\06.黄豆瓣数据爬取\01.TEMP_wait\logs_阶段6_cid3/响应错误!!! 获取影片页面.txt', r'2023-08-.+movie_vo: ({.+}) res: .+')
    影片页面_出现异常_movie_dict, 影片页面_出现异常_movie_list = read_movie_from_file(
        r'D:\34.Temp\06.黄豆瓣数据爬取\01.TEMP_wait\logs_阶段6_cid3/出现异常!!! 获取影片页面.txt', r'2023-08-.+movie_vo: ({.+}) res: .+')
    封面图大_出现异常_movie_dict, 封面图大_出现异常_movie_list = read_movie_from_file(
        r'D:\34.Temp\06.黄豆瓣数据爬取\01.TEMP_wait\logs_阶段6_cid3/出现异常!!! 影片封面图大.txt', r'2023-08-.+影片: ({.+}) res: .+')
    预览图_出现异常_movie_dict, 预览图_出现异常_movie_list = read_movie_from_file(
        r'D:\34.Temp\06.黄豆瓣数据爬取\01.TEMP_wait\logs_阶段6_cid3/出现异常!!! 影片预览图.txt', r'2023-08-.+影片: ({.+}) res: .+')
    print(len(影片页面_响应错误_movie_dict), len(影片页面_响应错误_movie_list))
    print(len(影片页面_出现异常_movie_dict), len(影片页面_出现异常_movie_list))
    print(len(封面图大_出现异常_movie_dict), len(封面图大_出现异常_movie_list))
    print(len(预览图_出现异常_movie_dict), len(预览图_出现异常_movie_list))

    marge_movie_dict = {}
    for d in [影片页面_响应错误_movie_dict, 影片页面_出现异常_movie_dict, 封面图大_出现异常_movie_dict, 预览图_出现异常_movie_dict]:
        marge_movie_dict.update(d)
    marge_movie_list = 影片页面_响应错误_movie_list + 影片页面_出现异常_movie_list + 封面图大_出现异常_movie_list + 预览图_出现异常_movie_list

    print(len(marge_movie_dict), len(marge_movie_list))

    for key, value in marge_movie_dict.items():
        # threading.Thread(target=get_movie_detail, args=(dict_movie,))
        get_movie_detail(key)


def read_movie_from_file(file_path, reg):
    dict_movie_list = []
    dict_movie_dict = {}
    with open(file=file_path, mode='r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            match = re.match(reg, line)
            if match:
                dict_movie = eval(match.group(1))
                dict_movie_list.append(dict_movie)
                dict_movie_dict[dict_movie.get('id')] = dict_movie
    return dict_movie_dict, dict_movie_list


def batch_get_trailer_from_error_log():
    movie_vo_list = []
    movie_vo_dict = {}
    with open(file=r'D:\34.Temp\06.黄豆瓣数据爬取\01.TEMP_wait\logs_阶段4_cid2/Async_error.log', mode='r',
              encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            match = re.match(r'2023-0.+出现异常!!! 第5次 msg: 影片预告片, movie_vo: ({.+})', line)
            if not match:
                match = re.match(r'2023-0.+响应错误!!! 第5次 msg: 影片预告片, movie_vo: ({.+})', line)
            if match:
                dict_movie = eval(match.group(1))
                movie_vo = MovieVo(**dict_movie)

                movie_vo_list.append(movie_vo)
                movie_vo_dict[movie_vo.id] = movie_vo

    com_log.info(f"从日志中发现的 预告片 获取失败的影片列表: {movie_vo_list}")
    com_log.info(f"从日志中发现的 预告片 获取失败的影片列表长度: {len(movie_vo_list)}")
    com_log.info(f"从日志中发现的 预告片 获取失败的影片列表去重后: {movie_vo_dict}")
    com_log.info(f"从日志中发现的 预告片 获取失败的影片列表长度去重后: {len(movie_vo_dict)}")

    # i = 0
    # for key, value in movie_vo_dict.items():
    #     print(key)
    #     i = i + 1
    #     LogUtil.LOG_PROCESS_MOVIE_ORDER = i
    #     if i > 0 and i % 100 == 0:
    #         time.sleep(100)  # 模拟耗时操作
    #     threading.Thread(target=get_and_save_trailer, args=(value,)).start()
    #     time.sleep(1)


def batch_get_cover_from_error_log():
    movie_vo_list = []
    movie_vo_dict = {}
    with open(file=r'D:\34.Temp\06.黄豆瓣数据爬取\01.TEMP_wait\logs_阶段4_cid2/Pic_error.log', mode='r',
              encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            match = re.match(r'2023-0.+出现异常!!! 第5次 msg: 影片封面图[大小], 影片: ({.+})', line)
            if not match:
                match = re.match(r'2023-0.+响应错误!!! 第5次 msg: 影片封面图[大小], 影片: ({.+})', line)
            if match:
                dict_movie = eval(match.group(1))
                movie_vo = MovieVo(**dict_movie)
                print(movie_vo)

                movie_vo_list.append(movie_vo)
                movie_vo_dict[movie_vo.id] = movie_vo

    com_log.info(f"从日志中发现的 影片封面图 获取失败的影片列表: {movie_vo_list}")
    com_log.info(f"从日志中发现的 影片封面图 获取失败的影片列表长度: {len(movie_vo_list)}")
    com_log.info(f"从日志中发现的 影片封面图 获取失败的影片列表去重后: {movie_vo_dict}")
    com_log.info(f"从日志中发现的 影片封面图 获取失败的影片列表长度去重后: {len(movie_vo_dict)}")
    # i = 0
    # for key, value in movie_vo_dict.items():
    #     print(key)
    #     i = i + 1
    #     LogUtil.LOG_PROCESS_MOVIE_ORDER = i
    #     if i > 0 and i % 100 == 0:
    #         time.sleep(100)  # 模拟耗时操作
    #     threading.Thread(target=get_and_save_cover, args=(value,)).start()
    #     time.sleep(1)


def batch_get_movie_from_error_log():
    movie_id_list = []
    movie_id_set = set()
    with open(file=r'D:\34.Temp\06.黄豆瓣数据爬取\01.TEMP_wait\logs_阶段4_cid2/Async_error.log', mode='r',
              encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            match = re.match(r'2023-0.+响应错误!!! 第5次 msg: 获取影片页面.+movie_id: (.+) res:', line)
            if not match:
                match = re.match(r'2023-0.+出现异常!!! 第5次 msg: 获取影片页面, movie_vo: ({.+})', line)
            if match:
                movie_id = match.group(1)

                movie_id_list.append(movie_id)
                movie_id_set.add(movie_id)
    com_log.info(f"从日志中发现的 影片页面 获取失败的影片列表: {movie_id_list}")
    com_log.info(f"从日志中发现的 影片页面 获取失败的影片列表长度: {len(movie_id_list)}")
    com_log.info(f"从日志中发现的 影片页面 获取失败的影片列表去重后: {movie_id_set}")
    com_log.info(f"从日志中发现的 影片页面 获取失败的影片列表长度去重后: {len(movie_id_set)}")
    i = 0
    for movie_id in movie_id_set:
        print(movie_id)
        i = i + 1
        LogUtil.LOG_PROCESS_MOVIE_ORDER = i
        if i > 0 and i % 100 == 0:
            time.sleep(100)  # 模拟耗时操作
        threading.Thread(target=get_movie_detail, args=(movie_id, async_log, i)).start()
        time.sleep(1)


if __name__ == '__main__':
    start_time = time.time()
    # test_get_actor_movie()
    # test_get_movie_detail()
    # batch_get_trailer_from_error_log()
    batch_get_movie_from_error_log()
    # batch_get_cover_from_error_log()
    end_time = time.time()
    duration = end_time - start_time
    duration_minutes = duration / 60
    print("程序持续时间：", duration_minutes, "分钟")
