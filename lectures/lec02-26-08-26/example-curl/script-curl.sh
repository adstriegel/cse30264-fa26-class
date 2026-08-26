#!/bin/bash

while true
do
    echo "Next loop iteration"
    curl http://ns-mn1.cse.nd.edu/iplog/index.html > /dev/null
    # Sleep for 30 seconds
    sleep 30
done
