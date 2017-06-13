#!/bin/bash 
#qsize=$1
iperf -c 10.0.0.1 -p 5001 -w 16m -t 3600 -i 1 > iperf.txt &
echo started iperf

