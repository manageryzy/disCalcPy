import os,sys,time,random
import httplib, urllib
import shutil

server_url = '121.251.255.51:80'
file_path = '/worker-node'


def downloadToFile(remote_path,path):

    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        conn = httplib.HTTPConnection(server_url)
        conn.request("GET", remote_path)
        r = conn.getresponse()
        if(r.status!=200):
            print r.__dict__
            return False
        data = r.read()
        conn.close()
    except:
        print 'Error in get data from server for ' + path
        return False;

    try:
        fw = open(path,'wb')
        fw.write(data)
        fw.close()
    except:
        print 'Error in writting ' + path + ' to disk'
        return False;
    
    return True


def getFileList():
    try:
        conn = httplib.HTTPConnection(server_url)
        conn.request("GET", file_path + '/file-list.txt')
        r = conn.getresponse()
        if(r.status!=200):
            print r.__dict__
            return False
        data = r.read()
        conn.close()
    except:
        print 'Error in get data from server for ' + path
        return False;

    remove_list = lambda x: x != '/file-list.txt' 
    
    data = data.replace("\r",'');
    print data
    data = data.replace('\\','/');
    return filter(remove_list , data.split('\n'));
    
def update():
    try:
        shutil.rmtree('./worker')
    except:
        print('del cache client error')
        
    l = getFileList()  

    for path in l:
        if(path == ''):
            continue
        if(downloadToFile(file_path + path,'./worker' + path) == False):
            print 'error in downloading ' + file_path + path
            return False

    return True

command = ''
lastcommand = 0

def UpdateCommand():
    return True

while 1:
    sleeptime = random.randint(10,600)
    print sleeptime
    time.sleep(sleeptime)
    print 'downloading'
    if(update()):
        break

print 'run'
os.chdir('./worker')
os.system('python monitor.py')
