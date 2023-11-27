#!/bin/sh

# echo "Starting script 1"
python3 broker.py &

# echo "Starting script 2"
python3 server.py &

# echo "Starting script 2"
python3 client.py &


# Keep the script running to keep the container alive
tail -f /dev/null
