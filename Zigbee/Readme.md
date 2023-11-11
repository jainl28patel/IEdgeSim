```ns zigbee.tcl``` > zigbee_nam.nam & zigbee_trace.tr
```./nam zigbee_nam.nam``` > simulate
```gawk -f statistics.awk zigbee_trace.tr``` > energyleft.txt pktrecvd.txt pktsent.txt
