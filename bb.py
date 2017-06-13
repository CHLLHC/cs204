#!/usr/bin/python

"Based on CS144 In-class exercise: Buffer Bloat"
"by CHL"

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.link import TCLink

from subprocess import Popen

import time,os
import itertools

class StarTopo(Topo):
    "Star topology for Buffer Bloat experiment"

    def __init__(self, n, cbw, clat, clos, cq, sbw, slat, slos, sq):
        # Add default members to class.
        super(StarTopo, self ).__init__()

	# Create the server
        self.addHost( 'server' )
        
        # Create switch and host nodes
        for i in xrange(n):
            self.addHost( 'h%d' % (i+1) )
            
        self.addSwitch('s0', fail_mode='open')
		
        self.addLink('server', 's0', bw=sbw, delay=slat, loss=slos,
                          max_queue_size=sq, use_htb=True )

        for i in xrange(n):
            self.addLink('h%d' % (i+1), 's0', bw=cbw, delay=clat, loss=clos,
                          max_queue_size=cq, use_htb=True)

def bbnet():
    cong = ['vegas','reno','cubic','bbr']
    nflow = [1,10,100]
    rmenmax = [67108864,16777216,524288,262144]
    clq = [1,10,100,1000] #client link queue
    seq = [1,10,100,1000] #server link queue
    aqm = [False, True]
    clb = [1,10] # client bandwidth
    duration = 5
    graceful = 1
    n=100
    for cc, nf, rmm, cl, se, aq, cb in itertools.product(cong,nflow,rmenmax,clq,seq,aqm,clb):    
        "Create network and run Buffer Bloat experiment"
        testname='%s_%d_%d_%d_%d_%d' % (cc,nf,rmm,cl,se,cb)
        if aq:
            testname = testname+'_aqm'
        else:
            testname = testname+'_noaqm'
        print "starting mininet for %s...." % testname
        # setup sys env
        Popen("mn -c", shell=True).wait()
        Popen("sysctl -w net.ipv4.tcp_congestion_control=%s"%cc, shell=True).wait()
        Popen("sysctl -w net.core.rmem_max=%d"%rmm, shell=True).wait()

        # Reset to known state
        topo = StarTopo(n=n, cbw=cb, clat='10ms', 
    		clos=0, cq=cl, sbw=1000,
    		slat='50ms', slos=0, sq=se)
        net = Mininet(topo=topo, link=TCLink, cleanup=True)
        net.start()
        #dumpNodeConnections(net.hosts)
        os.popen('mkdir -p ./results/%s' % testname)
        os.popen('date +%%s > ./results/%s/T0' % testname)
        #Start iperf server
        server = net.getNodeByName('server')
        server.cmd('iperf -s -w 16m -p 5001 -i 1 > ./results/%s/iperf-recv.txt &' % testname)
        serverip = server.IP()
        print serverip
        for i in xrange(nf):
            hostname = 'h%d' % (i+1)
            host = net.getNodeByName(hostname)
            host.cmd('iperf -c %s -p 5001 -w 16m -t %d  -i 1 > ./results/%s/%s_iperf.txt &' % (serverip,duration,testname,hostname))
            host.cmd('ping %s > ./results/%s/%s_ping.txt &' % (serverip,testname,hostname))
        #CLI( net )
        print 'All instructions issued.\n'
        time.sleep(duration+graceful)
        Popen("killall -9 ping", shell=True).wait()    
        Popen("killall -9 socat", shell=True).wait()    
        net.stop()


if __name__ == '__main__':
    os.popen('sysctl -w net.ipv4.tcp_no_metrics_save=1')
    bbnet()
