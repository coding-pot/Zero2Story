#!/bin/bash

PID=./gradio.pid
if [[ -f "$PID" ]]; then
    kill -9 `cat $PID`
fi

mkdir -p ./log
rm -rf ./log/gradio.log

nohup python app.py 1>./log/gradio.log 2>&1 &
echo $! > $PID
