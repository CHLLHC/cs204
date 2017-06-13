#!/usr/bin/python
'''
Monitor the traffic between s0 and server
'''

import time
import threading
import os
import re


class Poke(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        ifout = os.popen('ifconfig').read()
        parser = re.search(r's0-eth1.+\n.+\n.+RX packets:(\d+).+\n.+TX packets:(\d+).+\n+.+\n+.+RX bytes:(\d+).+TX bytes:(\d+)',ifout)
        if parser != None:
            with open('traffic.txt','a') as f:
                f.write(str(time.time())+','+parser.group(1)+','+parser.group(2)+','+parser.group(3)+','+parser.group(4)+'\n')
            print time.time(),parser.group(1),parser.group(2),parser.group(3),parser.group(4)
    
def Core():
    starttime=time.time()
    inter = 1
    while True:
        wk = Poke()
        wk.start()
        time.sleep(inter - ((time.time() - starttime) % inter))

if __name__ == '__main__':
    Core()









