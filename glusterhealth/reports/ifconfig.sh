. $(dirname $(readlink -e $0))/utils.sh

IFCONFIG_CMD=/sbin/ifconfig

all_ok=1
# Get the interface details
for interface in $(ifconfig | grep -v ^\ | grep ':' | cut -f 1 -d':'); do
    LOGINFO $($IFCONFIG_CMD $interface)

    # NOTE: The below assumes output on Fedora 25/26. Need to validate the
    # output from other distro's ifconfig tool
    rx_err=$($IFCONFIG_CMD $interface | grep 'RX error')
    tx_err=$($IFCONFIG_CMD $interface | grep 'TX error')

    echo $rx_err | grep -v -q -e '[1-9]'
    RET=$?
    if [ $RET != 0 ] ; then
       NOTOK Receive errors in \"ifconfig $interface\" output
       LOGWARNING RX Errors seen, try 'ethtool': $rx_err
       LOGINFO $(ethtool -S $interface);
       all_ok=0
    fi

    echo $tx_err | grep -v -q -e '[1-9]'
    RET=$?
    if [ $RET != 0 ] ; then
       NOTOK Transmission errors in \"ifconfig $interface\" output
       LOGWARNING TX Errors seen, try 'ethtool': $tx_err
       LOGINFO $(ethtool -S $interface);
       all_ok=0
    fi

done

if [ $all_ok == 1 ] ; then
    OK No errors seen at network card
fi
