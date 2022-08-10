# Author: Yap Jheng Khin
# Note that the code logic is tailored to the assignment's requirement
# Refer to sample codes in the https://github.com/aws/aws-iot-device-sdk-python-v2 to get the template

# Import third-party library
import argparse
from awscrt import io
from awscrt.mqtt import QoS
import json
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
parser.add_argument('-s', '--sub-topic',  required=F, action='store', dest='sub_topic',     help='Topic to subscribe', default='no_topic')
parser.add_argument('-p', '--pub-topic',  required=F, action='store', dest='pub_topic',     help='Topic to publish', default='no_topic')
parser.add_argument('-m', '--mode',       required=T, action='store', dest='mode',          help='Publish mode/Subscribe mode', choices=['pub', 'sub', 'both'])
parser.add_argument('-S', '--seq-no',     required=T, action='store', dest='seq_no',        help='Start sequence number of the messages')
parser.add_argument('-M', '--messages',   required=F, action='store', dest='json_messages', help='JSON file that contains message(s) to publish', default='None')
parser.add_argument('-n', '--sub-count',  required=F, action='store', dest='sub_count',     help='Number of messages expected to received from the subscribed topic', default='None')
parser.add_argument('-Q', '--qos',        required=T, action='store', dest='qos',           help='Quality of service', choices=list(QOS.keys()))
parser.add_argument('-v', '--verbosity',  required=T, action='store', dest='verbosity',     help='Logging level', choices=list(LOG_LEVEL.keys()))

# Parse command-line argument into variables
args = parser.parse_args()

# Preprocess arguments
args.qos = QOS[args.qos.lower()]
args.verbosity = LOG_LEVEL[args.verbosity.lower()]
args.seq_no = int(args.seq_no)

# Initialize logging in awscrt
io.init_logging(args.verbosity, 'stderr')

# Perform greengrass discovery
mqtt_connection = basic_discovery.perform_greengrass_discovery(args)

# ------------------------------------------------------------------------------------------- #
# Mode `sub`/`both`: Subscribe to topic to receive message
# ------------------------------------------------------------------------------------------- #
if args.mode == 'sub' or args.mode == 'both':

    # Pattern/code logic referred from https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/pubsub.py
    class SubStatus:
        total_message = -1
        cur_sub_count = 0
        receive_statuses = {}
        all_message_received = threading.Event()

    if args.sub_count == 'None':
        logger.error(f"The argument `--sub-count` is required for subscription mode.")
        exit(0)

    args.sub_count = int(args.sub_count)

    if args.sub_topic == 'no_topic':
        logger.error(f"The argument `--sub-topic` is required for subscription mode.")
        exit(0)

    if args.sub_count <= 0:
        logger.error(f"Invalid value for argument `--sub-count` in subscription mode, value must be larger than 0.")
        exit(0)
    else:
        SubStatus.total_message = args.sub_count
        for ms_id in range(args.seq_no, args.seq_no + args.sub_count):
            SubStatus.receive_statuses[ms_id] = False

    # Define a publish callback to handle received messages
    def publish_callback(topic, payload, dup, qos, retain, **kwargs):
        try:
            json_payload = json.loads(payload.decode('utf-8'))
            cur_seq_no = json_payload["sequence"]
            logger.info(f'Successfully receive the message (seq no: {cur_seq_no}, qos: {qos}) from the {topic}: {payload}')

            # In production environment, 
            # If the response status is OK (200):
            #   - The IoT garbage bin will retrieve the inferred trash type and sort the trash accordingly.
            # Else if the response status is BAD REQUEST (400):
            #   - The IoT garbage bin will retrieve the error information, fix the payload format, and 
            #     resend the request accordingly.
            # The logic is not implemented in this assignment since no hardware is available and due to 
            # time constraint.

            # Check if the message has already been received by checking the reference number
            # Note that the MQTT broker might send duplicate messages if QOS is set to AT_LEAST_ONE
            if not SubStatus.receive_statuses[cur_seq_no]:
                SubStatus.cur_sub_count += 1
                SubStatus.receive_statuses[cur_seq_no] = True
            # If all command responses have returned, set the internal flag of thread to true to 
            # unblock the main thread so that the program can exit
            if SubStatus.cur_sub_count == SubStatus.total_message:
                SubStatus.all_message_received.set()
                logger.info("All messages have been received.")

        except Exception:
            logger.exception(f"Error occurred while handling the message received from {topic}")

    # Initiate the topic subscription
    subscribe_future, _ = mqtt_connection.subscribe(args.sub_topic, args.qos, publish_callback)
    
    try:
        subscribe_result = subscribe_future.result()
        logger.info(f'Successfully subscribe to {args.sub_topic}, and MQTT server granted QOS of {subscribe_result["qos"]}')
    except Exception as e:
        logger.exception(f'Exception occurred while subscribing to {args.sub_topic}')
        exit(0)

# ------------------------------------------------------------------------------------------- #
# Mode `pub`/`both`: Publish messages to topic
# ------------------------------------------------------------------------------------------- #
if args.mode == 'pub' or args.mode == 'both':

    if args.pub_topic == 'no_topic':
        logger.error(f"The argument `--pub-topic` is required for publish mode.")
        exit(0)

    if args.json_messages == 'None':
        logger.error(f"The argument `--messages` is required for publish mode.")
        exit(0)

    cur_seq = args.seq_no

    # Publish to topic to send message
    try:
        with open(args.json_messages) as f:
            json_messages = json.load(f)
        # Refer to the sample json file for the format
        # The loaded json must be an array of dictionaries
    except Exception as e:
        logger.exception(f'Exception occurred when reading the JSON in {args.json_messages}. Refer to the sample JSON file for the format')
        exit(0)

    for json_message in json_messages:

        json_message['sequence'] = cur_seq
        messageJson = json.dumps(json_message).encode('utf-8')

        pub_future, _ = mqtt_connection.publish(args.pub_topic, messageJson, args.qos)

        try:
            pub_future.result()
            logger.info(f'Successfully publish the message (seq no: {cur_seq}, qos: {args.qos}) to the topic {args.pub_topic}: {messageJson}')
            cur_seq += 1
        except Exception as e:
            logger.exception(f'Exception occurred while publishing to {args.pub_topic}')
            exit(0)

if args.mode == 'sub' or args.mode == 'both':
    # Wait for all messages to be received.
    if not SubStatus.all_message_received.is_set():
        logger.info("Waiting for all messages to be received...")

    # Block the main thread until all the messages are received
    SubStatus.all_message_received.wait()

# Disconnect from the MQTT broker endpoints in the core device
logger.info("Trying to disconnecting from MQTT broker in the core device")
disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
logger.info("Disconnection successful. Program exits.")
