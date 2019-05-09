from flask import Flask
from flask import render_template
from nameko.standalone.rpc import ClusterRpcProxy
import json

from config import CONFIG

app = Flask(__name__)


@app.route("/school/<school_name>")
def school_info(school_name):
    with ClusterRpcProxy(CONFIG) as rpc:
        # 获取该学校的学院信息
        json_str = rpc.school.get_institutions(school_name, True)
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
