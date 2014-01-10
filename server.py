# -*- coding: utf-8 -*-
import web
import thread
import subprocess
import random
import string

#utf8处理
import sys 
default_encoding = 'utf-8' 
if sys.getdefaultencoding() != default_encoding: 
    reload(sys) 
    sys.setdefaultencoding(default_encoding) 

#禁用debug模式
web.config.debug = False

#webpy配置初始化
urls = (
    "/(.*)/", "redirect",
    "/", "index",
    "/sendmsg", "sendmsg",
    "/msg","msgjson",
    "/loginyeah","userverify",
    "/login","login"
)
render = web.template.render('templates')
app = web.application(urls, globals())
web.config.session_parameters['timeout'] = 60*20
web.config.session_parameters['ignore_expiry'] = False
web.config.session_parameters['secret_key'] = 'feWh4yv1We22QWQ'
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'uid': '0'})

#消息循环队列初始化
cache_msg=["","","","","","","","","",""]
cache_msg_num=0

#配置初始化
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
configxml = ET.ElementTree(file='rmcsconfig.xml')
mcargs = configxml.find("mcargs").text
javaexe = configxml.find("javaexe").text

#启动进程
p = subprocess.Popen(mcargs, executable=javaexe, universal_newlines=True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)

class redirect:
    def GET(self, path):
        web.seeother("/" + path)

class index:
    def GET(self):
        if not pverify():
            web.seeother("/login")
            return "请先登录"
        else:
            return render.index(outstring())

class login:
    def GET(self):
        try:
            derr = web.input().err
        except AttributeError:
            return render.login("style=\"display:none\"")
        if derr != "1":
            return render.login("style=\"display:none\"")
        return render.login("")

class userverify:
    def POST(self):
        if configxml.find("username").text == web.input().username and configxml.find("password").text == web.input().password:
            rstr=random_str()
            session.uid=rstr
            web.setcookie('uid', rstr, 20*60)
            web.seeother("/")
        else:
            web.seeother("/login?err=1")


class msgjson:
    def GET(self):
        if not pverify():
            return ""
        return outstring()

class sendmsg:
    def GET(self):
        global p,cache_msg,cache_msg_num
        if not pverify():
            return ""
        try:
            cmd=web.input().cmd
        except AttributeError:
            return ""
        if cmd=="p-frestart":
            p.kill()
            p = subprocess.Popen(mcargs, executable=javaexe, universal_newlines=True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
        if cmd=="p-restart":
            p.stdin.write('stop\n')
            p.stdin.flush()
            while True:
                p.poll()
                if p.returncode==0:
                    break
            p = subprocess.Popen(mcargs, executable=javaexe, universal_newlines=True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
        else:
            p.stdin.write(cmd.decode('utf-8').encode('gb2312')+'\n')
            p.stdin.flush()
        cache_msg[cache_msg_num]=u"发送命令:"+cmd
        cache_msg_num+=1
        if cache_msg_num>9:
            cache_msg_num=0
        print u"发送命令:"+cmd+"<br />"
        return cmd

def printerr():
    global p,cache_msg,cache_msg_num
    while True:
        line=p.stderr.readline().decode('gb2312').encode('utf-8')
        if line != "":
            cache_msg[cache_msg_num]=line
            cache_msg_num+=1
            if cache_msg_num>9:
                cache_msg_num=0
            sys.stdout.write(line.decode('utf-8').encode('gb2312')) 
    return 0

def printout():
    global p,cache_msg,cache_msg_num
    while True:
        line=p.stdout.readline().decode('gb2312').encode('utf-8')
        if line != "":
            cache_msg[cache_msg_num]=line
            cache_msg_num+=1
            if cache_msg_num>9:
                cache_msg_num=0
            sys.stdout.write(line.decode('utf-8').encode('gb2312'))
    return 0

def outstring():
    global cache_msg,cache_msg_num
    tpnum=cache_msg_num
    joinstr=""
    while True:
        joinstr+=cache_msg[tpnum]
        tpnum+=1
        if tpnum>9:
            tpnum=0
        if tpnum==cache_msg_num:
            break
        else:
            joinstr+="<br />"
    return joinstr

def random_str(randomlength=15):
    a = list(string.ascii_letters)
    random.shuffle(a)
    return ''.join(a[:randomlength])

def pverify():
    try:
        if web.cookies().uid != session.uid:
            return False
    except AttributeError:
        return False
    return True

if __name__ == "__main__":
    thread.start_new_thread(printerr,())
    thread.start_new_thread(printout,())
    app.run()