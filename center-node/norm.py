import os,sys
import cPickle as pickle
import numpy as np

sys.path.append('../worker-node/require/mnist/src')

import network2

if(len(sys.argv) != 3):
    print 'usage : python csv.py PATH_OF_DATA OUT_PUT_FILE'
    exit(0)

count = 0

for parent,dirnames,filenames in os.walk(sys.argv[1]):
    for filename in filenames:
        name = filename.split('.')
        if(len(name) < 2):
            continue

        if(name[-1]!='res'):
            continue

        #is the .res file
        print filename
        fr = open(parent+'/'+filename,'r')
        obj = fr.read()
        fr.close()
        try:
            net = pickle.loads(obj)

            for l in xrange(len(net.weights)):
                fw = open(sys.argv[2]+'-'+str(l)+'-norm.csv','a+')
                fw.write('"'+filename+'",')
                for r in xrange(len(net.weights[l])):
                    norm = np.linalg.norm(net.weights[l][r]);
                    if(norm < 0.1):
                        count += 1
                    fw.write(str(norm)+',')
                fw.write('\n')        
                fw.close()
        except:
            print 'err'
print count
            
