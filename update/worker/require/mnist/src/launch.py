import mnist_loader
import copy
import threading
import time
training_data, validation_data, test_data = mnist_loader.load_data_wrapper()

import network2

#weigit decay penalty term for cross enrtropy cost
WDCENet = network2.Network([784, 300, 10], cost=network2.CrossEntropyCost,regType='WD')
WDCENet.large_weight_initializer()
#weigit elimination penalty term for cross enrtropy cost
WECENet = copy.copy(WDCENet)
WECENet.regType = 'WE'
WECENet.WEParaQ = 0.5

SGLCENet = copy.copy(WDCENet)
SGLCENet.regType = 'SGL'
SGLCENet.SmFun = 'Quadratic'
SGLCENet.SmPa = 0.5

maxIter = 80

class MyThread(threading.Thread):
    def run(self):
        id = self.id
        if(id==1):
            evaluation_cost, evaluation_accuracy, \
            training_cost, training_accuracy = \
            WDCENet.SGD(training_data, maxIter, 50, 0.5,
                    lmbda = 5.0,
                    evaluation_data=test_data,
                    monitor_evaluation_cost=True,
                    monitor_evaluation_accuracy=True,
                    monitor_training_cost=True,
                    monitor_training_accuracy=True)
            WDCENet.evaluation_cost = evaluation_cost
            WDCENet.evaluation_accuracy = evaluation_accuracy
            WDCENet.training_cost = training_cost
            WDCENet.training_accuracy = training_accuracy

            file_object = open('OUTWD.txt','w+')
            file_object.write('WD.evaluation_cost=')
            print >>file_object,evaluation_cost
            file_object.write('WD.evaluation_accuracy=')
            print >>file_object,evaluation_accuracy
            file_object.write('WD.training_cost=')
            print >>file_object,training_cost
            file_object.write('WD.training_accuracy=')
            print >>file_object,training_accuracy
            file_object.close()

        if(id==2):
            evaluation_cost, evaluation_accuracy, \
            training_cost, training_accuracy = \
            WECENet.SGD(training_data, maxIter, 50, 0.5,
                    lmbda = 5.0,
                    evaluation_data=test_data,
                    monitor_evaluation_cost=True,
                    monitor_evaluation_accuracy=True,
                    monitor_training_cost=True,
                    monitor_training_accuracy=True)
            WECENet.evaluation_cost = evaluation_cost
            WECENet.evaluation_accuracy = evaluation_accuracy
            WECENet.training_cost = training_cost
            WECENet.training_accuracy = training_accuracy

            file_object = open('OUTWE.txt','w+')
            file_object.write('WE.evaluation_cost=')
            print >>file_object,evaluation_cost
            file_object.write('WE.evaluation_accuracy=')
            print >>file_object,evaluation_accuracy
            file_object.write('WE.training_cost=')
            print >>file_object,training_cost
            file_object.write('WE.training_accuracy=')
            print >>file_object,training_accuracy
            file_object.close()

        if(id==3):
            evaluation_cost, evaluation_accuracy, \
            training_cost, training_accuracy = \
            SGLCENet.SGD(training_data, maxIter, 50, 0.5,
                    lmbda = 5.0,
                    evaluation_data=test_data,
                    monitor_evaluation_cost=True,
                    monitor_evaluation_accuracy=True,
                    monitor_training_cost=True,
                    monitor_training_accuracy=True)
            SGLCENet.evaluation_cost = evaluation_cost
            SGLCENet.evaluation_accuracy = evaluation_accuracy
            SGLCENet.training_cost = training_cost
            SGLCENet.training_accuracy = training_accuracy

            file_object = open('OUTSGL.txt','w+')
            file_object.write('SGL.evaluation_cost=')
            print >>file_object,evaluation_cost
            file_object.write('SGL.evaluation_accuracy=')
            print >>file_object,evaluation_accuracy
            file_object.write('SGL.training_cost=')
            print >>file_object,training_cost
            file_object.write('SGL.training_accuracy=')
            print >>file_object,training_accuracy
            file_object.close()

threads = []
for i in range(3):
    t = MyThread()
    t.id=i+1
    t.start()
    threads.append(t)
print 'main thread is waitting for exit...'
for t in threads:
    t.join()

print 'main thread finished!'

