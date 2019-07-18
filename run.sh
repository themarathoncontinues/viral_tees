#!/bin/bash
HOME=/root
LOGNAME=root
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
LANG=en_US.UTF-8
SHELL=/bin/sh
PWD=/root

source /home/envs/vt/bin/activate
source /home/git/viral_tees/.env

python /home/git/viral_tees/run_luigi.py --all --soft 

deactivate
