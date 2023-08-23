import json
import re
import urllib
from os import makedirs
from typing import List, Tuple

from lxml import etree

from Config import StartPoint
from Config.Config import URL_HOST, API_PATH_ACTOR_MOVIE, URL_HOST_API, PAGE_PATH_MOVIE, JSON_DATA_ISSUER, \
    JSON_DATA_DIRECTOR, PIC_DIR_MOVIE_GALLERY_PIC_ID_FANHAO, PIC_DIR_MOVIE_GALLERY_PIC_FANHAO, \
    PIC_DIR_MOVIE_COVER_PIC_ID_FANHAO, PIC_DIR_MOVIE_COVER_PIC_FANHAO, \
    PIC_DIR_MOVIE_TRAILER_FANHAO, PIC_DIR_MOVIE_TRAILER_ID_FANHAO
from Dao.ActorDao import ActorVo
from Dao.DirectorDao import DirectorVo, DirectorDao
from Dao.IssuerDao import IssuerVo, IssuerDao
from Dao.MagnetDao import MagnetVo, MagnetDao
from Dao.MovieDao import MovieVo, MovieDao
from LogUtil import LogUtil
from LogUtil.LogUtil import com_log, process_log
from MyUtil.MyUtil import dict_to_obj2
from MyUtil.RcdDataJson import rcd_data_json
from MyUtil.XpathUtil import xpath_util
from ReqUtil.ReqUtil import ReqUtil
from ReqUtil.SavePicUtil import SavePicUtil
from Test01.test04 import StrToContainer

req_util = ReqUtil()
save_pic_util = SavePicUtil()

set_issuer_id = set()
set_director_id = set()
set_series_id = set()


# def get_movie_info_card_lang(lang_host, id_fanhao, log=com_log, movie_order=0):
#     """
#     获取影片在不同影片下的页面
#     :param movie_order:
#     :param log:
#     :param lang_host: 语言的基础路径
#     :param id_fanhao: 影片番号
#     :return:
#     """
#     res = req_util.try_get_req_times(f"{lang_host}/{id_fanhao}",
#                                      msg=f"获取不同语言的影片页面 lang_host: {lang_host}, id_fanhao: {id_fanhao}, movie_order: {movie_order}",
#                                      log=log)
#     return res


def get_movie_detail(movie_vo, log=com_log, movie_order=0):
    # 创建需要的dao, 不使用共享资源, 保证多线程时的线程安全 ↓↓↓
    movie_dao = MovieDao()
    issuer_dao = IssuerDao()
    director_dao = DirectorDao()
    magnet_dao = MagnetDao()
    # 创建需要的dao, 不使用共享资源, 保证多线程时的线程安全 ↑↑↑

    res = req_util.try_get_req_times(f"{URL_HOST}{PAGE_PATH_MOVIE}/{movie_vo.id}",
                                     msg=f"获取影片页面 movie_order: {movie_order}, movie_vo: {movie_vo}",
                                     log=log)
    if res:
        etree_res = etree.HTML(res.text)
        card_info = etree_res.xpath("//ul[@class='c-m-u']")[0]
        # 获取影片时长和发行日期 ↓↓↓
        span_cont_list = card_info.xpath("./li/span[@class='cont']/text()")
        duration = ""
        issue_date = ""
        for span_cont in span_cont_list:
            if span_cont.endswith('分钟'):
                duration = span_cont
                break
        for span_cont in span_cont_list:
            match = re.match(r"^.*(\d{4}-\d{2}-\d{2})$", span_cont)
            if match:
                issue_date = span_cont
                break

        # 获取影片时长和发行日期 ↑↑↑

        # 获取片商, 发行, 系列, 导演信息 ↓↓↓
        studio_nm = xpath_util.get_unique(element=card_info, xpath="./li/div/span/a[contains(@href,'studios')]/text()")
        studio_id = \
            xpath_util.get_unique(element=card_info, xpath="./li/div/span/a[contains(@href,'studios')]/@href").split(
                '/')[
                -1]

        director_nm = xpath_util.get_unique(element=card_info,
                                            xpath="./li/div/span/a[contains(@href,'director')]/text()")
        director_id = \
            xpath_util.get_unique(element=card_info, xpath="./li/div/span/a[contains(@href,'director')]/@href").split(
                '/')[
                -1]

        issuer_nm = xpath_util.get_unique(element=card_info, xpath="./li/div/span[@class='cont']/text()")

        series_nm = xpath_util.get_unique(element=card_info, xpath="./li/div/span/a[contains(@href,'series')]/text()")
        series_id = \
            xpath_util.get_unique(element=card_info, xpath="./li/div/span/a[contains(@href,'series')]/@href").split(
                '/')[-1]
        # 获取片商, 发行, 系列, 导演信息 ↑↑↑

        # 获取评价人数 ↓↓↓
        evaluators_num = xpath_util.get_unique(element=card_info, xpath="./li/span/em[2]/text()") \
            .replace('由', '') \
            .replace('人评价', '')
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
        movie_vo.mosaic = '0'
        movie_vo.condom = '0'
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
        insert_result = movie_dao.insert(movie_vo)
        if insert_result == 1:
            try:
                rcd_data_json.json_file_movie.write(f"{movie_vo}\n")
                log.info(f"json写入文件成功 movie JSON: {movie_vo}")
            except Exception as e:
                log.error(f"json写入文件出现异常 movie JSON: {movie_vo}"
                          f"\n\t异常: {e}")

        # 为影片对象赋值并保存 ↑↑↑

        # 发行商入库 ↓↓↓
        if issuer_nm:
            if (studio_id, issuer_nm) not in set_issuer_id:
                issuer_vo = IssuerVo(id_studio=studio_id, name=issuer_nm)
                insert_result = issuer_dao.insert(issuer_vo)
                if insert_result == 1:
                    rcd_data_json.append_data_to_txt(txt_file=JSON_DATA_ISSUER, data=issuer_vo, msg="发行商", log=log)
                    set_issuer_id.add((studio_id, issuer_nm))
        # 发行商入库 ↑↑↑

        # 导演入库 ↓↓↓
        if director_id:
            if director_id not in set_director_id:
                director_vo = DirectorVo(director_id, director_nm)
                insert_result = director_dao.insert(director_vo)
                if insert_result == 1:
                    rcd_data_json.append_data_to_txt(txt_file=JSON_DATA_DIRECTOR, data=director_vo, msg="导演", log=log)
                    set_issuer_id.add((studio_id, issuer_nm))
        # 导演入库 ↑↑↑

        # 封面图保存 ↓↓↓
        places: List[Tuple[str,str]] = []
        places.append((PIC_DIR_MOVIE_COVER_PIC_ID_FANHAO, movie_vo.id))
        places.append((PIC_DIR_MOVIE_COVER_PIC_FANHAO, movie_vo.number))
        if movie_vo.big_cove:
            save_pic_util.save_pic_multi_places(url=movie_vo.big_cove, places=places, msg=f"影片封面图大, 影片: {movie_vo}", log=log)
        elif movie_vo.small_cover:
            save_pic_util.save_pic_multi_places(url=movie_vo.big_cove, places=places, msg=f"影片封面图小, 影片: {movie_vo}", log=log)
        # 封面图保存 ↑↑↑

        script_text = etree_res.xpath("/html/body/script[not(@src)]/text()")[0].replace(r'\u002F', '/')
        # 预告片保存 ↓↓↓
        search = re.search(r'trailer:"(.*?.mp4)",', script_text)
        if search:
            trailer_url = search.group(1)
            if trailer_url:
                places: List[Tuple[str, str]] = []
                places.append((PIC_DIR_MOVIE_TRAILER_ID_FANHAO, movie_vo.id))
                places.append((PIC_DIR_MOVIE_TRAILER_FANHAO, movie_vo.number))
                if movie_vo.big_cove:
                    save_pic_util.save_pic_multi_places(url=trailer_url, places=places,
                                                        msg=f"影片预告片, 影片: {movie_vo}", log=log)
        # 预告片保存 ↑↑↑

        # 预览图保存 ↓↓↓
        big_gallery_list = re.findall(r',big_img:"(.+?)"}', script_text)
        if big_gallery_list:
            dir_id_fanhao = f"{PIC_DIR_MOVIE_GALLERY_PIC_ID_FANHAO}/{movie_vo.id}_{movie_vo.number}"
            dir_fanhao = f"{PIC_DIR_MOVIE_GALLERY_PIC_FANHAO}/{movie_vo.id}_{movie_vo.number}"
            makedirs(dir_id_fanhao, exist_ok=True)
            makedirs(dir_fanhao, exist_ok=True)
            for i, big_gallery in enumerate(big_gallery_list):
                places: List[Tuple[str, str]] = []
                places.append((dir_id_fanhao, f"{movie_vo.id}_{movie_vo.number}_{str(i + 1).zfill(3)}"))
                places.append((dir_fanhao, f"{movie_vo.number}_{str(i + 1).zfill(3)}"))
                save_pic_util.save_pic_multi_places(url=big_gallery, places=places,
                                                    msg=f"影片预览图, 影片: {movie_vo}", log=log)
        # 预览图保存 ↑↑↑

        # 保存磁力链接 ↓↓↓
        match = re.match(r'window.__NUXT__=\(function\((.+)\){return {layout:"default",data:\[{movieDetail:({.+}),'
                         r'query:{.+}\((.+)\)\);',
                         script_text)
        keys = match.group(1)
        key_list = keys.split(',')
        movie_detail_str = match.group(2)
        values = match.group(3)
        value_list = values.split(',')
        value_list = [value.strip('"') for value in value_list]

        str_to_container = StrToContainer(the_str=movie_detail_str)
        movie_detail_dict = str_to_container.get_monomer()
        print(key_list)
        print(value_list)
        param_dict = {key: value_list[i] for i, key in enumerate(key_list)}
        print(param_dict)
        print(movie_detail_dict)
        trailer = movie_detail_dict.get('trailer')
        print(trailer)
        if trailer in key_list:
            trailer = [value_list[i] for i, key in enumerate(key_list) if key == trailer][0]
        print(trailer)

        # element_magnet_list = etree_res.xpath("//ul[@class='cl-u']/li")
        # if element_magnet_list:
        #     magnet_name_list = [
        #         xpath_util.get_unique(x, "./div[contains(@class,'left')]/p[@class='point']/text()").strip() for x in
        #         element_magnet_list]
        #     magnet_file_list = [
        #         xpath_util.get_unique(x, "./div[contains(@class,'left')]/div/span[@class='file']/text()") for x in
        #         element_magnet_list]
        #     magnet_file_list = [x.strip().replace('(大小：', '').replace(')', '').split(', ') for x in magnet_file_list]
        #     magnet_url_list = re.findall(r'{name:.+?,url:"(.+?)".+?}',
        #                                  re.search(r'flux_linkage:\[(.*?)],', script_text).group(1))
        #     print(script_text)
        #     print(re.search(r'flux_linkage:\[(.*?)],', script_text).group(1))
        #     print()
        #
        #     magnet_hashcode_list = [x.split('&')[0].split(':')[-1] for x in magnet_url_list]
        #     magnet_time_list = [xpath_util.get_unique(x, "./div[contains(@class,'right')]/span[@class='time']/text()")
        #                         for x in element_magnet_list]
        #     for i in range(len(magnet_name_list)):
        #         magnet_size = ''
        #         magnet_file_num = ''
        #         for file_info in magnet_file_list[i]:
        #             if file_info.endswith("B"):
        #                 magnet_size = file_info
        #             elif file_info.endswith("個文件"):
        #                 magnet_file_num = file_info
        #         magnet_vo = MagnetVo(id_fanhao=movie_vo.number, id_hashcode=magnet_hashcode_list[i],
        #                              name=magnet_name_list[i],
        #                              url=magnet_url_list[i], time=magnet_time_list[i], size=magnet_size,
        #                              file_num=magnet_file_num)
        #         insert_result = magnet_dao.insert(magnet_vo)
        #         if insert_result == 1:
        #             try:
        #                 rcd_data_json.json_file_magnet.write(f"{magnet_vo}\n")
        #                 log.info(f"json写入文件成功 magnet JSON: {magnet_vo}")
        #             except Exception as e:
        #                 log.error(f"json写入文件出现异常 magnet JSON: {magnet_vo}"
        #                           f"\n\t异常: {e}")

        # 保存磁力链接 ↑↑↑


def get_movie_detail_async(args):
    id_fanhao, actor_vo, page_num, i = args
    process_log.process4(f"获取影片信息: 第{i + 1}个 番号: {id_fanhao} 演员: {actor_vo} 第{page_num}页 Start")
    # movie_vo = get_movie_detail(id_fanhao, async_log, movie_order=i + 1)
    process_log.process4(f"获取影片信息: 第{i + 1}个 番号: {id_fanhao} 演员: {actor_vo} 第{page_num}页 End")
    # return movie_vo


def get_actor_movie_page(actor_vo: ActorVo, page_num):
    movie_list: List = []

    data = {
        'filter': 2,  # 过滤: 0-全部, 1-有字幕, 2-可下载, 3-含短评  试了下,没有更多码值
        'id': actor_vo.id,
        'page': page_num,
        'pageSize': 50,
        'sort': "1",  # 排序: 1-发布日期, 2-磁链更新  试了下,没有更多码值
        # 'cid': '2',

    }
    res = req_util.try_post_req_times(url=f"{URL_HOST_API}{API_PATH_ACTOR_MOVIE}", data=data,
                                      msg=f"获取演员影片列表: 第{page_num}页 演员: {actor_vo}")


    if res:
        dict_res = json.loads(res.text)
        print(dict_res)

        if dict_res.get('code') == 200:
            for i, dict_movie in enumerate(dict_res.get('data').get('list')):
                LogUtil.LOG_PROCESS_MOVIE_ORDER = i + 1
                if StartPoint.START_POINT_MOVIE_ORDER > 1:
                    process_log.process4(f"跳过 获取影片信息: 第{i + 1}个 第{page_num}页 演员: {actor_vo}")
                    StartPoint.START_POINT_MOVIE_ORDER -= 1
                    continue
                process_log.process4(f"获取影片信息: 第{i + 1}个 第{page_num}页 演员: {actor_vo} Start")
                movie_vo = MovieVo(**dict_movie)
                get_movie_detail(movie_vo)
                movie_list.append(movie_vo)
                process_log.process4(f"获取影片信息: 第{i + 1}个 第{page_num}页 演员: {actor_vo} End")

    # if res:
    #     etree_res = etree.HTML(res.text)
    #     url_movie_page_list = etree_res.xpath("//a[@class='movie-box']/@href")
    #     page_list = etree_res.xpath("//ul[@class='pagination pagination-lg']/li/a/text()")
    #     if page_list:
    #         if page_list[-1] == '下一頁':
    #             have_next_page = True
    #     id_fanhao_list = [url_movie_page.split('/')[-1] for url_movie_page in url_movie_page_list]

    # 同步获取影片信息
    # for i, id_fanhao in enumerate(id_fanhao_list):
    #     LogUtil.LOG_PROCESS_MOVIE_ORDER = i+1
    #     if StartPoint.START_POINT_MOVIE_ORDER > 1:
    #         process_log.process4(f"跳过 获取影片信息: 第{i + 1}个 演员: {actor_vo} 第{page_num}页")
    #         StartPoint.START_POINT_MOVIE_ORDER -= 1
    #         continue
    #     process_log.process4(f"获取影片信息: 第{i + 1}个 演员: {actor_vo} 第{page_num}页 Start")
    #     movie_vo = get_movie_detail(id_fanhao)
    #     movie_list.append(movie_vo)
    #     process_log.process4(f"获取影片信息: 第{i + 1}个 演员: {actor_vo} 第{page_num}页 End")

    # # 创建线程池, 异步多线程获取影片信息(整页开始)
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     # 开启多个线程获取影片详情
    #     futures = [executor.submit(get_movie_detail_async, args=(id_fanhao, actor_vo, page_num, i))
    #                for i, id_fanhao in enumerate(id_fanhao_list)]
    # # 等待所有线程完成并获取结果
    # for future in concurrent.futures.as_completed(futures):
    #     if future.result():
    #         movie_list.append(future.result())
    return movie_list


def get_actor_movie(actor_vo: ActorVo):
    for i in range(1, 100):
        LogUtil.LOG_PROCESS_MOVIE_PAGE = i
        LogUtil.LOG_PROCESS_MOVIE_ORDER = 0
        if StartPoint.START_POINT_MOVIE_PAGE > 1:
            process_log.process3(f"跳过 获取演员影片列表: 第{i}页 演员: {actor_vo}")
            StartPoint.START_POINT_MOVIE_PAGE -= 1
            continue
        process_log.process3(f"获取演员影片列表: 第{i}页 演员: {actor_vo} Start")
        movie_list = get_actor_movie_page(actor_vo, i)
        com_log.info(f"获取演员影片列表完成: 第{i}页 演员: {actor_vo} 结果: {movie_list}")
        process_log.process3(f"获取演员影片列表: 第{i}页 演员: {actor_vo} End")
        if not movie_list:
            process_log.process3(f"获取演员影片列表第{i}页没有数据, 不再获取下一页了")
            break


def test_get_actor_movie():
    actor_dict = {"id": 1065, "name": "小川桃果",
                  "photo": "https://wimg.9618599.com/resources//javdb_actor/avatar/47e49f088dad6c4dcdb37e8ee670b692.jpg",
                  "sex": "♀", "social_accounts": "", "movie_sum": 181, "like_sum": 28, "alias": "三田百合子,横田まり"}

    actor_vo: ActorVo = dict_to_obj2(ActorVo, actor_dict)
    get_actor_movie(actor_vo)


def test_get_movie_detail():
    dict_movie = {"id": 480766, "name": " 初老の小説家に飼われた編集者の妻 川上ゆう パンティと生写真付き", "number": "NACR-545",
                  "release_time": "2022-05-20 00:00:00", "created_at": "2022-07-31T08:21:25.000000Z", "is_download": 2,
                  "is_subtitle": 1, "is_short_comment": 1, "is_hot": 1, "is_new_comment": 2, "is_flux_linkage": 2,
                  "comment_num": 0, "score": 9,
                  "small_cover": "https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/small_cover.jpg",
                  "big_cove": "https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/big_cover.jpg",
                  "mosaic": "0", "condom": "0", "duration": "2分钟", "issue_date": "2022-05-20", "studio_nm": "プラネットプラス",
                  "studio_id": "28", "director_nm": "桜人", "director_id": "122", "issuer_nm": " ", "series_nm": "",
                  "series_id": "", "evaluators_num": "106", "labels": "已婚婦女,中出,自慰,口交,熟女,單體作品",
                  "label_ids": "89,192,197,200,377,6784", "actors": "川上ゆう♀,栗原良♂,矢野慎二♂",
                  "actor_ids": "1065,3524,3290"}

    movie_vo: MovieVo = dict_to_obj2(MovieVo, dict_movie)

    get_movie_detail(movie_vo)


if __name__ == '__main__':
    test_get_actor_movie()
    # test_get_movie_detail()
