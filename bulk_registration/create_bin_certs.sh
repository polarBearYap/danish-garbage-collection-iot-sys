#!/bin/bash

# Example usage:
# 1) mkdir Device_Certs
# 2) sudo chmod 777 ./create_bin_certs.sh
# 3) ./create_bin_certs.sh -d Device_Certs -s 1 -e 15

# d, s & e option must have a required parameter
while getopts d:s:e: flag
do
	# Collect parameter values that passed to the script
	case "${flag}" in
		d) dest_path=$OPTARG;; # The file path that stores the newly created device certificates
		s) start_id=$OPTARG;; # The start number of the unique device ID
		e) end_id=$OPTARG;; # The end number of the unique device ID
	esac
done

# Change to the directory where new certificates are placed
cd $dest_path

# Certificate's information
country="MY"
state="Perak"
location="Kampar"
organization="International IT Solution Sdn Bhd"
organization_unit="IT Department"
email="service@itsolution.com"

for ((i = $start_id ; i <= $end_id ; i++)); do
    # Get the filenames and common name for the ith bin
	filename="binCert$i"
	pk_filename="$filename.key"
	req_filename="$filename.csr"

	common_name="danish-garbage-bin-$i"
	sub_args="/C=$country/ST=$state/L=$location/O=$organization"
	sub_args+="/OU=$organization_unit/CN=$common_name/emailAddress=$email"

	# Generate the current bin's private key and certificate sign request
	openssl req -new -newkey rsa:2048 -nodes -keyout $pk_filename \
	-out $req_filename -subj "$sub_args"
done
