from flask import Flask
from flask import render_template
from flask import request
from nameko.standalone.rpc import ClusterRpcProxy
import json

from config import CONFIG

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/school")
def school_info():
    school_name = request.args.get("school_name")
    # 是否过滤非重点院系
    is_filter = request.args.get("filter")
    is_filter = False if is_filter is None else True
    print(is_filter)
    with ClusterRpcProxy(CONFIG) as rpc:
        # 获取该学校的学院信息
        json_str = rpc.school.get_institutions(school_name, is_filter)
        institutions = json.loads(json_str)

        if len(institutions) != 0:
            return render_template("school_info.html",
                                   school_name=school_name,
                                   institutions=institutions)
        else:
            return "暂时没有该学校的相关信息"


@app.route("/api/school/<school_name>")
def get_school_info(school_name):
    with ClusterRpcProxy(CONFIG) as rpc:
        # 获取该学校的学院信息
        json_str = rpc.school.get_institutions(school_name)
        return json_str


if __name__ == '__main__':
    app.run()
