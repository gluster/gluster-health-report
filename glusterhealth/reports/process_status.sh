#!/bin/bash
. $(dirname $(readlink -e $0))/utils.sh

good=80

pid=`gluster v status| grep localhost|awk '/Self-heal/ {print $NF}'|uniq`
value=`ps -p $pid -o %cpu | grep -v CPU | cut -d'.' -f1` 

if [ "x$value" == "x" ] ; then
    exit 0;
fi

if (( $(echo "$value $good" | awk '{print ($1 > $2)}') ))
then 
    NOTOK "High CPU usage by Self-heal value=$value"
else
    OK "CPU usage by Self-heal value=$value"
fi
