from flask import Flask
from flask import render_template
from nameko.standalone.rpc import ClusterRpcProxy
import json

from config import CONFIG

app = Flask(__name__)


@app.route('/')
def hello_world():

    return "hello world"


@app.route('/teachers/<school_name>/<institution_name>')
def teacher_info(school_name, institution_name):
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

        # 学校代码信息
        result = rpc.school.get_discipline_by_institution(institution_id)
        disciplines = json.loads(result)
        # 获取学科的id数组
        discipline_ids = []
        for discipline in disciplines:
            discipline_ids.append(discipline["discipline_code"])
        # 获取学科对应的名称
        json_str = rpc.school.get_names_by_discipline_ids(discipline_ids)
        discipline_mapping = json.loads(json_str)

    return render_template("teachers.html",
                           disciplines=disciplines,
                           teachers=teachers,
                           discipline_mapping=discipline_mapping)


@app.route("/teacher/<teacher_name>/<int:teacher_id>")
def teacher_detail(teacher_name, teacher_id):
    with ClusterRpcProxy(CONFIG) as rpc:
        # 获取该老师的所有论文
        json_str = rpc.school.get_papers_by_author_id(teacher_id)

        papers = json.loads(json_str)
        # 获取论文的md5

    return render_template("teacher_detail.html",
                           papers=papers,
                           teacher_id=teacher_id,
                           teacher_name=teacher_name)


if __name__ == '__main__':
    app.run()
