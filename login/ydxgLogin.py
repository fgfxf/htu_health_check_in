import requests
import login.authLogin

def isYdxgLoginSuccess(res):
    if "course" in res.url:
        print("移动学工 登录成功！")
        return True
    return False

# ydxg login using home website cookies   
def ydxgLogin(CASTGC_cookies):
    # ydxg logining
    ydxgUrl = r"http://authserver2.htu.edu.cn/authserver/login?service=http://ydxg.htu.edu.cn/land/caslogin?ref=%2Fquickgo%2Fx8k58999"
    res = requests.get(ydxgUrl, headers={"User-Agent":"Mozilla/5.0 (Linux; Android 10; ELE-AL00 Build/HUAWEIELE-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045713 Mobile Safari/537.36 MMWEBID/8101 MicroMessenger/8.0.10.1960(0x28000A3D) Process/tools WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"}, cookies=CASTGC_cookies)
    print(res.url)
    # if ydxg login success
    if isYdxgLoginSuccess(res):
        # return cookie
        cookie = res.cookies.get_dict()
        print(cookie)
        return cookie
    else:
        print("移动学工 登录失败！")
        return False

if __name__ == '__main__':
    cookie = login.authLogin.authLogin()
    ydxgLogin(cookie)