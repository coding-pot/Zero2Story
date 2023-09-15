#!/bin/bash

PID=./gradio.pid
if [[ -f "$PID" ]]; then
    kill -15 `cat $PID` || kill -9 `cat $PID`
fi

mkdir -p ./logs
rm -rf ./logs/app.log

CONFIDENTIAL=./.palm_api_key.txt
if [[ ! -f "$CONFIDENTIAL" ]]; then
    echo "Error: PaLM API file not found. To continue, please create a .palm_api_key.txt file in the current directory."
    exit 1
fi

export PALM_API_KEY=`cat .palm_api_key.txt`
nohup python -u app.py > ./logs/app.log 2>&1 &
echo $! > $PID
