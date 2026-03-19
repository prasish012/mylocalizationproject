#!/bin/bash
pkill -f gunicorn
sleep 2
cd /root/mylocalizationproject
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:/root/mylocalizationproject
gunicorn --workers 3 --bind 127.0.0.1:8001 mylocalizationproject.wsgi:application --daemon
echo "Engine Restarted on Port 8001!"
