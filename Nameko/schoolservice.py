"""
author: sky
desc:
    get_famous_teachers_by_school 表 es_institution es_teacher
    get_discipline_by_institution 表 es_relation_in_dis
    get_teacher_ids_by_institution_id 表 teacher_discipline
    get_id_by_school_name 表 es_institution
    get_names_by_discipline_ids 表 es_discipline
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
        # 按照evaluation进行排序
        results.sort(key=lambda x: School.get_score_by_evaluation(x['evaluation']), reverse=True)

        return json.dumps(results, ensure_ascii=False)

    @staticmethod
    def get_score_by_evaluation(evaluation):
        score = 0
        if len(evaluation) == 0:
            return score
        elif len(evaluation) > 0:
            score += (ord('E') - ord(evaluation[0])) * 10
        if len(evaluation) > 1:
            if evaluation[1] == '+':
                score += 1
            elif evaluation[1] == '-':
                score -= 1
        return score

    @rpc
    def get_names_by_discipline_ids(self, discipline_list):
        """
        根据学科代码id数组获取该id对应的学科名
        :param discipline_list: 学科代码id数组
        :return:已经按照评分逆序完成的数组
        """
        # 构造sql语句
        text = "select CODE as code,NAME as name from es_discipline where CODE in (%s)"
        sql = text % ','.join(['?' for name in discipline_list])

        results = db.select(sql, *discipline_list)
        mapping = {}
        # 转换成键为code，值为name的键值对
        for result in results:
            mapping[result['code']] = result['name']

        return json.dumps(mapping, ensure_ascii=False)

    @rpc
    def get_teacher_ids_by_institution_id(self, institution_id):
        """
        根据学院id获取对应的老师id和学科id
        :param institution_id: 学院id 为integer
        :return:
        """

        sql = "select * from teacher_discipline where institution_id=?"
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

    @rpc
    def get_papers_by_author_id(self, author_id):
        """
        根据该老师的id获取该老师的所有论文
        :param author_id: 老师id
        :return: 老师论文数组生成的字符串
        """
        sql = "select name,year,cited_num,author,paper_md5 from eds_paper_clean where author_id = ?"
        results = db.select(sql, author_id)

        return json.dumps(results, ensure_ascii=False)

    @rpc
    def get_authors_by_md5_in_papers(self, md5_list):
        """
        根据论文的md5值获取对应的作者id数组
        :param md5_list: 论文的md5数组
        :return: 作者id数组(不重复)
        """
        if len(md5_list) == 0:
            return ""

        sql = "select author_id from eds_paper_clean where paper_md5 in (%s)"
        sql = sql % ','.join(['?' for name in md5_list])

        results = db.select(sql, *md5_list)
        author_id_list = set()
        for result in results:
            author_id_list.add(result['author_id'])

        return json.dumps(list(author_id_list), ensure_ascii=False)

    @rpc
    def get_title_by_id_in_teachers(self, teacher_id_list):
        """
        根据老师的id数组获取该老师的头衔
        :param teacher_id_list:
        :return: 返回以老师名称为键，头衔数组和id为值的键值对
        """
        sql = ("select ID as id,NAME as name, TITLE as title,ACADEMICIAN as academician,"
               "OUTYOUTH as outyouth,CHANGJIANG as changjiang from es_teacher where ID in (%s)"
               " and (TITLE is not null or ACADEMICIAN is not null or OUTYOUTH is not null or CHANGJIANG is not null)")
        sql = sql % ','.join(['?' for name in teacher_id_list])

        results = db.select(sql, *teacher_id_list)
        mapping = {}
        for teacher in results:
            teacher_name = teacher['name']
            teacher_id = teacher['id']
            # 添加荣誉
            honors = []
            if teacher['academician'] is not None:
                honors.append({"title": "院士", "year": teacher['academician']})
            if teacher['outyouth'] is not None:
                honors.append({"title": "杰出青年", "year": teacher['outyouth']})
            if teacher['changjiang'] is not None:
                honors.append({"title": "长江学者", "year": teacher['changjiang']})
            if teacher['title'] is not None:
                honors.append({"title": teacher['title'], "year": "0"})

            if len(honors) == 0:
                continue
            mapping[teacher_name] = {"honors": honors, "id": teacher_id}

        return json.dumps(mapping, ensure_ascii=False)
