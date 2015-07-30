# disCalcPy #
为了神经网络数值试验用python和nodejs以及php编写的一个分布式计算框架

[English Readme](readme.md)

## 要求

* Python 2.7 (只测试了在2.7下能运行)
* numpy
* scikit-learn(在默认的网络下不需要)
* scipy
* nodejs 或 iojs
* Web服务器（阿帕奇httpd或者nginx）

##概要说明

### 控制节点

控制节点是整个网络的核心，一个网络有且只有一个控制节点，是一个用NodeJS写的程序。控制节点负责读取配置文件、生成测试任务，分配节点类型，分配测试任务以及储存计算结果。工作节点将会通过转发节点把任务打包返回控制节点。控制节点也可以主动控制转发节点

### 更新服务器

用来更新整个网络的程序。在这里我们假设每台用于计算或者用于转发的电脑都没有储存能力，每次开机系统将会还原并且执行自动更新程序。这里将会自动的分发被工作节点或者转发节点执行的程序。具体的节点程序的分发方法在下面介绍。

这里其实用NodeJS效果可能更好的，但是我的服务器80口已经被httpd使用了，那么就直接用好了

### 转发节点

下载更新的时候会获得一个下载器，下载器被启动之后连接控制节点，控制节点确定他的类型是转发节点之后下载工作节点的文件压缩包并且解包备用。

转发节点的作用如下：

* 轮询发送心跳包告知控制节点自己存在
* 处理连接在转发节点的来自计算节点的心跳包
* 响应控制节点的请求（返回统计信息）
* 接受来自计算节点的轮询来实现全网络执行命令（控制节点发送执行命令的请求，转发节点在计算节点轮询的时候把来自控制节点的推送送出）
* 接受控制节点的返回结果
* 打包压缩结果并且上传控制节点

### 工作节点

工作节点的机器在更新服务器下只会获得一个下载器，这个下载器被启动之后会连接控制节点，控制节点会给它分配一个转发节点。接收到转发节点之后，下载器连接转发节点开始下载客户端。客户端下载完成之后根据CPU的线程数量开启python计算任务进程。这些计算的进程会连接转发节点来请求工作


## 包格式

网络连接全部采用HTTP连接。标示身份的参数在cookie域，而请求的参数在url里面

## Licence

The MIT License (MIT)

Copyright © 2015 <manageryzy>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## 作者

manageryzy@gmail.com