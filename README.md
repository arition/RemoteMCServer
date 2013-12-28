RemoteMCServer
==============
Lanuch a Minecraft Server with a remote console access<br />
Important:The user_control module is undone now, so you should not use it in public network!<br />
Only tested in windows<br />

Usage
--------------
You need python 2.7 to run it<br />
1.Copy files to the folder where you place the mcserver<br />
2.Edit mcargs,javaexe in server.py<br />
3.Run server.py<br />
4.open 127.0.0.1:8080 in your browser and enjoy it!(other computers need to access it with 192.168.X.X:8080)<br />

RemoteMCServer
==============
一个Minecraft远程控制服务端<br />
注意：由于目前用户权限控制模块还没有写完，为了安全请仅在局域网中运行<br />
目前只在windows环境下测试过，预计将来会支持linux<br />

使用
--------------
下载并安装python 2.7<br />
1.复制到你的MC服务器所在文件夹<br />
2.编辑server.py中的 mcargs,javaexe 两个变量<br />
3.运行 server.py<br />
4.在浏览器中输入127.0.0.1:8080即可访问（其他电脑需要你的IP地址来访问，像192.168.X.X:8080这样）<br />