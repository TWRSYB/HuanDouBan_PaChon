import json

import requests

from Dao.ActorDao import ActorVo

session = requests.Session()

params = {
    'cid': '2',
    'page': '1',
    'pageSize': '50',

}

session.headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9,application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cookie': 'promo_shown=1; __51cke__=; limited=pass; promo_shown=1; __snaker__id=yfhMSHt1lNwkJmYo; studios=%7B%22currentSecondaryIndex%22%3A2%2C%22currentCrumbsLabel%22%3A%22%E6%97%A0%E7%A0%81%22%2C%22query%22%3A%7B%22cid%22%3A2%2C%22page%22%3A1%2C%22pageSize%22%3A20%7D%7D; series=%7B%22currentSecondaryIndex%22%3A1%2C%22currentCrumbsLabel%22%3A%22%E6%97%A0%E7%A0%81%22%2C%22query%22%3A%7B%22cid%22%3A2%2C%22page%22%3A1%2C%22pageSize%22%3A20%7D%7D; actor=%7B%22currentSecondaryIndex%22%3A2%2C%22currentCrumbsLabel%22%3A%22%E6%97%A0%E7%A0%81%22%2C%22query%22%3A%7B%22cid%22%3A2%2C%22page%22%3A1%2C%22pageSize%22%3A21%7D%7D; __tins__21256849=%7B%22sid%22%3A%201692200331653%2C%20%22vd%22%3A%2021%2C%20%22expires%22%3A%201692202155356%7D; __51laig__=29',
    'origin': 'https://xultka.com',
    'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',

}
print(session.headers)
res = session.get('https://api.483b193.com/api/movie/attributes/actor/list', params=params)

res_dict = json.loads(res.text)
print(res_dict)


if res_dict.get_once('code') == 200:
    for actor_dict in res_dict.get_once('data').get_once('actorList'):
        vo = ActorVo(**actor_dict)
        print(vo)
        res_actor_page = session.get(f'https://xultka.com/actor/{vo.id}')
        print(res_actor_page.text)



# session.headers = {
#     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#     'accept-language': 'zh-CN,zh;q=0.9',
#     'cache-control': 'max-age=0',
#     'cookie': 'promo_shown=1; __51cke__=; limited=pass; promo_shown=1; __snaker__id=yfhMSHt1lNwkJmYo; studios=%7B%22currentSecondaryIndex%22%3A2%2C%22currentCrumbsLabel%22%3A%22%E6%97%A0%E7%A0%81%22%2C%22query%22%3A%7B%22cid%22%3A2%2C%22page%22%3A1%2C%22pageSize%22%3A20%7D%7D; series=%7B%22currentSecondaryIndex%22%3A1%2C%22currentCrumbsLabel%22%3A%22%E6%97%A0%E7%A0%81%22%2C%22query%22%3A%7B%22cid%22%3A2%2C%22page%22%3A1%2C%22pageSize%22%3A20%7D%7D; actor=%7B%22currentSecondaryIndex%22%3A2%2C%22currentCrumbsLabel%22%3A%22%E6%97%A0%E7%A0%81%22%2C%22query%22%3A%7B%22cid%22%3A2%2C%22page%22%3A1%2C%22pageSize%22%3A21%7D%7D; __tins__21256849=%7B%22sid%22%3A%201692200331653%2C%20%22vd%22%3A%2021%2C%20%22expires%22%3A%201692202155356%7D; __51laig__=29',
#     'sec-fetch-dest': 'document',
#     'sec-fetch-mode': 'navigate',
#     'sec-fetch-site': 'same-origin',
#     'sec-fetch-user': '?1',
#     'upgrade-insecure-requests': '1',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
#
# }


# data = {
#     'filter': "0",
#     'id': "399",
#     'page': 2,
#     'pageSize': 50,
#     'sort': "1",
#
# }
#
# res_actor_movie = session.post('https://api.483b193.com/api/actor/products', data=params)
#
# res_dict = json.loads(res.text)
# print(res_dict)