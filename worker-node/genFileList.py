import os,sys

fw = open('file-list.txt','w')

ignore = {'genFileList.py':1,'genNet.py':1}

for parent,dirnames,filenames in os.walk('.'):
    for filename in filenames:
        if ignore.has_key(filename):
            continue
        
        data = parent[1:] + '/' + filename + '\n';
        data = data.replace('\\','/');
        
        fw.write(data);

fw.close()
