COLOR=1

function use_color
{
    COLOR=1
}

function no_color
{
    COLOR=0
}

RED="\033[31m"
GREEN="\033[32m"
ORANGE="\033[33m"
NOCOLOR="\033[0m"

function LOGINFO
{
    echo "["$(date +"%Y-%m-%d %H:%M:%S")".0] I [bash:0:bash] <top>: "$@ >> $GLUSTER_HEALTH_REPORT_LOG_FILE
}

function LOGERROR
{
    echo "["$(date +"%Y-%m-%d %H:%M:%S")".0] E [bash:0:bash] <top>: "$@ >> $GLUSTER_HEALTH_REPORT_LOG_FILE
}

function LOGWARNING
{
    echo "["$(date +"%Y-%m-%d %H:%M:%S")".0] W [bash:0:bash] <top>: "$@ >> $GLUSTER_HEALTH_REPORT_LOG_FILE
}

function LOGDEBUG
{
    echo "["$(date +"%Y-%m-%d %H:%M:%S")".0] D [bash:0:bash] <top>: "$@ >> $GLUSTER_HEALTH_REPORT_LOG_FILE
}

function OK
{
    if [ $COLOR -eq 1 ]; then
        echo -e "${GREEN}[     OK]${NOCOLOR}" $@;
    else
        echo "[     OK]" $@;
    fi
}

function NOTOK
{
    if [ $COLOR -eq 1 ]; then
        echo -e "${RED}[ NOT OK]${NOCOLOR}" $@;
    else
        echo "[ NOT OK]" $@;
    fi
}

function WARNING
{
    if [ $COLOR -eq 1 ]; then
        echo -e "${ORANGE}[WARNING]${NOCOLOR}" $@;
    else
        echo "[WARNING]" $@;
    fi
}

function ERROR
{
    if [ $COLOR -eq 1 ]; then
        echo -e "${RED}[  ERROR]${NOCOLOR}" $@;
    else
        echo "[  ERROR]" $@;
    fi
}
