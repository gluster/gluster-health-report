#!/bin/bash

good=80

pid=`gluster v status test | awk '/Self-heal/ {print $NF}'`
value=`ps -p $pid -o %cpu | grep -v CPU` | cut -d'.' -f1 
echo $value

if (( $(echo "$value $good" | awk '{print ($1 > $2)}') ))
then 
    echo "High CPU usage by Self-heal $value"
fi





