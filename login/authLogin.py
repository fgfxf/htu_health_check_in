#!/usr/bin/python
#coding=utf-8
import requests
import re
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import padding
import base64
import random
import time
import math
#python 在 Windows下使用AES时要安装的是pycryptodome 模块   pip install pycryptodome 
#python 在 Linux下使用AES时要安装的是pycrypto模块   pip install pycrypto 

proxies={'http':'http://127.0.0.1:8080','https':'https://127.0.0.1:8080'}  # debug查看发包

def GetAuthLog():
    print("【info】登录到统一认证平台")
    Login="http://authserver2.htu.edu.cn/authserver/login"
    header={
        'Host': 'authserver2.htu.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Connection': 'close',
        }
    response=requests.get(url=Login,headers=header)
    print(response)
    ex='id="pwdDefaultEncryptSalt" value=\"(.*?)\"'
    pwdDefaultEncryptSalt=re.findall(ex,response.text,re.S)
    ex2='input type="hidden" name="lt" value=\"(.*?)\"'
    lt=re.findall(ex2,response.text,re.S)
    cookie=response.headers['Set-Cookie']
    return cookie,pwdDefaultEncryptSalt,lt

def  _rds(lenth):
    retStr=""
    HtuDic="ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
    for i in range(0,lenth):
        retStr+= HtuDic[math.floor(random.random()*len(HtuDic))]
    return retStr

def __pad(text):
    """填充方式，加密内容必须为16字节的倍数，若不足则使用self.iv进行填充"""
    text_length = len(text)
    amount_to_pad = AES.block_size - (text_length % AES.block_size)
    if amount_to_pad == 0:
        amount_to_pad = AES.block_size
    pad = chr(amount_to_pad)
    return text + pad * amount_to_pad

def AesEncrypt(password,key,iv):
    password=__pad(password).encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(cipher.encrypt(password))

def __unpad(text):
    pad = ord(text[-1])
    return text[:-pad]

def AesDecrypt(enc,key,iv):
    """解密"""
    enc = base64.b64decode(enc)
    cipher = AES.new(key, AES.MODE_CBC,iv )
    return __unpad(cipher.decrypt(enc).decode("utf-8"))

def HtuAesEncrypt(password,salt):
    iv= _rds(16).encode('utf-8')
    password=_rds(64)+password
    encode_context=AesEncrypt(password,salt.encode('utf-8'),iv)
    decode_context=AesDecrypt(encode_context,salt.encode('utf-8'),iv)
    return encode_context,decode_context
    



def PostToLogin(cookie,username,password,lt):
    AuthIndex="http://authserver2.htu.edu.cn/authserver/login"
    data={
    'username':username,
    'password':password,
    'lt':lt,
    'dllt':'userNamePasswordLogin',
    'execution':'e1s1',
    '_eventId':'submit',
    'rmShown':1
        }
    
    header={
        'Host': 'authserver2.htu.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Connection': 'close',
        'Cookie':cookie,
        'Content-Length': '275',
        'Content-Type': 'application/x-www-form-urlencoded'


        }
    response=requests.post(url=AuthIndex,headers=header,data=data,allow_redirects=False)
    return response

def GetRedirects(Location,cookie,UA):
    header={
   #'Host': 'authserver2.htu.edu.cn',
    'User-Agent':UA,
    'Accept-Encoding': 'gzip, deflate',
    'Accept': '*/*',
    'Connection': 'close',
    'Cookie':cookie,
    }
    response=requests.get(url=Location,headers=header,allow_redirects=False)
    return response

def LoginHTU(username,password):
    cookie,pwdDefaultEncryptSalt,lt=GetAuthLog()
    pwdDefaultEncryptSalt=pwdDefaultEncryptSalt[0]
    lt=lt[0]
    cookie=cookie.split(';')
    cookie=cookie[0].split(',')
    route=cookie[0]
    JSESSIONID=cookie[1]
    security_check="org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN"
    encode,decode=HtuAesEncrypt(password,pwdDefaultEncryptSalt)
    logincookie=route+';'+JSESSIONID+';'+security_check
    time.sleep(2)
    response=PostToLogin(logincookie,username,encode,lt)
    Location=response.headers['Location']
    cookiestr=response.headers['SET-COOKIE']
    CASTGC=re.findall('CASTGC=(.*?);',cookiestr,re.S)
    iPlanetDirectoryPro=re.findall('iPlanetDirectoryPro=(.*?);',cookiestr,re.S)

    cookie="CASTGC="+CASTGC[0]+";"+route+';'+JSESSIONID+";"+"iPlanetDirectoryPro="+iPlanetDirectoryPro[0]

    UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36';
    response=GetRedirects(Location,cookie,UA)
    while(response.status_code==302):
        Location=response.headers['Location']
        response=GetRedirects(Location,cookie,UA)
    print(response)
    print(response.text)
    cookielist={
        'CASTGC':'CASTGC='+CASTGC[0],
        'route':route,
        'JSESSIONID':JSESSIONID,
        'iPlanetDirectoryPro':'iPlanetDirectoryPro='+iPlanetDirectoryPro[0]

        }
    return cookielist,response,Location

def GetydxgCookie(cookielist):
    UA="Mozilla/5.0 (Linux; Android 10; ELE-AL00 Build/HUAWEIELE-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045713 Mobile Safari/537.36 MMWEBID/8101 MicroMessenger/8.0.10.1960(0x28000A3D) Process/tools WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"
    cookie=cookielist['CASTGC']+';'+cookielist['route']+';'+cookielist['iPlanetDirectoryPro']

    #第一次访问
    response=GetRedirects("http://authserver2.htu.edu.cn/authserver/login?service=http://ydxg.htu.edu.cn/land/caslogin?ref=/quickgo/x8k58999",cookie,UA)
    Location=response.headers['Location'] #http://ydxg.htu.edu.cn/land/caslogin?ref=/quickgo/x8k58999&ticket=ST-280150-fPL4zBh9BPi9CmhxMXVw1629889259247-3jgP-cas

    #第二次访问
    response=GetRedirects(Location,cookie,UA)
    Location=response.headers['Location']#ydxg.htu.edu.cn/land/caslogin?ref=/quickgo/x8k58999
    #同时返回了PHPSESSID
    cookiestr=response.headers['SET-COOKIE']
    PHPSESSID=re.findall('PHPSESSID=(.*?);',cookiestr,re.S)
    cookie+=';PHPSESSID='+PHPSESSID[0]
    
    #第三次访问
    response=GetRedirects(Location,cookie,UA)
    Location=response.headers['Location']#'ydxg.htu.edu.cn'/quickgo/x8k58999
    
    #第四次访问
    ydxg= "http://ydxg.htu.edu.cn"+Location
    response=GetRedirects(ydxg,cookie,UA)
    Location=response.headers['Location']#http://htu.banjimofang.com/student/loginbyno/1493/1828324038?secode=x8k58999&sign=1629889276-38714-0-0b42a0dc2be90a679d2bfa0ca55c30fb

    #第五次访问
    cookie=cookielist['CASTGC']
    response=GetRedirects(Location,cookie,UA)

    #cookie处理
    cookiestr=response.headers['Set-Cookie']
    yxktmf=re.findall('yxktmf=.*?;',cookiestr,re.S)
    remember_student=re.findall('remember_student_.*?;',cookiestr,re.S)
    return yxktmf[0],remember_student[0]

def Login(USERNAME,PASSWORD):
    cookielist,response,Location=LoginHTU(USERNAME,PASSWORD)
    yxktmf,remember_student=GetydxgCookie(cookielist)
    return yxktmf

if __name__ == '__main__':
    Login(USERNAME,PASSWORD)
    

