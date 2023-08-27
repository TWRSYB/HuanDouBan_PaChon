from Dao.ComDao import ComVo, ComDao
from LogUtil.LogUtil import ComLog, com_log


class MovieVo(ComVo):

    def __init__(self, id, name, number, release_time, created_at, is_download, is_subtitle, is_short_comment,
                 is_hot,
                 is_new_comment, is_flux_linkage, comment_num, score, small_cover, big_cove,
                 time='',
                 trailer='',
                 duration='',
                 issue_date='',
                 studio_nm='',
                 studio_id='',
                 director_nm='',
                 director_id='',
                 issuer_nm='',
                 series_nm='',
                 series_id='',
                 evaluators_num='',
                 labels='',
                 label_ids='',
                 actors='',
                 actor_ids=''):
        # 影片列表接口返回的数据 ↓↓↓
        self.id = id  # 影片ID
        self.name = name  # 影片名称
        self.number = number  # 影片番号
        self.release_time = release_time  # 发行时间
        self.created_at = created_at  # 制作时间
        self.is_download = is_download  # 可下载(1-否, 2-是)
        self.is_subtitle = is_subtitle  # 有字幕(1-无, 2-有)
        self.is_short_comment = is_short_comment  # 含短评(1-无, 2-有)
        self.is_hot = is_hot  # 热的
        self.is_new_comment = is_new_comment  # 今日新评
        self.is_flux_linkage = is_flux_linkage  # 今日新种
        self.comment_num = comment_num  # 评论数量
        self.score = score  # 评分
        self.small_cover = small_cover  # 小背景图
        self.big_cove = big_cove  # 大背景图
        # 影片列表接口返回的数据 ↑↑↑

        # 影片详情页获得的数据 ↓↓↓
        self.time = time  # 播放时间 s/60
        self.trailer = trailer  # 预告片
        self.duration = duration  # 时长
        self.issue_date = issue_date  # 发行日期
        self.studio_nm = studio_nm  # 制片商
        self.studio_id = studio_id  # 制片商ID
        self.director_nm = director_nm  # 导演
        self.director_id = director_id  # 导演ID
        self.issuer_nm = issuer_nm  # 发行商
        self.series_nm = series_nm  # 系列
        self.series_id = series_id  # 系列ID
        self.evaluators_num = evaluators_num  # 评价人数
        self.labels = labels  # 标签
        self.label_ids = label_ids  # 标签ID
        self.actors = actors  # 演员
        self.actor_ids = actor_ids  # 演员ID
        # 影片详情页获得的数据 ↑↑↑


class MovieDao(ComDao):
    def __init__(self):
        super().__init__()
        self.table_name = '影片表'
        self.select_by_id_sql = f"""
                SELECT 
                    id, name, `number`, 
                    release_time, created_at, 
                    is_download, is_subtitle, is_short_comment, is_hot, is_new_comment, is_flux_linkage, 
                    comment_num, score, small_cover, big_cove, 
                    `time`, trailer, 
                    duration, issue_date, 
                    studio_nm, studio_id, director_nm, director_id, issuer_nm, series_nm, series_id, 
                    evaluators_num, labels, label_ids, actors, actor_ids
                FROM huandouban.movie
                WHERE id = %s
            """

    def insert(self, vo: MovieVo, log=com_log):
        insert_sql = f"""
                INSERT INTO huandouban.movie
                    (id, name, `number`, 
                    release_time, created_at, 
                    is_download, is_subtitle, is_short_comment, is_hot, is_new_comment, is_flux_linkage, 
                    comment_num, score, small_cover, big_cove, 
                    `time`, trailer, 
                    duration, issue_date, 
                    studio_nm, studio_id, director_nm, director_id, issuer_nm, series_nm, series_id, 
                    evaluators_num, labels, label_ids, actors, actor_ids)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
        insert_data = [vo.id, vo.name, vo.number,
                       vo.release_time, vo.created_at,
                       vo.is_download, vo.is_subtitle, vo.is_short_comment, vo.is_hot, vo.is_new_comment, vo.is_flux_linkage,
                       vo.comment_num, vo.score, vo.small_cover, vo.big_cove,
                       vo.time, vo.trailer,
                       vo.duration, vo.issue_date,
                       vo.studio_nm, vo.studio_id, vo.director_nm, vo.director_id, vo.issuer_nm, vo.series_nm,vo.series_id,
                       vo.evaluators_num, vo.labels, vo.label_ids, vo.actors, vo.actor_ids]
        return self.try_insert(insert_sql, insert_data, vo, log)

    def select_with_condition(self, where, order_by = "", limit="", args=None):
        select_sql = f"""
                SELECT 
                    id, name, `number`, 
                    release_time, created_at, 
                    is_download, is_subtitle, is_short_comment, is_hot, is_new_comment, is_flux_linkage, 
                    comment_num, score, small_cover, big_cove, 
                    `time`, trailer, 
                    duration, issue_date, 
                    studio_nm, studio_id, director_nm, director_id, issuer_nm, series_nm, series_id, 
                    evaluators_num, labels, label_ids, actors, actor_ids
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
