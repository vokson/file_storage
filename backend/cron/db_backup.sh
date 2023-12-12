#!/usr/bin bash

# Copy backups in ../backups directory. CHANGE IF NECESSARY.
pg_dumpall -p ${DB__PORT} -c -U postgres | gzip > /backups/${SERVER_NAME}_`date +%d-%m-%Y"_"%H_%M_%S`.sql.gz
#  Delete all files older than one week
find /backups/ -mindepth 1 -mmin +10080 -delete