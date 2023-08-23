from Dao.ComDao import ComVo, ComDao
from LogUtil.LogUtil import com_log


class LabelVo(ComVo):

    def __init__(self, id, name, in_cid_1=1, in_cid_2=1, in_cid_3=1, in_cid_4=1, in_cid_10=1, parent_id=0):
        self.id = id  # 制片商ID
        self.name = name  # 制片商名
        self.in_cid_1 = in_cid_1  # 在有码片里
        self.in_cid_2 = in_cid_2  # 在无码片里
        self.in_cid_3 = in_cid_3  # 在欧美片里
        self.in_cid_4 = in_cid_4  # 在FC2片里
        self.in_cid_10 = in_cid_10  # 在国产片里
        self.parent_id = parent_id  # 父标签


class LabelDao(ComDao):
    def __init__(self):
        super().__init__()
        self.table_name = '标签表'
        self.select_by_id_sql = f"""
                SELECT 
                    id, name, in_cid_1, in_cid_2, in_cid_3, in_cid_4, in_cid_10, parent_id
                FROM huandouban.label
                WHERE id = %s
            """

    def insert(self, vo: LabelVo, log=com_log):
        insert_sql = f"""
                INSERT INTO huandouban.label
                    (id, name, in_cid_1, in_cid_2, in_cid_3, in_cid_4, in_cid_10, parent_id)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s);
            """
        insert_data = [vo.id, vo.name, vo.in_cid_1, vo.in_cid_2, vo.in_cid_3, vo.in_cid_4, vo.in_cid_10, vo.parent_id]
        return self.try_insert(insert_sql=insert_sql, insert_data=insert_data, vo=vo, log=log)

    def update_by_id(self, vo: LabelVo, log=com_log):
        update_sql = f"""
                UPDATE huandouban.label
                SET 
                    name=%s, in_cid_1=%s, in_cid_2=%s, in_cid_3=%s, in_cid_4=%s, in_cid_10=%s, parent_id=%s
                WHERE id=%s;
            """
        update_data = [vo.name, vo.in_cid_1, vo.in_cid_2, vo.in_cid_3, vo.in_cid_4, vo.in_cid_10, vo.parent_id, vo.id]
        return self.try_update(update_sql, update_data, vo, log)

    def get_data_id(self, vo):
        return [vo.id]