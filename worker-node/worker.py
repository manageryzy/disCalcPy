# -*- coding: utf-8 -*-
'''
This file is a part of disCalcPy .
homepage -> https://github.com/manageryzy/disCalcPy

MIT licenced!!!
'''

debug = 1

import socket
import json
import sys
import os
import time
import threading
import uuid
import cPickle as pickle

sys.path.append('./require/mnist/src')

socket.setdefaulttimeout(20)

import mnist_loader
import network2

os.chdir('./require/mnist/src')
training_data, validation_data, test_data = mnist_loader.load_data_wrapper()
os.chdir('../../..')

UUID = str(uuid.uuid1())
print 'uuid generated ',UUID

class Conf:
    @staticmethod
    def loadConf():
        f = open('conf.json')
        j = json.load(f)
        f.close()
        conf = Conf()

        conf.ip = j['ip']
        conf.port = j['port']
        return conf

Config = Conf.loadConf()

class Work:
    def __init__(self):
        self.eta = 0
        self.WEParaQ = 0
        self.SmPa = 0
        self.lmbda = 0
        self.iter = 0
        self.regType = ''
        self.SmFun = ''

class CalcThread(object):
    def __init__(self):
        self.calcFinish = False
        self.thread = threading.Thread(target=self.run)
    def refresh(self):
        self.calcFinish = False
        self.thread = threading.Thread(target=self.run)
    def run(self):
        print 'Worker thread run!'
        self.calcFinish = False
        
        self.net = network2.load('init.net')
        self.net.regType = Config.regType
        self.net.WEParaQ = Config.WEParaQ
        self.net.SmFun = Config.SmFun
        self.net.SmPa = Config.SmPa
        self.net.iter = Config.iter
        self.net.eta = Config.eta
        self.net.lmbda = Config.lmbda

        evaluation_cost, evaluation_accuracy, \
        training_cost, training_accuracy = \
        self.net.SGD(training_data, Config.iter, 50, Config.eta,
                lmbda = Config.lmbda,
                evaluation_data=test_data,
                monitor_evaluation_cost=True,
                monitor_evaluation_accuracy=True,
                monitor_training_cost=True,
                monitor_training_accuracy=True)
        self.net.evaluation_cost = evaluation_cost
        self.net.evaluation_accuracy = evaluation_accuracy
        self.net.training_cost = training_cost
        self.net.training_accuracy = training_accuracy
        self.calcFinish = True
        print 'Worker thread finish!'

calcThread = CalcThread()


while 1:
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((Config.ip,Config.port))
    except socket.error, msg:
        print 'error'
        print msg
        print 'retry in 60s'
        time.sleep(60)
        continue

    try:
        serverfile = s.makefile('rw',0)
        
        if(~calcThread.thread.is_alive() & calcThread.calcFinish):
            #send the finish package
            serverfile.write('worker finish\n')
            line = serverfile.readline().strip()
            if(debug):
                print line
            if(line != 'server ping'):
                print 'petrol error'
                continue
            serverfile.write(UUID + '\n')

            obj = pickle.dumps(calcThread.net)
            serverfile.write(str(len(obj))+'\n')
            serverfile.write(obj)
            
            line = serverfile.readline().strip()
            if(debug):
                print line
            if(line != 'ok'):
                print 'petrol error'
                continue

            calcThread.refresh()
        else:
            #heart beat ping and request for work
            serverfile.write('worker ping\n'+UUID+'\n')
            line = serverfile.readline().strip()
            if(debug):
                print line
            if(line != 'server ping'):
                print 'wrong server',line
                sys.exit(-1)
            serverfile.write('ok\n')
            line = serverfile.readline().strip()
            if(debug):
                print line
            if(line == 'null'):
                serverfile.write('ok\n')
            else:
                obj = serverfile.read(int(line))
                work = json.loads(obj)
                Config.eta = work['eta']
                Config.WEParaQ = work['WEParaQ']
                Config.SmPa = work['SmPa']
                Config.lmbda = work['lmbda']
                Config.iter = work['iter']
                Config.regType = work['regType']
                Config.SmFun = work['SmFun']

                if(calcThread.thread.is_alive()):
                    print 'error:the worker thread is busy!'
                    serverfile.write('busy\n')
                else:
                    calcThread.thread.start()
                serverfile.write('ok\n')

        serverfile.close()
        s.shutdown(socket.SHUT_RDWR)
        time.sleep(60)
    
    except socket.error, msg:
        print 'error'
        print msg
        print 'retry in 60s'
        time.sleep(60)
        continue
