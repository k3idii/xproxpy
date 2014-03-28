#!/bin/bash
openssl req -config openssl.cnf -extensions v3_ca -days 3650 -new -x509 -keyout ca.key -out ca.crt -nodes

cat ca.crt ca.key > ca.pem


echo -en > index.txt

echo 10000 > serial
