import json
import os
import traceback
from typing import List, Dict

from Config.Config import JSON_DATA_MOVIE, JSON_DATA_MAGNET
from LogUtil.LogUtil import com_log


class RcdDataJson:

    json_file_movie = open(JSON_DATA_MOVIE, 'a', encoding='utf-8')
    json_file_magnet = open(JSON_DATA_MAGNET, 'a', encoding='utf-8')

    def append_data_to_txt(self, txt_file, data, msg="", log=com_log):
        try:
            with open(file=txt_file, mode='a', encoding="utf-8") as jf:
                jf.write(f"{data}\n")
                log.info(f"json写入文件成功 路径: {txt_file} JSON: {data} msg: {msg}")
        except Exception as e:
            log.error(f"json写入文件出现异常 路径: {txt_file} JSON: {data} "
                      f"\n\tmsg: {msg}"
                      f"\n\t异常: {e}")



    def add_data_to_json_list(self, json_file, data, msg="", log=com_log):
        try:
            # 检查文件是否存在
            if os.path.exists(json_file):
                # 如果文件存在，则读取JSON数据
                with open(json_file, 'r', encoding='utf-8') as f:
                    data_list = json.load(f)
            else:
                # 如果文件不存在，则创建一个空的列表数据
                data_list = []
            if isinstance(data, Dict):
                data_list.append(data)
            else:
                data_list.append(vars(data))

            # 将修改后的JSON数据写回到文件中
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, ensure_ascii=False)
                log.info(f"json添加成功 路径: {json_file} JSON: {data} msg: {msg}")
        except Exception as e:
            log.error(f"json添加出现异常 路径: {json_file} JSON: {data} "
                      f"\n\tmsg: {msg}"
                      f"\n\t异常: {e}"
                      f"{traceback.format_exc()}")

    def update_dict_json(self, json_file, new_entry, msg="", log=com_log):
        try:
            # 如果文件存在，则读取JSON数据
            with open(json_file, 'w+', encoding='utf-8') as f:

                if f.read().strip() == "":
                    data_dict = {}
                else:
                    data_dict = json.load(f)

                data_dict.update(new_entry)
                json.dump(data_dict, f, ensure_ascii=False)
                log.info(f"更新dict_json成功 路径: {json_file} new_entry: {new_entry} msg: {msg}")

        except Exception as e:
            log.error(f"更新dict_json出现异常 路径: {json_file} new_entry: {new_entry} "
                      f"\n\tmsg: {msg}"
                      f"\n\t异常: {e}"
                      f"{traceback.format_exc()}")

    def add_data_to_json_dict(self, json_file, key, value, msg="", log=com_log):
        try:
            # 检查文件是否存在
            if os.path.exists(json_file):
                # 如果文件存在，则读取JSON数据
                with open(json_file, 'r', encoding='utf-8') as f:
                    data_dict = json.load(f)
            else:
                # 如果文件不存在，则创建一个空的列表数据
                data_dict = {}
            data_dict[key] = value if isinstance(value, Dict) else vars(value)

            # 将修改后的JSON数据写回到文件中
            try:
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data_dict, f, ensure_ascii=False)
                    log.info(f"json添加成功 路径: {json_file}, key: {key}, value: {value} msg: {msg}")
            except Exception as e:
                log.error(f"json添加出现异常(写入) 路径: {json_file}, key: {key}, value: {value} "
                          f"\n\tmsg: {msg}"
                          f"\n\t异常: {e}"
                          f"\n\tdata_dict: {data_dict}"
                          f"\n\tdata_dict[key]: {data_dict[key]}"
                          f"{traceback.format_exc()}")
        except Exception as e:
            log.error(f"json添加出现异常 路径: {json_file}, key: {key}, value: {value} "
                      f"\n\tmsg: {msg}"
                      f"\n\t异常: {e}"
                      f"{traceback.format_exc()}")

    def update_data_to_json(self, json_file, data, update_by_list: List, msg="", log=com_log):
        try:
            # 检查文件是否存在
            if os.path.exists(json_file):
                # 如果文件存在，则读取JSON数据
                with open(json_file, 'r', encoding='utf-8') as f:
                    data_list = json.load(f)
            else:
                # 如果文件不存在，则创建一个空的列表数据
                data_list = []
            match = False
            for i, item in enumerate(data_list):
                for update_by in update_by_list:
                    if str(item.get(update_by[0])) == str(update_by[1]):
                        match = True
                    else:
                        match = False
                        break
                if match:
                    data_list[i] = vars(data)
                    break
            if match:
                # 将修改后的JSON数据写回到文件中
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data_list, f, ensure_ascii=False)
                    log.info(f"json更新成功 路径: {json_file} JSON: {data} msg: {msg}")
            else:
                log.error(f"json更新失败, 没有找到数据 路径: {json_file} JSON: {data} msg: {msg}")
        except Exception as e:
            log.error(f"json更新出现异常 路径: {json_file} JSON: {data} "
                      f"\n\tmsg: {msg}"
                      f"\n\t异常: {e}"
                      f"{traceback.format_exc()}")

    def delete_data_from_json_dict(self, json_file, delete_key, msg="", log=com_log):
        try:
            # 检查文件是否存在
            if os.path.exists(json_file):
                # 如果文件存在，则读取JSON数据
                with open(json_file, 'r', encoding='utf-8') as f:
                    data_dict = json.load(f)
            else:
                # 如果文件不存在，则创建一个空的列表数据
                data_dict = {}
            match = False
            for key, value in data_dict.items():
                if str(key) == str(delete_key):
                    match = True
                    del data_dict[key]
                    break
            if match:
                # 将修改后的JSON数据写回到文件中
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data_dict, f, ensure_ascii=False)
                    log.info(f"json删除数据成功 路径: {json_file} delete_key: {delete_key} msg: {msg}")
            else:
                log.error(f"json删除数据失败, 没有找到数据 路径: {json_file} delete_key: {delete_key} msg: {msg}")
        except Exception as e:
            log.error(f"json删除数据出现异常 路径: {json_file} delete_key: {delete_key} "
                      f"\n\tmsg: {msg}"
                      f"\n\t异常: {e}"
                      f"{traceback.format_exc()}")


rcd_data_json = RcdDataJson()


if __name__ == '__main__':
    rcd_data_json.update_dict_json('/test.json', )
