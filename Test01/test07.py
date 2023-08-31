import re

dict_movie_list = []
with open(file=r'D:\34.Temp\06.黄豆瓣数据爬取\01.TEMP_wait\logs_阶段5_cid2/Async_error - 副本.log', mode='r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        match = re.match(r'2023-08-.+movie_vo: ({.+}) res: .+', line)
        if match:
            dict_movie_list.append(eval(match.group(1)))
print(dict_movie_list)
print(len(dict_movie_list))
for dict_movie in dict_movie_list:
    print(dict_movie)
    print(type(dict_movie))