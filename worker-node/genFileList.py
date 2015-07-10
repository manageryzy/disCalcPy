import os,sys

fw = open('file-list.txt','w')

for parent,dirnames,filenames in os.walk('.'):
    for filename in filenames:
        fw.write(parent[1:] + '/' + filename + '\n');

fw.close()
