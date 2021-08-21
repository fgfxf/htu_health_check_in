# -*- coding:UTF-8 -*-
import execjs

def getEncryptedString(password, pwdDefaultEncryptSalt):
    with open("encrypt.js", "r", encoding="UTF-8") as f:
        jsText = f.read()
    js = execjs.compile(jsText)
    password = password
    pwdDefaultEncryptSalt = pwdDefaultEncryptSalt
    # exec js
    encrypted = js.call("encryptAES", password, pwdDefaultEncryptSalt)

    # print(encrypted)
    return encrypted