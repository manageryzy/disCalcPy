'''

this program just a background program to communicate with the server

'''

import os

#stop the auto shutdown task
os.startfile('shut.bat')

# start four workers for four kernel
os.startfile('worker.py')
os.startfile('worker.py')
os.startfile('worker.py')
os.startfile('worker.py')
