import requests
from bs4 import BeautifulSoup
from encrypt import getEncryptedString
import configparser

def makeInfo(username, encryptedPassword, lt):
    head = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    body = {
        "username":username,
        "password":encryptedPassword,
        "lt":lt,
        "dllt":"userNamePasswordLogin",
        "execution":"e1s1",
        "_eventId":"submit",
        "rmShown":"1"
    }

    return {
        "head": head,
        "body": body
    }

def getpwdDefalutEncryptSalt( soup ):
    input = soup.find_all('input')
    pwdDefalutEncryptSalt = input[9]['value']
    return pwdDefalutEncryptSalt

def getlt( soup ):
    input = soup.find_all('input')
    lt = input[4]['value']
    return lt

def isLoginSuccess(res):
    if res.url != "http://authserver2.htu.edu.cn/authserver/index.do":
        return False
    return True

def isYdxgLoginSuccess(res):
    if "course" in res.url:
        print("移动学工 登录成功！")
        return True
    return False

# 返回用户信息的字典
# 包括 data_post_url college name cookies
def returnInfo(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    url = soup.find_all('a')[7].attrs['href']
    # 打卡Post Url
    daka_url = "https://htu.banjimofang.com"+url

    # 学院和年纪
    college = soup.find_all('a')[1].text

    # 包含名字的字符串
    strIncName = soup.find_all("script")[0].string
    start = strIncName.find("uname")+7
    end = strIncName.find("'", start)
    # 截取名字字符串
    name = strIncName[start: end]

    userInfo = {
        "daka_post_url": daka_url,
        "college": college,
        "name": name,
        "cookies": response.cookies.get_dict()
    }

    return userInfo

def Login():
    # read config file
    config = configparser.RawConfigParser()
    config.read("./config/config.txt", encoding="UTF-8")

    session = requests.Session()
    url = "http://authserver2.htu.edu.cn/authserver/login"
    res = session.get(url, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"})
    cookies = res.cookies
    soup = BeautifulSoup(res.text, "html.parser")
    pwdDefaultEncryptSalt = getpwdDefalutEncryptSalt( soup )
    lt = getlt( soup )
    # encrypting
    encryptedPassword = getEncryptedString(config["UserInfo"]["password"], pwdDefaultEncryptSalt)
    # make Info
    postInfo = makeInfo(config["UserInfo"]["username"],encryptedPassword, lt)
    # logining
    res = session.post(url, headers=postInfo['head'], data=postInfo['body'])
    # print(res.url)
    # if login success
    if isLoginSuccess(res):
        print("门户网站登录成功！")
        # get cookies
        cookies = session.cookies.get_dict()
        CASTGC = cookies["CASTGC"]
        # print(CASTGC)
        # get Cookies CASTG of Chome website
        cookies = {"CASTGC": CASTGC}
        # ydxg logining
        ydxgUrl = "http://authserver2.htu.edu.cn/authserver/login?service=http://ydxg.htu.edu.cn/land/caslogin?ref=%2Fquickgo%2Fx8k58999"
        res = requests.get(ydxgUrl, headers={"User-Agent":"Mozilla/5.0 (Linux; Android 10; ELE-AL00 Build/HUAWEIELE-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045713 Mobile Safari/537.36 MMWEBID/8101 MicroMessenger/8.0.10.1960(0x28000A3D) Process/tools WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"}, cookies=cookies)
        print(res.url)
        # if ydxg login success
        if isYdxgLoginSuccess(res):
            # make user infomation
            userInfo = returnInfo(res)
            # print(userInfo)
            return userInfo
        else:
            print("移动学工 登录失败！")
    else:
        print("您提供的用户名或者密码有误")
    # if have any error, then return False
    return False

if __name__ == '__main__':
    info = Login()
    print(info)