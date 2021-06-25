#!/bin/bash
#set -e
LOGFILE=/var/www/data/irrigation/log/gunicorn.log
LOGDIR=$(dirname $LOGFILE)
PIDFILE=/var/www/data/irrigation/run/gunicorn.pid
TMPDIR=/var/www/data/irrigation/tmp/
NUM_WORKERS=1
# user/group to run as
USER=www-data
GROUP=www-data
BINDADDR=0.0.0.0:9000
cd /var/www/data/irrigation/irrigation/
test -d $LOGDIR || mkdir -p $LOGDIR
source /var/www/data/irrigation/envs/irrigation/bin/activate
exec gunicorn irrigation.wsgi:application -b $BINDADDR -w $NUM_WORKERS \
  --user=$USER --group=$GROUP --log-level=info --pid=$PIDFILE \
  --timeout=90 --log-file=$LOGFILE 2>>$LOGFILE
