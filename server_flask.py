# -*- coding: utf-8 -*-
from flask import redirect,url_for,render_template,session
import os
import thread
import subprocess
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)
session.permanent = True
app.permanent_session_lifetime = timedelta(minutes=30)

#消息循环队列初始化
cache_msg=[""]*30
cache_msg_num=0

#配置初始化
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
configxml = ET.ElementTree(file='rmcsconfig.xml')
mcargs = configxml.find("mcargs").text
javaexe = configxml.find("javaexe").text
expires = configxml.find("expires").text

#启动进程
p = subprocess.Popen(mcargs, executable=javaexe, universal_newlines=True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)


@app.route('/')
def index():
    if verifyLogin():
        return render_template('index.html',name=outstring())
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if configxml.find("username").text == request.form["username"] and configxml.find("password").text == request.form["password"]:
            session["username"] = configxml.find("username").text
            return redirect(url_for('index'))
    if request.method == 'GET':
        derr = request.args.get("err","")
        if derr != "1":
            return render_template('login.html',name="style=\"display:none\"")
        return render_template('login.html')
    return render_template('login.html')

@app.route('/msg')
def msgjson():
    if verifyLogin():
        return outMsg()
    return ""

@app.route('/sendmsg')
def sendmsg():
    global p
    if verifyLogin():
        cmd = request.args.get('cmd', '')
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
            p.stdin.write(cmd+'\n')
            p.stdin.flush()
        return cmd
    return ""

def verifyLogin():
    return 'username' in session and session["username"] == configxml.find("username").text

def printerr():
    global p,cache_msg,cache_msg_num
    while True:
        line=p.stderr.readline()
        if line != "":
            cache_msg[cache_msg_num]=line
            cache_msg_num+=1
            if cache_msg_num>29:
                cache_msg_num=0
            sys.stdout.write(line) 
    return 0

def printout():
    global p,cache_msg,cache_msg_num
    while True:
        line=p.stdout.readline()
        if line != "":
            cache_msg[cache_msg_num]=line
            cache_msg_num+=1
            if cache_msg_num>29:
                cache_msg_num=0
            sys.stdout.write(line)
    return 0

def outstring():
    global cache_msg,cache_msg_num
    tpnum=cache_msg_num
    joinstr=""
    while True:
        joinstr+=cache_msg[tpnum]
        tpnum+=1
        if tpnum>29:
            tpnum=0
        if tpnum==cache_msg_num:
            break
        else:
            joinstr+="<br />"
    return joinstr

if __name__ == '__main__':
    thread.start_new_thread(printerr,())
    thread.start_new_thread(printout,())
    app.run()