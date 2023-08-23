from Dao.ComDao import ComVo, ComDao
from LogUtil.LogUtil import com_log


class StudioVo(ComVo):

    def __init__(self, id, name, movie_sum, like_sum, in_cid_1=1, in_cid_2=1, in_cid_3=1, in_cid_4=1, in_cid_10=1):
        self.id = id  # 制片商ID
        self.name = name  # 制片商名
        self.movie_sum = movie_sum  # 影片数量
        self.like_sum = like_sum  # 收藏数量
        self.in_cid_1 = in_cid_1  # 有码
        self.in_cid_2 = in_cid_2  # 无码
        self.in_cid_3 = in_cid_3  # 欧美
        self.in_cid_4 = in_cid_4  # FC2
        self.in_cid_10 = in_cid_10  # 国产


class StudioDao(ComDao):

    def __init__(self):
        super().__init__()
        self.table_name = '制片商表'
        self.select_by_id_sql = f"""
                SELECT 
                    id, name, movie_sum, like_sum, in_cid_1, in_cid_2, in_cid_3, in_cid_4, in_cid_10
                FROM huandouban.studio
                WHERE id = %s
            """

    def insert(self, vo: StudioVo, log=com_log):
        insert_sql = f"""
                INSERT INTO huandouban.studio
                    (id, name, movie_sum, like_sum, in_cid_1, in_cid_2, in_cid_3, in_cid_4, in_cid_10)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
        insert_data = [vo.id, vo.name, vo.movie_sum, vo.like_sum, vo.in_cid_1, vo.in_cid_2, vo.in_cid_3, vo.in_cid_4,
                       vo.in_cid_10]
        return self.try_insert(insert_sql=insert_sql, insert_data=insert_data, vo=vo, log=log)

    def update_by_id(self, vo: StudioVo, log=com_log):
        update_sql = f"""
                UPDATE huandouban.studio
                SET 
                    name=%s, movie_sum=%s, like_sum=%s, in_cid_1=%s, in_cid_2=%s, in_cid_3=%s, in_cid_4=%s, in_cid_10=%s
                WHERE id=%s;
            """
        update_data = [vo.name, vo.movie_sum, vo.like_sum, vo.in_cid_1, vo.in_cid_2, vo.in_cid_3, vo.in_cid_4,
                       vo.in_cid_10, vo.id]
        return self.try_update(update_sql=update_sql, update_data=update_data, vo=vo, log=log)

    def get_data_id(self, vo):
        return [vo.id]