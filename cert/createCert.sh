#!/bin/bash

cd `dirname $0`
DD="./domains/${1}"

if [ -d ${DD} ]; then 
  echo 'got one'; 
  exit
else 
  echo 'create new '; 
fi;

mkdir ./${DD}

LOG="ca.log"

echo "Create ${DD} " >> $LOG 

echo "STAGE 1" >> $LOG 
B=' -batch '

C=' '
openssl req $B $C -days 365 -nodes -new -keyout ./${DD}/cert.key -out ./${DD}/cert.csr -subj "/C=IT/CN=$1/O=it/OU=it" 2>> $LOG  >> $LOG

echo "STAGE 2 " >> $LOG 
C=' -config openssl.cnf  '

openssl ca $B $C -cert ./ca.pem -out ./${DD}/cert.crt -infiles ./${DD}/cert.csr 2>> $LOG  1>> $LOG 

echo "STAGE 3 " >> $LOG 

cat ./${DD}/cert.crt ./${DD}/cert.key > ./${DD}/cert.pem


