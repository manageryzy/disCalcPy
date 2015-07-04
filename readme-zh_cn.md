# disCalcPy #
为了神经网络数值试验用python编写的一个分布式计算框架

[English Readme](readme.md)

## 要求

* Python 2.7 (只测试了在2.7下能运行)
* numpy
* scikit-learn(在默认的网络下不需要)
* scipy


##安装

### 控制节点

控制节点是整个网络的核心，一个网络有且只有一个控制节点。控制节点负责读取配置文件、生成测试任务，分配测试任务以及储存计算结果。

center-node.py：控制节点的程序。别的配置就不说了，注意debug开关。把debug设置成False来关闭调试协议用的信息。

conf.json：

* port：控制节点监听端口
* timeout：心跳包超时。如果超过timeout秒没有收到心跳包，认为工作节点异常死亡
* iter：迭代次数
* eta：学习率η
* regType：正则化项类型。WD是weigit decay，WE是weigit elimination，SGL是光滑逼近
* WEParaQ：weigit elimination中的参数Q，如果不是weigit elimination会被无视
* SmFun：SGL的光滑函数类型。可以是Half、Quadratic、Quadratic、Sextic。如果不是SGL被无视
* SmPa：光滑函数阈值。如果不是SGL被无视
* lambda：正则化项系数λ

res：储存输出结果的文件夹。输出结果是序列化之后的对象。按照计算结束的时间戳命名

### 工作节点

工作节点负责从控制节点获得任务，计算之后返回结果到控制节点

worker.py：工作节点的主程序。同样的还是有debug开关

init.net：网络的初始权值，用来保证在相同初始权值下开始

conf.json：

* ip：控制节点的ip
* port：控制节点的端口

require：这个文件夹包含了需要的神经网络的实现。关于原始程序参考文件夹下面的markdown文档

## 包格式

*  握手/心跳包
	*  客户端发送worker ping
	*  客户端发送UUID
	*  服务端发送server ping
	*  客户端发送ok
	*  服务端发送工作任务对象信息长度或者发送null
	*  服务端发送任务信息或者进入下一步
	*  客户端发送ok
	*  连接结束
*  工作完成信息包
	*  客户端发送worker finish
	*  客户端发送UUID
	*  服务端发送server ping
	*  客户端发送长度
	*  客户端发送结果对象
	*  服务端发送ok
	*  连接结束



## Licence

The MIT License (MIT)

Copyright © 2015 <manageryzy>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## 作者

manageryzy@gmail.com