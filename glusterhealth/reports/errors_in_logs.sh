. $(dirname $(readlink -e $0))/utils.sh

out=$(grep " E " /var/log/glusterfs/glusterd.log | grep -v grep | wc -l)

if [ $out -gt 0 ]; then
    WARNING Errors in Glusterd log file num_errors=$out
fi

out=$(grep " W " /var/log/glusterfs/glusterd.log | grep -v grep | wc -l)

if [ $out -gt 0 ]; then
    WARNING Warnings in Glusterd log file num_warnings=$out
fi
