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
    def get_institutions(self, school_name, filter=False):
        """
        获取学校名对应的学院信息,目前每个学院的信息包括
        （学院id,学院名称,一流学科数量,重点学科数,重点实验室,院士数量,杰青数,长江数, 学院学科）
        :param school_name: 学校名称
        :param filter: 是否过滤掉既没有重点实验室，也没有重点学科的学院 默认为False
        :return: 返回学院数组，如果未找到该学院，则返回空数组
        """
        sql = ("select ID as id,NAME as name,DFC_NUM as dfc_num,NKD_NUM as nkd_num,"
               "SKL_NUM as skl_num,ACADEMICIAN_NUM as academician_num,OUTSTANDING_NUM as outyouth_num,"
               "CJSP_NUM as changjiang_num from es_institution where SCHOOL_NAME = ?")
        if filter:
            sql += (" and (DFC_NUM is not null and DFC_NUM <> 0 or NKD_NUM is not null and NKD_NUM <> 0 or "
                    " SKL_NUM is not null and SKL_NUM <> 0)")
        institutions = db.select(sql, school_name)
        if len(institutions) == 0:
            return "[]"
        institution_ids = []

        keys = ["dfc_num", "nkd_num", "skl_num", "academician_num", "outyouth_num", "changjiang_num"]
        # 把为None的字段转为0
        for institution in institutions:
            institution_ids.append(institution['id'])
            for key in keys:
                if institution[key] is None:
                    institution[key] = 0
        # 获得学科
        sql = ("select INSTITUTION_ID as institution_id,DISCIPLINE_CODE as code,"
               "DFC as dfc,NKD as nkd,EVALUATION as evaluation, NAME as name,ROOT as root"
               " from es_relation_in_dis,es_discipline where INSTITUTION_ID in (%s) and "
               "es_relation_in_dis.DISCIPLINE_CODE = es_discipline.CODE")
        sql = sql % ','.join(['?'] * len(institution_ids))
        disciplines = db.select(sql, *institution_ids)
        # 把学科添加到学院中
        for discipline in disciplines:
            institution_id = discipline.pop("institution_id")
            index = institution_ids.index(institution_id)
            institution = institutions[index]

            if "disciplines" not in institution:
                institution['disciplines'] = []
            institution['disciplines'].append(discipline)

        return json.dumps(institutions, ensure_ascii=False)

    @rpc
    def get_disciplines(self, institution_ids):
        """
        根据学校名和学院名对应的学院的学科信息
        :param institution_ids: 可以是int或者数组
        :return:返回以学院id为键，其余数据为值的字典，或返回{}
        """
        sql = ("select INSTITUTION_ID as institution_id,DISCIPLINE_CODE as code,"
               "DFC as dfc,NKD as nkd,EVALUATION as evaluation, NAME as name,ROOT as root"
               " from es_relation_in_dis,es_discipline where INSTITUTION_ID in (%s) and "
               "es_relation_in_dis.DISCIPLINE_CODE = es_discipline.CODE")

        if type(institution_ids) is int:
            sql = sql % "?"
            results = db.select(sql, institution_ids)
        # 数组
        elif len(institution_ids) != 0:
            sql = sql % ','.join(['?'] * len(institution_ids))
            results = db.select(sql, *institution_ids)
        else:
            results = {}
        return json.dumps(results, ensure_ascii=False)
