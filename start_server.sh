#!/bin/sh

port="8080"
db_url="mongodb://192.168.99.100:32768/"
db_name="svt_test"

port=$port db_name=$db_name db_url=$db_url node api/bin/www # replace 'node bin/www' with 'npm start' at some point maybe
