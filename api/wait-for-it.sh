#!/bin/bash
host="mysql"
port="3306"
shift 2
cmd="$@"

until nc -z -v -w30 $host $port
do
  echo "Waiting for MySQL at $host:$port..."
  sleep 1
done

echo "MySQL is up!"
exec $cmd
