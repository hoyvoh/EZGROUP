#!/bin/sh

echo "CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE};" > /docker-entrypoint-initdb.d/1-init.sql
echo "CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';" >> /docker-entrypoint-initdb.d/1-init.sql
echo "GRANT ALL PRIVILEGES ON ${MYSQL_DATABASE}.* TO '${MYSQL_USER}'@'%';" >> /docker-entrypoint-initdb.d/1-init.sql
echo "FLUSH PRIVILEGES;" >> /docker-entrypoint-initdb.d/1-init.sql

cat /docker-entrypoint-initdb.d/1-init.sql
