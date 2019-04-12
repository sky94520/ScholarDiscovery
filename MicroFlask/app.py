from flask import Flask
from flask import render_template
import time
from nameko.standalone.rpc import ClusterRpcProxy
import json

from config import CONFIG

app = Flask(__name__)


@app.route('/')
def hello_world():

    return "hello world"


@app.route('/teachers/<school_name>/<institution_name>')
def teacher_info(school_name, institution_name):
    startTime = time.time()
    with ClusterRpcProxy(CONFIG) as rpc:
        # 学校名 => 学校ID
        info = rpc.school.get_id_by_school_name(school_name, institution_name)
        if len(info) == 0:
            return "学校名或者学院名输入有误"
        school_id = info['school_id']
        institution_id = info['institution_id']
        # 获取该学院的带有头衔的所有老师
        result = rpc.school.get_famous_teachers_by_school(school_id, institution_id)
        # 转换成字典
        teachers = json.loads(result)

        # 获取学院id对应的teacher_id和学科id
        result = rpc.school.get_teacher_ids_by_institution_id(institution_id)
        teachers_dis_mapping = json.loads(result)

        # 按学科划分老师
        dis_teachers = {}
        for dis in teachers_dis_mapping:
            discipline_id = dis['discipline_id']
            teacher_id = str(dis['teacher_id'])
            if discipline_id not in dis_teachers:
                dis_teachers[discipline_id] = []

            if teacher_id in teachers:
                dis_teachers[discipline_id].append(teachers[teacher_id])

        print(dis_teachers)
        print(teachers)
        # 学校信息
        result = rpc.school.get_discipline_by_institution(institution_id)
        disciplines = json.loads(result)

    print(time.time() - startTime)

    return render_template("teachers.html",
                           disciplines=disciplines,
                           dis_teachers=dis_teachers)


if __name__ == '__main__':
    app.run()
