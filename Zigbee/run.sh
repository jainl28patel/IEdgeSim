#!/bin/bash

echo "Starting script 1"
python3 zigbee_server.py &

echo "Starting script 2"
python3 zigbee_client.py &

# Keep the script running to keep the container alive
tail -f /dev/null
