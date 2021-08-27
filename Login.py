# -*- coding:UTF-8 -*-
from login.authLogin import authLogin
from login.ydxgLogin import ydxgLogin

def Login():
    authCookie = authLogin()
    ydxgCookie = ydxgLogin(authCookie)
    return ydxgCookie

if __name__ == '__main__':
    Login()