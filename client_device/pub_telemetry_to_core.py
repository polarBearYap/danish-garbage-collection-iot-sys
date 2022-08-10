# Author: Yap Jheng Khin
# Note that the code logic is tailored to the assignment's requirement
# Refer to sample codes in the https://github.com/aws/aws-iot-device-sdk-python-v2 to get the template

# Import third-party library
import argparse
from awscrt import io
from awscrt.mqtt import QoS
import json
import os
import threading

# Import modules/files
from logger import logger
import basic_discovery

parser = argparse.ArgumentParser()

# Constants
T = True
F = False
QOS = {
    "at_most_once" : QoS.AT_MOST_ONCE,
    "at_least_once": QoS.AT_LEAST_ONCE
}

LOG_LEVEL = {
    "nologs": 0,
    "fatal" : 1,
    "error" : 2,
    "warn"  : 3,
    "info"  : 4,
    "debug" : 5,
    "trace" : 6,
}

parser.add_argument('-t', '--thing-name', required=T, action='store', dest='thing_name',    help='Thing name for this client device')
parser.add_argument('-c', '--dev-cert',   required=T, action='store', dest='dev_cert_path', help='Client device\'s certificate file path')
parser.add_argument('-k', '--dev-key',    required=T, action='store', dest='dev_pk_path',   help='Client device\'s private key file path')
parser.add_argument('-r', '--root-ca',    required=T, action='store', dest='root_ca_path',  help='Root CA file path')
parser.add_argument('-R', '--region',     required=F, action='store', dest='region',        help='Region ', default='us-east-1')
parser.add_argument('-p', '--pub-topics',  required=T, action='store', dest='pub_topics',     help='Topic to publish', default='no_topic')
parser.add_argument('-M', '--message-path',   required=T, action='store', dest='message_path', help='JSON file that contains message(s) to publish', default='None')
parser.add_argument('-Q', '--qos',        required=T, action='store', dest='qos',           help='Quality of service', choices=list(QOS.keys()))
parser.add_argument('-v', '--verbosity',  required=T, action='store', dest='verbosity',     help='Logging level', choices=list(LOG_LEVEL.keys()))

# Parse command-line argument into variables
args = parser.parse_args()

# Preprocess arguments
args.qos = QOS[args.qos.lower()]
args.verbosity = LOG_LEVEL[args.verbosity.lower()]

# Initialize logging in awscrt
io.init_logging(args.verbosity, 'stderr')

# Perform greengrass discovery
mqtt_connection = basic_discovery.perform_greengrass_discovery(args)

# ------------------------------------------------------------------------------------------- #
# Publish messages to topic
# ------------------------------------------------------------------------------------------- #

# Publish to topic to send message
try:
	pub_topics = []
	with open(args.pub_topics) as f:
		for pub_topic in f:
			pub_topics.append(pub_topic.strip())

except Exception as e:
	logger.exception(f'Exception occurred when reading the publish topics in {args.pub_topics}. Refer to the sample file for the format')

# Assume that the sequence of topic to publish in same with the device_id 
for device_id in range(1, len(pub_topics)+1):
	pub_topic = pub_topics[device_id-1]
	logger.info(f"Publishing telemetry to {pub_topic} on behalf of danish-garbage-bin-{device_id}...")
	cur_seq = 1
	messages_filename = os.path.join(args.message_path, f"danish-garbage-bin-{device_id}-telemetry.json")
	try:
		with open(messages_filename) as f:
			json_messages = json.load(f)
	# Refer to the sample json file for the format
	# The loaded json must be an array of dictionaries
	except Exception as e:
		logger.exception(f'Exception occurred when reading the JSON in {args.json_messages}. Refer to the sample JSON file for the format')
		exit(0)

	for json_message in json_messages:
		json_message['sequence'] = str(cur_seq)
		cur_seq += 1
		messageJson = json.dumps(json_message).encode('utf-8')
		pub_future, _ = mqtt_connection.publish(pub_topic, messageJson, args.qos)

	try:
		pub_future.result()
	except Exception as e:
		logger.exception(f'Exception occurred while publishing to {pub_topic}')
		exit(0)
	logger.info(f'Successfully publish all messages (qos: {args.qos}) to the topic {pub_topic} on behalf of danish-garbage-bin-{device_id}')

# Disconnect from the MQTT broker endpoints in the core device
logger.info("Trying to disconnecting from MQTT broker in the core device")
disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
logger.info("Disconnection successful. Program exits.")
