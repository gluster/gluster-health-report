. $(dirname $(readlink -e $0))/utils.sh

NET_FILE="/proc/net/dev"

all_ok=1
# Get the interface details

for interface in $(cat $NET_FILE | grep ':'  | cut -f1 -d':'); do
    line=$(grep $interface $NET_FILE);
    only_errs=$(echo $line | awk '{ print $4 $5 $7 $12 $13 $15 $16 }');

    echo $only_errs | grep -v -q -e '[1-9]'
    RET=$?
    if [ $RET != 0 ] ; then
       NOTOK Errors seen in \"cat /proc/net/dev -- ${interface}\" output
       LOGWARNING N/W Errors seen, try 'ethtool': $line
       LOGINFO $(ethtool -S $interface);
       all_ok=0
    fi
done

if [ $all_ok == 1 ] ; then
    OK No errors seen at network card
fi
