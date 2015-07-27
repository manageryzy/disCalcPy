import sys
sys.path.append('./require/mnist/src')
import network2

net = network2.Network([784, 1024, 10], cost=network2.CrossEntropyCost,regType='WD')
net.save('init.net')
