import json

import pymysql
from pymysql import Connection

from LogUtil.LogUtil import com_log


class ComVo:
    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)


class ComDao:
    def __init__(self):
        self.conn = Connection(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='HuanDouBan',
            autocommit=True
        )
        self.table_name = ""
        self.select_by_id_sql = ""

    def try_insert(self, insert_sql, insert_data=None, vo=None, log=com_log):
        insert_result = None
        cursor = self.conn.cursor()
        try:
            cursor.execute(insert_sql, insert_data)
            log.info(f"插入数据库成功: {self.table_name} vo:{vo}")
            insert_result = 1
        except pymysql.err.IntegrityError as e:
            exist_verity_result = self.select_by_id(vo=vo)
            if len(exist_verity_result) > 0:
                log.warning(f"插入数据库失败, 数据已存在: {self.table_name} vo:{vo}")
                insert_result = exist_verity_result
            else:
                log.error(f"插入数据库失败, 且数据不存在: {self.table_name} vo:{vo}"
                          f"\n\t异常: {e}"
                          f"\n\tInsert: {insert_sql} Data: {insert_data}")
                insert_result = 3
        except Exception as e:
            log.error(f"插入数据库失败, 插入出现异常: {self.table_name} vo:{vo}"
                      f"\n\t异常: {e}"
                      f"\n\tInsert: {insert_sql} Data: {insert_data}")
            insert_result = 4
        finally:
            cursor.close()
            return insert_result

    def select_by_id(self, vo):
        cursor = self.conn.cursor()
        select_result = ()
        try:
            cursor.execute(self.select_by_id_sql, self.get_data_id(vo))
            select_result = cursor.fetchall()
            if len(select_result) > 0:
                com_log.info(f"通过ID查找, 得到数据: {self.table_name} 结果: {select_result}")
                return select_result
            else:
                com_log.info(f"通过ID查找, 得到数据: {self.table_name} 结果: {select_result}"
                             f"\n\tselect_sql: {self.select_by_id_sql} select_data: {vo}")
        except Exception as e:
            com_log.error(f"通过ID查找发生异常: {self.table_name}"
                          f"\n\t异常: {e}"
                          f"\n\tselect_sql: {self.select_by_id_sql} select_data: {vo}")
        finally:
            cursor.close()
        return select_result

    def try_update(self, update_sql, update_data=None, vo=None, log=com_log):
        update_result = None
        cursor = self.conn.cursor()
        try:
            cursor.execute(update_sql, update_data)
            log.info(f"更新数据库成功: {self.table_name} vo:{vo}")
            update_result = 1
        except pymysql.err.IntegrityError as e:
            exist_verity_result = self.select_by_id(vo=vo)
            if len(exist_verity_result) < 1:
                log.error(f"更新数据库失败, 数据不存在: {self.table_name} vo:{vo}")
                update_result = 2
            else:
                log.error(f"更新数据库失败, 且数据已存在: {self.table_name} vo:{vo}"
                          f"\n\t异常: {e}"
                          f"\n\tInsert: {update_sql} Data: {update_data}")
                update_result = exist_verity_result
        except Exception as e:
            log.error(f"更新数据库失败, 更新出现异常: {self.table_name} vo:{vo}"
                      f"\n\t异常: {e}"
                      f"\n\tInsert: {update_sql} Data: {update_data}")
            update_result = 3
        finally:
            cursor.close()
            return update_result

    def get_data_id(self, vo):
        pass

