# -*- coding: utf-8 -*-
import webpy/web
import os
import time
import thread
import subprocess

import sys 
default_encoding = 'utf-8' 
if sys.getdefaultencoding() != default_encoding: 
    reload(sys) 
    sys.setdefaultencoding(default_encoding) 

web.config.debug = False

urls = (
    "/(.*)/", "redirect",
    "/", "index",
    "/sendmsg", "sendmsg",
    "/msg","msgjson"
)
render = web.template.render('templates')

cache_msg=["","","","","","","","","",""]
cache_msg_num=0

lock = thread.allocate_lock()
mcargs=" -Xincgc -Xmx1G -jar craftbukkit-1.6.2-R1.0.jar -nojline"
javaexe="C:\\Program Files\\Java\\jre7\\bin\\java.exe"
#mcargs=""
#javaexe="test.exe"

p = subprocess.Popen(mcargs, executable=javaexe, universal_newlines=True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
class redirect:
    def GET(self, path):
        web.seeother("/" + path)

class index:
    global outstring,render
    def GET(self):
        return render.index(outstring())

class msgjson:
    global cache_msg,outstring
    def GET(self):
        global p,cache_msg
        return outstring()

class sendmsg:
    global p,cache_msg,cache_msg_num
    def GET(self):
        global p,cache_msg,cache_msg_num
        cmd=web.input().cmd
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
        #cache_msg+=cmd+"<br />"
        return cmd

def printerr():
    global p,cache_msg,cache_msg_num
    #lock.acquire()
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
    #lock.acquire()
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

if __name__ == "__main__":
    app = web.application(urls, globals())
    thread.start_new_thread(printerr,())
    thread.start_new_thread(printout,())
    app.run()
    