#!/bin/bash

cd `dirname $0`
if [ -d $1 ]; then 
  echo 'got one'; 
  exit
else 
  echo 'create new '; 
fi;

mkdir ./$1

LOG="ca.log"

echo "Create $1 " >> $LOG 

#echo -en "" > ../index.txt
#echo -en "00" > ../serial

echo "STAGE 1" >> $LOG 
B=' -batch '

C=' '
openssl req $B $C -days 365 -nodes -new -keyout ./$1/cert.key -out ./$1/cert.csr -subj "/C=IT/CN=$1/O=it/OU=it" 2>> $LOG  >> $LOG

echo "STAGE 2 " >> $LOG 
C=' -config openssl.cnf  '

openssl ca $B $C -cert ../ca.pem -out ./$1/cert.crt -infiles ./$1/cert.csr 2>> $LOG  1>> $LOG 

echo "STAGE 3 " >> $LOG 

cat ./$1/cert.crt ./$1/cert.key > ./$1/cert.pem 
