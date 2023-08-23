from Dao.ComDao import ComVo, ComDao
from LogUtil.LogUtil import com_log


class DirectorVo(ComVo):

    def __init__(self, id, name):
        self.id = id  # 导演ID
        self.name = name  # 导演名


class DirectorDao(ComDao):

    def __init__(self):
        super().__init__()
        self.table_name = '导演表'
        self.select_by_id_sql = f"""
                SELECT id, name, MS_RESUME, MS_DETAIL, RC_RECORD_TIME, RC_RECORDER, RC_LAST_MODIFIED_TIME, RC_LAST_MODIFIER, RC_DATA_STATUS
                FROM huandouban.director
                WHERE id = %s
            """

    def insert(self, vo: DirectorVo, log=com_log):
        insert_sql = f"""
                INSERT INTO huandouban.director
                    (id, name)
                VALUES
                    (%s, %s);
            """
        insert_data = [vo.id, vo.name]
        return self.try_insert(insert_sql=insert_sql, insert_data=insert_data, vo=vo, log=log)

    def get_data_id(self, vo):
        return [vo.id]