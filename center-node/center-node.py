# -*- coding: utf-8 -*-
'''
This file is a part of disCalcPy .
homepage -> https://github.com/manageryzy/disCalcPy

MIT licenced!!!
'''

import socket
import json
import sys,os
import time
import threading
import traceback
import cPickle as pickle  

debug = 1

socket.setdefaulttimeout(20)

WorkerNodes = {}

# maybe it is a stack rather than a queue, do not mind the name
WorkQueue = []
WorkingQueue = []
WorkFinishedQueue = []

class Conf:
    @staticmethod
    def loadConf(path):
        f = open(path)
        j = json.load(f)
        f.close()
        conf = Conf()
        conf.iter = j['iter']
        conf.eta = j['eta']
        conf.regType = j['regType']
        conf.WEParaQ = j['WEParaQ']
        conf.SmFun = j['SmFun']
        conf.SmPa = j['SmPa']
        conf.lmbda = j['lambda']

        conf.port = j['port']
        conf.timeout = j['timeout']
        return conf

class Work:
    @staticmethod
    def loadWorks():
        for eta in Config.eta:
            for WEParaQ in Config.WEParaQ:
                for SmPa in Config.SmPa:
                    for lmbda in Config.lmbda:
                        work = Work()
                        work.eta = eta
                        work.WEParaQ = WEParaQ
                        work.SmPa = SmPa
                        work.lmbda = lmbda
                        work.iter = Config.iter
                        work.regType = Config.regType
                        work.SmFun = Config.SmFun
                        WorkQueue.append(work)
        return

class WatchThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print 'monitor thread run!'
        while 1:
            if(len(WorkQueue)==0):
                if(len(WorkingQueue)==0):
                    break
            time.sleep(60)
            print len(WorkQueue),' works left'
            print len(WorkingQueue),' works calculating'
            print len(WorkFinishedQueue),' works finished'
            print len(WorkerNodes),' nodes'

class SocketThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def setClientSocket(self,clientSocket,clinetAddr):
        self.clientsock = clientSocket
        self.clientaddr = clinetAddr
    def run(self):
        try:
            clientsock = self.clientsock
            clientaddr = self.clientaddr
            clientfile=clientsock.makefile('rw',0)

            cleanWorker()

            if(debug):
                print 'client ',clientaddr,' connect'
            
            line=clientfile.readline().strip()
            if line=='worker ping':
                uuid=clientfile.readline().strip()
                if(debug):
                    print uuid
                clientfile.write('server ping\n')
                if(WorkerNodes.get(uuid) == None):
                    if(debug):
                        print 'worker ',uuid ,' at ',clientaddr,' connected'
                    
                    line = clientfile.readline().strip()
                    if line=='ok':
                        if(len(WorkQueue)==0):
                            clientfile.write('null\n')
                            line = clientfile.readline().strip()
                            if (line!='ok'):
                                print 'petrol error! connection to ',clientaddr,' closed!!!'
                        else:
                            work = WorkQueue.pop()
                            work.node = uuid
                            
                            obj = pickle.dumps(work)
                            clientfile.write(str(len(obj))+'\n')
                            clientfile.write(obj)

                            line = clientfile.readline().strip()
                            if(line == 'busy'):
                                WorkQueue.append(work)
                                print '[Error]: client is busy!'
                                return

                            WorkerNodes[uuid] = {}
                            WorkerNodes[uuid]['last_active'] = time.time()
                            WorkingQueue.append(work)

                            
                            if (line!='ok'):
                                print 'petrol error! connection to ',clientaddr,' closed!!!'
                else:
                    WorkerNodes[uuid]['last_active'] = time.time()
                    line = clientfile.readline().strip()
                    clientfile.write('null\n')
                    line = clientfile.readline().strip()
            else:
                if(line=='worker finish'):
                    clientfile.write('server ping\n')
                    uuid = clientfile.readline().strip()
                    size = int(clientfile.readline().strip())
                    res = clientfile.read(size)

                    if(WorkerNodes.get(uuid) == None):
                        print 'result from unknown node ',uuid,' ignore!'

                    else:
                        del WorkerNodes[uuid]
                        for w in xrange(len(WorkingQueue)):
                            if(WorkingQueue[w].node == uuid):
                                WorkFinishedQueue.append(WorkingQueue[w])
                                del WorkingQueue[w]
                                break
                        print 'worker node:',uuid,' fiished task!Res saved to ',fileName
                    fileName = './res/' + str(time.time()) + '.res'
                    f = file(fileName,'w')
                    f.write(res)
                    f.close()
                    clientfile.write('ok\n')


                else:  
                    print 'petrol error! connection to ',clientaddr,' closed!!!'

            clientfile.close()
            clientsock.close()
        except socket.error, msg:
            print '[ERROR] error in change data with client'
            print msg
            print traceback.format_exc()
        finally:
            try:
                clientfile.close()
            except :
                print '[ERROR] error in change data with client!!!'
            try:
                clientsock.close()
            except :
                print '[ERROR] error in change data with client!!!'

        if(debug):
            print 'connection to ',clientaddr,' closed'

#clean the worker nodes do not send heart beat ping package
def cleanWorker():
    t = time.time()
    dellist = []
    for w in WorkerNodes:
        if(t - WorkerNodes[w]['last_active'] > Config.timeout):
            for work in xrange(len(WorkingQueue)):
                if(WorkingQueue[work].node == w):
                    WorkQueue.append(WorkingQueue[work])
                    del WorkingQueue[work]
                    break
            dellist.append(w)
    for w in dellist:
        print w
        del WorkerNodes[w]

for parent,dirnames,filenames in os.walk('./conf'):
    for filename in filenames:
        path = parent+'/'+filename;
        path = path.replace('\\','/');
        Config = Conf.loadConf(path)
        print 'config json have been loaded'

        Work.loadWorks()
        print len(WorkQueue),' work(s) loaded!'

watchThread = WatchThread()
watchThread.start()


try:
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind(('',Config.port))
    s.listen(10)
except socket.error, msg:
    sys.stderr.write("[ERROR] %s\n" )
    print msg
    sys.exit(2)

while 1:
    try:
        if(len(WorkQueue)==0):
            if(len(WorkingQueue)==0):
                break

        clientsock,clientaddr=s.accept()
        socketThread = SocketThread()
        socketThread.setClientSocket(clientsock,clientaddr)
        socketThread.start()
            
        
    except socket.error, msg:
        print '[ERROR] error in change data with client'
        print msg
        print traceback.format_exc()
    finally:
        try:
            clientfile.close()
        except :
            print '[ERROR] error in change data with client!!!'
        try:
            clientsock.close()
        except :
            print '[ERROR] error in change data with client!!!'

print 'all works done'
