#!/bin/sh

# echo "Starting script 1"
python3 ser.py > log.txt &

# echo "Starting script 2"
python3 cl.py > log.txt &

# Keep the script running to keep the container alive
tail -f /dev/null
