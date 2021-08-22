# -*- coding:UTF-8 -*-
import json
from bs4 import BeautifulSoup
import requests
import configparser
import login
import getBeijingTime
import mail

# 构造信息
def makeInfo(config, form_id):
    head = {
        'User-Agent' :"Mozilla/5.0 (Linux; Android 10; ELE-AL00 Build/HUAWEIELE-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045713 Mobile Safari/537.36 MMWEBID/8101 MicroMessenger/8.0.10.1960(0x28000A3D) Process/tools WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"
    }

    body = {
        'form_id': form_id,
        'formdata[z]': config["QianDao"]["z"],
        'formdata[x]': config["QianDao"]["x"],
        'formdata[y]': config["QianDao"]["y"],
        'formdata[w]': config["QianDao"]['w'],
        'formdata[v]': config["QianDao"]["v"],
        'formdata[a]': config["QianDao"]["a"],
        'formdata[b]': config["QianDao"]["b"],
        'formdata[c]': config["QianDao"]["c"],
        'formdata[d]': config["QianDao"]["d"],
        'formdata[e]': config["QianDao"]["e"],
        'formdata[f]': config["QianDao"]["f"],
        'formdata[g]': config["QianDao"]["g"],
        'formdata[q]': config["QianDao"]["q"],
        'formdata[h]': config["QianDao"]["h"],
        'formdata[i]': config["QianDao"]["i"],
        'formdata[j]': config["QianDao"]["j"],
        'formdata[k]': config["QianDao"]["k"],
        'formdata[l]': config["QianDao"]["l"],
        'formdata[m]': config["QianDao"]["m"],
        'formdata[n]': config["QianDao"]["n"],
        'formdata[o]': config["QianDao"]["o"],
        'formdata[p]': config["QianDao"]["p"],
        'formdata[r]': config["QianDao"]["r"],
        'formdata[s]': config["QianDao"]["s"],
        'formdata[t]': config["QianDao"]["t"],
        'formdata[u]': config["QianDao"]["u"]
    }

    return head, body

# 从文件中读取Cookies，返回Dict
def getCookieFromFile():
    cookies = ''
    with open("./cookies/cookies.txt", "r", encoding="UTF-8") as f:
        cookies = json.loads(f.read())
    return cookies

# 打印提示信息
def Msg(signRes):
    soup = BeautifulSoup(signRes.text, 'html.parser')
    msg = "打卡成功！"
    if "新增失败" in signRes.text:
        msg = soup.find_all("div")[3].string
    elif "重复提交被暂停" in signRes.text:
        msg = "重复提交被暂停，1分钟内只能提交1次！"
    elif "每日超过14:00无法再提交" in signRes.text:
        msg = "每日超过14:00无法再提交"
    print(msg)
    return msg

# 签到Post
def Post(session, postApi, config, cookies, form_id):
    
    # 获取信息
    head, body = makeInfo(config, form_id)
    # 签到Post
    signRes = session.post(postApi, headers=head, data = body, cookies = cookies)
    # print(signRes.text)
    # print(signRes.url)
    return signRes

# def log(Info, msg):
#     logDict = {
#         "time": getBeijingTime.getBeijingTimeStr(),
#         "user": Info["name"],
#         "msg": msg
#     }
#     with open("./log/loginLog.text", "a+", encoding="UTF-8") as f:
#         f.write(str(logDict) + '\n')

def getVersion():
    url = "https://raw.fastgit.org/easechen/htu_health_check_in/master/version"
    res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    js = json.loads(res.text)
    return js

def sendMail(Info, msg, config, version, isSuccess):
    updateMsg = ''
    if( version["version"] != "8.22"):
        updateMsg = version["msg"]
        print(version)
    if isSuccess:
        htmlMsg = f'''
    <html>
        <title>健康打卡推送</title>
        <div ></div>
        <head>
            
            <h1>健康打卡推送</h1>
            <h2>本程序完全开源免费<h2>
            <h2>代码仓库：<a href="https://github.com/easechen/htu_health_check_in">GitHub</a>,<a href="https://hub.fastgit.org/easechen/htu_health_check_in">镜像</a></h2>
        </head>
        <body>
            <hr>
            你好，来自 <font size="6" color="red">{Info['college']} 的 {Info['name']} !</font>
            <br>
            <br>
            打卡信息：<font size="4" color="red">{msg}</font>
            <br>
            <br>
            时间：<font size="3" color="red">{getBeijingTime.getBeijingTimeStr()}</font>
            <br>
            <font size="6" color="red">{updateMsg} </font>
            <br>
            如有问题请提出Issue或者PR。
        </body>
    </html>
'''
    else:
        htmlMsg = f'''
        <html>
        <title>健康打卡推送</title>
        <div ></div>
        <head>
            
            <h1>健康打卡推送</h1>
            <h2>本程序完全开源免费<h2>
            <h2>代码仓库：<a href="https://github.com/easechen/htu_health_check_in">GitHub</a>,<a href="https://hub.fastgit.org/easechen/htu_health_check_in">镜像</a></h2>
        </head>
        <body>
            <hr>
            <font size="6" color="red">错误！请检查配置或者更新最新代码！！</font>
            <br>
            <br>
            时间：<font size="3" color="red">{getBeijingTime.getBeijingTimeStr()}</font>
            <br>
            <font size="6" color="red">{updateMsg} </font>
            <br>
            如有问题请提出Issue或者PR。
        </body>
    </html>
        
'''
    mail.sendMail(config, htmlMsg)

# 获取form_id
def getFormId(postUrl, cookies):
    res = requests.get(postUrl,headers={'User-Agent':"Mozilla/5.0 (Linux; Android 10; ELE-AL00 Build/HUAWEIELE-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045713 Mobile Safari/537.36 MMWEBID/8101 MicroMessenger/8.0.10.1960(0x28000A3D) Process/tools WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"}, cookies=cookies)
    soup = BeautifulSoup(res.text,'html.parser')
    form_id = soup.input['value']
    return form_id

def sign():
    session = requests.session()
    config = configparser.RawConfigParser()
    config.read("./config/config.txt", encoding="UTF-8")
    version = getVersion()
    # 登录
    Info = login.Login()
    # 登录失败
    if Info == False:
        sendMail(None, None, config, version, False)
        return False

    print(f"你好，来自 {Info['college']} 的 {Info['name']} !")
    # Post APi
    postUrl = Info["daka_post_url"]
    # 签到
    # cookies
    cookies = Info["cookies"]
    form_id = getFormId(postUrl, cookies)
    signRes = Post(session, postUrl, config, cookies, form_id)
    
    # 打印用户提示信息
    msg = Msg(signRes)
    if config["Mail"]["isOpen"] == 'on':
        sendMail(Info, msg, config, version, True)

if __name__=='__main__':
    sign()