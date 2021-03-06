"""
author: sky
desc: get_famous_teachers_by_school 表 es_institution es_teacher
"""
from nameko.rpc import rpc
import json
import time

import db
from config import DB_CONFIG


# 需要预先调用，且只调用一次
db.create_engine(**DB_CONFIG)


class School(object):
    name = "school"

    @rpc
    def get_famous_teachers_by_school(self, school_id, institution_id):
        """
        根据学校名和学院名获取院士、杰出青年和长江学者
        :param school_id:
        :param institution_id:
        :return:
        """

        sql = ("select ID as teacher_id,NAME as name,BIRTHYEAR as birthyear,"
               "ACADEMICIAN as academician,OUTYOUTH as outyouth,CHANGJIANG as changjiang"
               " from es_teacher where SCHOOL_ID =? and INSTITUTION_ID = ? "
               " and (ACADEMICIAN is not null or OUTYOUTH is not null or CHANGJIANG is not null)")

        results = db.select(sql, school_id, institution_id)
        # 转换成teacher_id为键，其余值为dict的dict
        teachers = {}

        for result in results:
            teacher_id = result.pop("teacher_id")
            if result['birthyear'] is not None:
                result['years-old'] = time.localtime(time.time()).tm_year - int(result['birthyear'])
            else:
                result['years-old'] = None
            teachers[teacher_id] = result

        return json.dumps(teachers, ensure_ascii=False)

    @rpc
    def get_discipline_by_institution(self, institution_id):
        """
        根据学校名和学院名对应的学院的学科信息
        :param institution_id:
        :return:
        """

        sql = ("select INSTITUTION_ID as institution_id,DISCIPLINE_CODE as discipline_code,"
               "DFC as dfc,NKD as nkd,EVALUATION as evaluation from es_relation_in_dis where INSTITUTION_ID=?")
        results = db.select(sql, institution_id)

        return json.dumps(results, ensure_ascii=False)

    @rpc
    def get_teacher_ids_by_institution_id(self, institution_id):
        """
        根据学院id获取对应的老师id和学科id
        :param institution_id: 学院id 为integer
        :return:
        """

        sql = ("select * from teacher_discipline where institution_id=?")
        results = db.select(sql, institution_id)

        return json.dumps(results, ensure_ascii=False)

    @rpc
    def get_id_by_school_name(self, school_name, institution_name):
        """
        根据学校的名字和学院名获取对应的学校id和学院id，若不存在则返回空的字典
        :param school_name: 学校名
        :param institution_name: 学院名
        :return: {school_id: 1, institution_id: 1}
        """
        sql = ("select SCHOOL_ID as school_id, ID as institution_id"
               " from es_institution where SCHOOL_NAME = ? and NAME=?")
        # 查找
        results = db.select(sql, school_name, institution_name)

        if len(results) == 0:
            return {}
        else:
            return results[0]
