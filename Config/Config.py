# 爬虫输出目录
OUTPUT_DIR = 'D:/10.temp/06.黄豆瓣数据爬取/01.TEMP'
PIC_DIR_ACTOR_AVATAR = f"{OUTPUT_DIR}/images/Actor_avatar"
# PIC_DIR_MOVIE_COVER_PIC_ID_FANHAO = f"{OUTPUT_DIR}/images/Movie_cover_pic_id_fanhao"
PIC_DIR_MOVIE_COVER_PIC_STUDIO_FANHAO = f"{OUTPUT_DIR}/images/Movie_cover_pic_studio_fanhao"
# PIC_DIR_MOVIE_GALLERY_PIC_ID_FANHAO = f"{OUTPUT_DIR}/images/Movie_gallery_pic_id_fanhao"
PIC_DIR_MOVIE_GALLERY_PIC_STUDIO_FANHAO = f"{OUTPUT_DIR}/images/Movie_gallery_pic_studio_fanhao"
# PIC_DIR_MOVIE_TRAILER_ID_FANHAO = f"{OUTPUT_DIR}/images/Movie_trailer_id_fanhao"
PIC_DIR_MOVIE_TRAILER_STUDIO_FANHAO = f"{OUTPUT_DIR}/images/Movie_trailer_studio_fanhao"

# JSON_DATA的存储路径
JSON_DATA_STUDIO = f"{OUTPUT_DIR}/jsondatas/studio.json"
JSON_DATA_LABEL = f"{OUTPUT_DIR}/jsondatas/label.json"
JSON_DATA_SERIES = f"{OUTPUT_DIR}/jsondatas/series.json"
JSON_DATA_ACTOR = f"{OUTPUT_DIR}/jsondatas/actor.json"
JSON_DATA_MOVIE = f"{OUTPUT_DIR}/jsondatas/movie.txt"
JSON_DATA_ISSUER = f"{OUTPUT_DIR}/jsondatas/issuer.txt"
JSON_DATA_DIRECTOR = f"{OUTPUT_DIR}/jsondatas/director.txt"
JSON_DATA_MAGNET = f"{OUTPUT_DIR}/jsondatas/magnet.txt"

# 请求地址
URL_HOST = 'https://xultka.com'
URL_HOST_API = 'https://api.483b193.com'
PAGE_PATH_ACTOR = '/actor'
PAGE_PATH_MOVIE = '/moviedetail'
API_PATH_ACTOR_LIST = '/api/movie/attributes/actor/list'
API_PATH_ACTOR_DETAIL = '/api/actor/detail'
API_PATH_ACTOR_MOVIE = '/api/actor/products'
API_PATH_STUDIO_LIST = '/api/movie/attributes/film/companies/list'
API_PATH_LABEL_LIST = '/api/label/list'
API_PATH_SERIES_LIST = '/api/movie/attributes/series/list'


HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9,application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'cookie': 'promo_shown=1; __snaker__id=AVspqKKElWMVtrtU; __51cke__=; limited=pass; promo_shown=1; __snaker__id=yfhMSHt1lNwkJmYo; studios=%7B%22currentSecondaryIndex%22%3A2%2C%22currentCrumbsLabel%22%3A%22%E6%97%A0%E7%A0%81%22%2C%22query%22%3A%7B%22cid%22%3A2%2C%22page%22%3A1%2C%22pageSize%22%3A20%7D%7D; actor=%7B%22currentSecondaryIndex%22%3A2%2C%22currentCrumbsLabel%22%3A%22%E6%97%A0%E7%A0%81%22%2C%22query%22%3A%7B%22cid%22%3A2%2C%22page%22%3A1%2C%22pageSize%22%3A21%7D%7D; __tins__21256849=%7B%22sid%22%3A%201692674428696%2C%20%22vd%22%3A%206%2C%20%22expires%22%3A%201692677092486%7D; __51laig__=207',
    'pragma': 'no-cache',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'origin': 'https://xultka.com',
    'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',

}
# HEADERS = {
#     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9,application/json, text/plain, */*',
#     'accept-language': 'zh-CN,zh;q=0.9',
#     'cookie': 'promo_shown=1; __51cke__=; limited=pass; promo_shown=1; __snaker__id=yfhMSHt1lNwkJmYo; studios=%7B%22currentSecondaryIndex%22%3A2%2C%22currentCrumbsLabel%22%3A%22%E6%97%A0%E7%A0%81%22%2C%22query%22%3A%7B%22cid%22%3A2%2C%22page%22%3A1%2C%22pageSize%22%3A20%7D%7D; series=%7B%22currentSecondaryIndex%22%3A1%2C%22currentCrumbsLabel%22%3A%22%E6%97%A0%E7%A0%81%22%2C%22query%22%3A%7B%22cid%22%3A2%2C%22page%22%3A1%2C%22pageSize%22%3A20%7D%7D; actor=%7B%22currentSecondaryIndex%22%3A2%2C%22currentCrumbsLabel%22%3A%22%E6%97%A0%E7%A0%81%22%2C%22query%22%3A%7B%22cid%22%3A2%2C%22page%22%3A1%2C%22pageSize%22%3A21%7D%7D; __tins__21256849=%7B%22sid%22%3A%201692200331653%2C%20%22vd%22%3A%2021%2C%20%22expires%22%3A%201692202155356%7D; __51laig__=29',
#     'origin': 'https://xultka.com',
#     'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-fetch-dest': 'empty',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-site': 'cross-site',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
#
# }
