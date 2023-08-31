from Dao.ComDao import ComVo, ComDao
from LogUtil.LogUtil import ComLog, com_log


class MovieVo(ComVo):

    def __init__(self, id, number, name, time, release_time, small_cover, big_cove, trailer,
                 score, score_people, comment_num, flux_linkage_num, flux_linkage_time, created_at,
                 label_names, label_ids, actor_names, actor_ids, director_name, director_id,
                 studio_name, studio_id, series_name, series_id, issuer_name):
        self.id = id  # 影片ID
        self.number = number  # 影片番号
        self.name = name  # 影片名称
        self.time = time  # 影片时长 s/60
        self.release_time = release_time  # 发行时间
        self.small_cover = small_cover  # 封面图小
        self.big_cove = big_cove  # 封面图大
        self.trailer = trailer  # 预告片
        self.score = score  # 评分
        self.score_people = score_people  # 评分人数
        self.comment_num = comment_num  # 评论数
        self.flux_linkage_num = flux_linkage_num  # 磁力连接数量
        self.flux_linkage_time = flux_linkage_time  # 磁力连接时间
        self.created_at = created_at  # 制作时间
        self.label_names = label_names  # 分类
        self.label_ids = label_ids  # 分类ID
        self.actor_names = actor_names  # 演员
        self.actor_ids = actor_ids  # 演员ID
        self.director_name = director_name  # 导演名
        self.director_id = director_id  # 导演ID
        self.studio_name = studio_name  # 制片商名
        self.studio_id = studio_id  # 制片商ID
        self.series_name = series_name  # 系列名
        self.series_id = series_id  # 系列ID
        self.issuer_name = issuer_name  # 发行商名


class MovieDao(ComDao):
    def __init__(self):
        super().__init__()
        self.table_name = '影片表'
        self.select_by_id_sql = f"""
                SELECT 
                    id, `number`, name, `time`, release_time, small_cover, big_cove, trailer, 
                    score, score_people, comment_num, flux_linkage_num, flux_linkage_time, created_at, 
                    label_names, label_ids, actor_names, actor_ids, director_name, director_id, 
                    studio_name, studio_id, series_name, series_id, issuer_name
                FROM huandouban.movie
                WHERE id = %s
            """

    def insert(self, vo: MovieVo, log=com_log):
        insert_sql = f"""
                INSERT INTO huandouban.movie
                    (id, `number`, name, `time`, release_time, small_cover, big_cove, trailer, 
                    score, score_people, comment_num, flux_linkage_num, flux_linkage_time, created_at, 
                    label_names, label_ids, actor_names, actor_ids, director_name, director_id, 
                    studio_name, studio_id, series_name, series_id, issuer_name)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
        insert_data = [vo.id, vo.number, vo.name, vo.time, vo.release_time, vo.small_cover, vo.big_cove, vo.trailer,
                       vo.score, vo.score_people, vo.comment_num, vo.flux_linkage_num, vo.flux_linkage_time, vo.created_at,
                       vo.label_names, vo.label_ids, vo.actor_names, vo.actor_ids, vo.director_name, vo.director_id,
                       vo.studio_name, vo.studio_id, vo.series_name, vo.series_id, vo.issuer_name]
        return self.try_insert(insert_sql, insert_data, vo, log)

    def select_with_condition(self, where, order_by="", limit="", args=None):
        select_sql = f"""
                SELECT 
                    id, `number`, name, `time`, release_time, small_cover, big_cove, trailer, 
                    score, score_people, comment_num, flux_linkage_num, flux_linkage_time, created_at, 
                    label_names, label_ids, actor_names, actor_ids, director_name, director_id, 
                    studio_name, studio_id, series_name, series_id, issuer_name
                FROM huandouban.movie
            """
        where = where
        order_by = order_by
        limit = limit
        args = args
        cursor = self.conn.cursor()
        cursor.execute(f"{select_sql}\n{where} \n{order_by} \n{limit}", args=args)
        fetchall = cursor.fetchall()
        return fetchall

    def get_data_id(self, vo):
        return [vo.id]
