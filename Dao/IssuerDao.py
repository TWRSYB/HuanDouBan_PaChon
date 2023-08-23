from Dao.ComDao import ComVo, ComDao
from LogUtil.LogUtil import com_log


class IssuerVo(ComVo):

    def __init__(self, id_studio, name):
        self.id_studio = id_studio  # 制片商ID
        self.name = name  # 发行商名


class IssuerDao(ComDao):

    def __init__(self):
        super().__init__()
        self.table_name = '发行商表'
        self.select_by_id_sql = f"""
                SELECT id_studio, name
                FROM huandouban.issuer
                WHERE id_studio = %s and name = %s
            """

    def insert(self, vo: IssuerVo, log=com_log):
        insert_sql = f"""
                INSERT INTO huandouban.issuer
                    (id_studio, name)
                VALUES
                    (%s, %s);
            """
        insert_data = [vo.id_studio, vo.name]
        return self.try_insert(insert_sql=insert_sql, insert_data=insert_data, vo=vo, log=log)

    def get_data_id(self, vo):
        return [vo.id_studio, vo.name]