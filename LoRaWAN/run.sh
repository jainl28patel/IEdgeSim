#!/bin/sh

# echo "Starting script 1"
python3 ser.py &

# echo "Starting script 2"
python3 cl.py &

# Keep the script running to keep the container alive
tail -f /dev/null
