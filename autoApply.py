import json
from urllib import parse
import requests
import datetime
import re
import os

session = requests.Session()


def login(username: str, password: str):
    session.cookies.clear()
    resp = session.get("https://auth.bupt.edu.cn/authserver/login")
    matchLT = re.findall(r'<input type="hidden" name="lt" value="(.*)" />',
                         resp.text)
    if len(matchLT) == 0:
        print("登录 CSRF 加载错误")
        return ""
    lt = matchLT[0]

    resp = session.post("https://auth.bupt.edu.cn/authserver/login",
                        data={
                            "username": username,
                            "password": password,
                            "lt": lt,
                            "execution": "e1s1",
                            "_eventId": "submit",
                            "rmShown": 1,
                        })

    matchUserInfo = re.findall(
        r'<div class="login_info">\s*<span>\s*([^\s]*)\s*</span>\s*<a href=".*" title="退出登录">',
        resp.text)
    if len(matchUserInfo) != 0:
        return matchUserInfo[0]
    return ""


def getCollege():
    resp = session.get("https://service.bupt.edu.cn/site/user/get-name")
    return resp.json()["d"]["college"]


def apply(username: str, password: str, phone: str, destination: str,
          reason: str, teacher: object):
    name = login(username, password)
    if name == "":
        print(username, "登录失败")
        return
    print(name, "登录成功")

    college = getCollege()

    date = datetime.datetime.now().replace(
        hour=0, minute=0, second=0,
        microsecond=0).isoformat(timespec="microseconds")[:-7] + "+08:00"
    beginTime = datetime.datetime.utcnow().replace(microsecond=0).isoformat(
        timespec="seconds") + ".000Z"
    endTime = datetime.datetime.now().replace(
        hour=23, minute=59, second=59,
        microsecond=0).astimezone(tz=datetime.timezone.utc).isoformat(
            timespec="microseconds").replace("000+00:00", "Z")

    data = {
        "app_id": "578",
        "node_id": "",
        "form_data": {
            "1716": {
                "User_5":
                name,  # 姓名
                "User_7":
                username,  # 学号
                "User_9":
                college,  # 学院
                "User_11":
                phone,  # 电话
                "Alert_65":
                "",
                "Alert_67":
                "",
                "Input_28":
                destination,  # 外出去向
                "Radio_52": {
                    "value": "1",
                    "name": "本人已阅读并承诺"
                },
                "Calendar_47":
                endTime,  # 返校时间
                "Calendar_50":
                beginTime,  # 外出时间
                "Calendar_62":
                date,  # 日期
                "SelectV2_58": [{
                    "name": "沙河校区",
                    "value": "1",
                    "default": 0,
                    "imgdata": ""
                }, {
                    "name": "西土城校区",
                    "value": "2",
                    "default": 0,
                    "imgdata": ""
                }],
                "Validate_63":
                "",
                "Validate_66":
                "",
                "MultiInput_30":
                reason,  # reason
                "UserSearch_60":
                teacher
            }
        },
        "userview": 1
    }

    resp = session.post(
        "https://service.bupt.edu.cn/site/apps/launch",
        data="data=" +
        parse.quote(str(data).replace("'", '"').replace(" ", "")),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "UserAgent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.38",
            "x-requested-with": "XMLHttpRequest",
        })
    resp.encoding = "utf-8"
    print(json.loads(resp.text)['m'])


if __name__ == "__main__":
    username = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    phone = os.environ['PHONE']
    destination = 'Automatic Apply Script by h0lyduck'
    reason = 'Automatic Apply Script by h0lyduck'
    teacher = {"uid": int(os.environ['TEACHER_UID']), "name": os.environ['TEACHER_NAME'], "number": os.environ['TEACHER_NUMBER']}
    print(username)
    print(phone)
    print(destination)
    print(reason)
    print(teacher)
    apply(username, password, phone, destination, reason, teacher)
