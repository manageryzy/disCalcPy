import os,sys
import cPickle as pickle

sys.path.append('../worker-node/require/mnist/src')

import mnist_loader
import network2

'''
os.chdir('../worker-node/require/mnist/src')
training_data, validation_data, test_data = mnist_loader.load_data_wrapper()
os.chdir('../../../../center-node')
'''

if(len(sys.argv) != 3):
    print 'usage : python csv.py PATH_OF_DATA OUT_PUT_FILE'
    exit(0)

fw = open(sys.argv[2]+'-training_cost.csv','w')
fw.write('')
fw.close()

fw = open(sys.argv[2]+'-training_accuracy.csv','w')
fw.write('')
fw.close()

fw = open(sys.argv[2]+'-evaluation_cost.csv','w')
fw.write('')
fw.close()

fw = open(sys.argv[2]+'-evaluation_accuracy.csv','w')
fw.write('')
fw.close()

fw = open(sys.argv[2]+'-parmeter.csv','w')
fw.write('filename , eta , lambda , SmFun ,SmPa ,RegType,WEParaQ \n')
fw.close()

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
        net = pickle.loads(obj)

        fw = open(sys.argv[2]+'-training_cost.csv','a+')
        fw.write('"' + filename + '",' + str(net.training_cost)[1:-1] +'\n')
        fw.close()

        fw = open(sys.argv[2]+'-training_accuracy.csv','a+')
        fw.write('"' + filename + '",' + str(net.training_accuracy)[1:-1] +'\n')
        fw.close()

        fw = open(sys.argv[2]+'-evaluation_cost.csv','a+')
        fw.write('"' + filename + '",' + str(net.evaluation_cost)[1:-1] +'\n')
        fw.close()

        fw = open(sys.argv[2]+'-evaluation_accuracy.csv','a+')
        fw.write('"' + filename + '",' + str(net.evaluation_accuracy)[1:-1] +'\n')
        fw.close()
        
        fw = open(sys.argv[2]+'-parmeter.csv','a+')
        fw.write('"' + filename + '",' + str(net.eta) + ',' + str(net.lmbda) + \
                 ',' + str(net.SmFun) + ',' + str(net.SmPa)  + ','
                 + str(net.regType) + ',' + str(net.WEParaQ) + '\n')
        fw.close()
