```ns zigbee.tcl``` > zigbee_nam.nam & zigbee_trace.tr
```./nam zigbee_nam.nam``` > simulate
```gawk -f statistics.awk zigbee_trace.tr``` > energyleft.txt pktrecvd.txt pktsent.txt


requirements 

```
sudo apt-get update
sudo apt-get install ns2
sudo apt-get install nam
sudo apt-get install tcl```
