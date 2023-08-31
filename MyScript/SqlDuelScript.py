

print('CREATE TABLE xxx (')

# out_attributes = [attr for attr in dir(MyClass) if not callable(getattr(MyClass, attr)) and attr != "__init__" and not attr.startswith("__")]

out_attributes = """

"""

init_attributes = """
        self.id = id                                        # 影片ID
        self.number = number                                # 影片番号
        self.name = name                                    # 影片名称
        self.time = time                                    # 影片时长 s/60
        self.release_time = release_time                    # 发行时间
        self.small_cover = small_cover                      # 封面图小
        self.big_cove = big_cove                            # 封面图大
        self.trailer = trailer                              # 预告片
        self.score = score                                  # 评分
        self.score_people = score_people                    # 评分人数
        self.comment_num = comment_num                      # 评论数
        self.flux_linkage_num = flux_linkage_num            # 磁力连接数量
        self.flux_linkage_time = flux_linkage_time          # 磁力连接时间
        self.created_at = created_at                        # 制作时间
        self.label_names = label_names                      # 分类
        self.label_ids = label_ids                          # 分类ID
        self.actor_names = actor_names                      # 演员
        self.actor_ids = actor_ids                          # 演员ID
        self.director_name = director_name                  # 导演名
        self.director_id = director_id                      # 导演ID
        self.studio_name = studio_name                      # 制片商名
        self.studio_id = studio_id                          # 制片商ID
        self.series_name = series_name                      # 系列名
        self.series_id = series_id                          # 系列ID
        self.issuer_name = issuer_name                      # 发行商名
"""

out_attribute_list = out_attributes.splitlines()

out_attribute_list = [(x.split(":")[0].split("=")[0].strip(), x.split('#')[-1].strip() if '#' in x else '') for x in
                      out_attribute_list if x.strip() != ""]

init_attribute_list = init_attributes.splitlines()

init_attribute_list = [
    (x.split(":")[0].split("=")[0].replace('self.', '').strip(), x.split('#')[-1].strip() if '#' in x else '') for x in
    init_attribute_list if x.strip().startswith('self.')]

attribute_list = init_attribute_list + [x for x in out_attribute_list if
                                        x[0] not in [x[0] for x in init_attribute_list]]

for attribute in attribute_list:
    t_num = '\t' * (8 - len(attribute[0]) // 4)
    comment = attribute[1]
    print(f"\t{attribute[0]}{t_num}VARCHAR(255)\t\tNOT NULL\t\tDEFAULT ' '\t\tCOMMENT '{comment}',")

	# MS_RESUME						VARCHAR(300)		NOT NULL		DEFAULT ' '							COMMENT '简述',
	# MS_DETAIL						VARCHAR(1000)		NOT NULL		DEFAULT ' '							COMMENT '详细',
	# RC_RECORD_TIME					TIMESTAMP			NOT NULL		DEFAULT CURRENT_TIMESTAMP			COMMENT '收录时间',
	# RC_RECORDER						VARCHAR(50)			NOT NULL		DEFAULT '未收录'						COMMENT '收录人',
	# RC_LAST_MODIFIED_TIME			TIMESTAMP			COMMENT '最后修改时间',
	# RC_LAST_MODIFIER				VARCHAR(50)			NOT NULL		DEFAULT '未收录'						COMMENT '最后修改人',
	# RC_DATA_STATUS					CHAR(1)				NOT NULL		DEFAULT '0'							COMMENT '数据状态: 0-未生效, 1-正常, 2-不可用,9-废弃',
print("""
	CONSTRAINT class_pk PRIMARY KEY (,)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_bin
COMMENT=;
""")