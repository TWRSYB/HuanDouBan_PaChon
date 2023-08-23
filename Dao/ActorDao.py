from Dao.ComDao import ComVo, ComDao
from LogUtil.LogUtil import com_log


class ActorVo(ComVo):

    def __init__(self, id, name, photo, sex, social_accounts, movie_sum, like_sum, in_cid_1=1, in_cid_2=1, in_cid_3=1,
                 in_cid_4=1, in_cid_10=1, alias=''):
        self.id = id  # 演员ID
        self.name = name  # 演员名
        self.photo = photo  # 演员照片
        self.sex = sex  # 演员性别
        self.social_accounts = social_accounts  # 社交账号
        self.movie_sum = movie_sum  # 影片数量
        self.like_sum = like_sum  # 收藏数量
        self.in_cid_1 = in_cid_1  # 在有码片里
        self.in_cid_2 = in_cid_2  # 在无码片里
        self.in_cid_3 = in_cid_3  # 在欧美片里
        self.in_cid_4 = in_cid_4  # 在FC2片里
        self.in_cid_10 = in_cid_10  # 在国产片里
        self.alias = alias  # 演员别名


class ActorDao(ComDao):
    def __init__(self):
        super().__init__()
        self.table_name = '演员表'
        self.select_by_id_sql = f"""
                SELECT id, name, photo, sex, social_accounts, movie_sum, like_sum, in_cid_1, in_cid_2, in_cid_3, in_cid_4, in_cid_10, alias
                FROM huandouban.actor
                WHERE id = %s
            """

    def insert(self, vo: ActorVo, log=com_log):
        insert_sql = f"""
                INSERT INTO huandouban.actor
                    (id, name, photo, sex, social_accounts, movie_sum, like_sum, 
                    in_cid_1, in_cid_2, in_cid_3, in_cid_4, in_cid_10, alias)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s);
            """
        insert_data = [vo.id, vo.name, vo.photo, vo.sex, vo.social_accounts, vo.movie_sum, vo.like_sum, 
                       vo.in_cid_1, vo.in_cid_2, vo.in_cid_3, vo.in_cid_4, vo.in_cid_10, vo.alias]
        return self.try_insert(insert_sql, insert_data, vo, log)

    def update_by_id(self, vo: ActorVo, log=com_log):
        update_sql = f"""
                        UPDATE huandouban.actor
                        SET 
                            name=%s, photo=%s, sex=%s, social_accounts=%s, movie_sum=%s, like_sum=%s, 
                            in_cid_1=%s, in_cid_2=%s, in_cid_3=%s, in_cid_4=%s, in_cid_10=%s, alias=%s
                        WHERE id=%s;
                    """
        update_data = [vo.name, vo.photo, vo.sex, vo.social_accounts, vo.movie_sum, vo.like_sum,
                       vo.in_cid_1, vo.in_cid_2, vo.in_cid_3, vo.in_cid_4, vo.in_cid_10, vo.alias,
                       vo.id]
        return self.try_update(update_sql, update_data, vo, log)

    def get_data_id(self, vo):
        return [vo.id]
