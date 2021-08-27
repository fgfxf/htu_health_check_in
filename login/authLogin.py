import execjs
import requests
from bs4 import BeautifulSoup
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

def getEncryptedString(password, pwdDefaultEncryptSalt):
    with open("./login/encrypt.js", "r", encoding="UTF-8") as f:
        jsText = f.read()
    js = execjs.compile(jsText)
    password = password
    pwdDefaultEncryptSalt = pwdDefaultEncryptSalt
    # exec js
    encrypted = js.call("encryptAES", password, pwdDefaultEncryptSalt)

    # print(encrypted)
    return encrypted

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

# homo website login
# return cookies of home website CASTGC
def authLogin():
    # read config file
    config = configparser.RawConfigParser()
    config.read("./config/config.txt", encoding="UTF-8")
    # create session of requests
    session = requests.Session()
    url = "http://authserver2.htu.edu.cn/authserver/login"
    # get website
    res = session.get(url, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"})
    soup = BeautifulSoup(res.text, "html.parser")
    # get encrypt password
    pwdDefaultEncryptSalt = getpwdDefalutEncryptSalt( soup )
    # get lt value
    lt = getlt( soup )
    # get encrypted password
    encryptedPassword = getEncryptedString(config["UserInfo"]["password"], pwdDefaultEncryptSalt)
    # make Info
    postInfo = makeInfo(config["UserInfo"]["username"],encryptedPassword, lt)
    # logining
    res = session.post(url, headers=postInfo['head'], data=postInfo['body'])
    if isLoginSuccess(res):
        print("门户网站登录成功！")
        cookies = session.cookies.get_dict()
        CASTGC = cookies["CASTGC"]
        # get Cookies CASTG of home website
        cookies = {"CASTGC": CASTGC}
        print(cookies)
        return cookies
    else:
        print("用户名或密码错误！")
        return False

if __name__=='__main__':
    authLogin()
