#!/bin/bash

PID=./gradio.pid
if [[ -f "$PID" ]]; then
    kill -9 `cat $PID`
fi

mkdir -p ./logs
rm -rf ./logs/app.log

nohup python -u app.py > ./logs/app.log 2>&1 &
echo $! > $PID
