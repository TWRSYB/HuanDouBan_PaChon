from Dao.ComDao import ComVo, ComDao
from LogUtil.LogUtil import ComLog, com_log


class MagnetVo(ComVo):

    def __init__(self, id_fanhao, id_hashcode, name, url, time, size, file_num):
        self.id_fanhao = id_fanhao  # 番号
        self.id_hashcode = id_hashcode  # hashcode
        self.name = name  # 名称
        self.url = url  # 链接
        self.time = time  # 时间
        self.size = size  # 大小
        self.file_num = file_num  # 文件数量


class MagnetDao(ComDao):
    def __init__(self):
        super().__init__()
        self.table_name = '磁力链接表'
        self.select_by_id_sql = f"""
                SELECT id_fanhao, id_hashcode, name, url, `time`, `size`, file_num
                FROM huandouban.magnet
                WHERE id_fanhao = %s and id_hashcode = %s
            """

    def insert(self, vo: MagnetVo, log=com_log):
        insert_sql = f"""
                INSERT INTO huandouban.magnet
                    (id_fanhao, id_hashcode, name, url, `time`, `size`, file_num)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s);
            """
        insert_data = [vo.id_fanhao, vo.id_hashcode, vo.name, vo.url, vo.time, vo.size, vo.file_num]
        return self.try_insert(insert_sql, insert_data, vo, log)

    def get_data_id(self, vo):
        return [vo.id_fanhao, vo.id_hashcode]