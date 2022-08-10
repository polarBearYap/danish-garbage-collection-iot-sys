#!/bin/bash

# Example usage:
# sudo chmod 777 ./create_bulk_registration_params.sh
# ./create_bulk_registration_params.sh -i devices.txt -p Device_Certs -s 1 -o bulk_registration_params.txt

# i, o, s & p option must have a required parameter
while getopts i:o:s:p: flag
do
	# Collect parameter values that passed to the script
	case "${flag}" in
		i) device_metadata_filename=$OPTARG;; # The text file that contains device metadata
		o) output_filename=$OPTARG;; # The output file that stores the parameter values required for the bulk registration
		s) start_id=$OPTARG;; # The start number of the unique device ID
		p) device_cert_path=$OPTARG;; # The file path that stores the newly created device certificates
	esac
done

# Obtain the absolute path of the given file/directory
# Source: https://stackoverflow.com/a/3915420
function realpath {
	echo $(cd $(dirname $1); pwd)/$(basename $1);
}

# Get the absolute paths of these files before changing directory
device_metadata_filename=$(realpath $device_metadata_filename)
output_filename=$(realpath $output_filename)

# Change to the directory where new certificates are placed
cd $device_cert_path

# The template to form the JSON strings
json_template1='{"ThingName": "%s", "HouseArea": "%s","HouseNumber": "%s", "FloorNumber": "%s", "SerialNumber": "%s", '
json_template2='"ManufacturingDate": "%s", "DeviceCertificateId": "%s"}\n'

cur_id=$start_id

# Clear the output file content
> $output_filename

while read record; do
	# Split the record by delimiter ',' and store into an array
	IFS=',' read -ra metadata <<< "$record"
	
	# Fetch the field from the array
	thing_name="danish-garbage-bin-$cur_id"
	house_area=${metadata[0]}
	house_number=${metadata[1]}
	floor_number=${metadata[2]}
	serial_number=${metadata[3]}
	manufacturing_year=${metadata[4]}
	
	# Get the filename of the device certificate
	filename="binCert$cur_id"
	dev_csr_filename="$filename.csr"
	dev_cert_filename="$filename.pem.crt"

	csr_output=$(aws iot create-certificate-from-csr --certificate-signing-request=file://$dev_csr_filename)
	dev_cert=$(echo $csr_output | jq --raw-output ".certificatePem")
	$(echo $dev_cert > $dev_cert_filename)
	dev_cert_id=$(echo $csr_output | jq --raw-output ".certificateId")
	$(aws iot update-certificate --certificate-id $dev_cert_id --new-status "ACTIVE")

	# Format the metadata and certificates into JSON string
	json_payload=$(printf "$json_template1" "$thing_name" "$house_area" "$house_number" "$floor_number" "$serial_number")
	json_payload+=$(printf "$json_template2" "$(date +"%d-%m-%Y")" "$dev_cert_id")

	# Increment unique device ID by 1
	cur_id=$(( $cur_id+1 ))

	# Append the JSON string to the output file
	echo $json_payload >> $output_filename

# Read from a text file containing the client devices' metadata 
done < $device_metadata_filename
