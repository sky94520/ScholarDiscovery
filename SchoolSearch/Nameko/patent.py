from nameko.rpc import rpc
import json

import db
from config import PATENT_DB_CONFIG


# 需要预先调用，且只调用一次
db.create_engine(**PATENT_DB_CONFIG)


class Patent(object):
    name = "patent"

    @rpc
    def get_patents(self, school_name, teacher_list):
        """
        根据学校名和老师列表查询老师列表中的所有专利
        :param school_name: 学校名称
        :param teacher_list: 老师名称数组
        :return: 数组
        """
        sql = "select author_list,title,date1 from cnki_zhuanli where proposer like ?"
        results = db.select(sql, "%s%s%s" % ("%", school_name, "%"))
        patents = []
        # 对查找的数据进行筛选
        for result in results:
            author_list = result["author_list"]
            for teacher in teacher_list:
                if teacher in author_list:
                    patents.append(result)
                    break
        return json.dumps(patents, ensure_ascii=False)
