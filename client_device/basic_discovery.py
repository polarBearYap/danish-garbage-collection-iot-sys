# Sources: Amazon, https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/basic_discovery.py

# Import third-party library
import sys
from awscrt import io
from awsiot.greengrass_discovery import DiscoveryClient
from awsiot import mqtt_connection_builder
from awscrt import mqtt

# Import modules/files
from logger import logger

def perform_greengrass_discovery(args):
    mqtt_connection = None

    try:
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        tls_options = io.TlsContextOptions.create_client_with_mtls_from_path(args.dev_cert_path, args.dev_pk_path)
        if args.root_ca_path:
            tls_options.override_default_trust_store_from_path(None, args.root_ca_path)
        tls_context = io.ClientTlsContext(tls_options)

        socket_options = io.SocketOptions()

        logger.info('Performing greengrass discovery...')
        discovery_client = DiscoveryClient(client_bootstrap, socket_options, tls_context, args.region)
        resp_future = discovery_client.discover(args.thing_name)
        discover_response = resp_future.result()

        mqtt_connection = try_iot_endpoints(args, client_bootstrap, discover_response)
    except Exception as e:
        logger.exception(f'Exception occurred while performing greengrass discovery')
        exit(0)

    return mqtt_connection

def on_connection_interupted(connection, error, **kwargs):
    logger.warn('connection interrupted with error {}'.format(error))

# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    logger.info("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)

def on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))

# Try IoT endpoints until we find one that works
def try_iot_endpoints(args, client_bootstrap, discover_response):
    for gg_group in discover_response.gg_groups:
        for gg_core in gg_group.cores:
            for connectivity_info in gg_core.connectivity:
                try:
                    logger.info('Trying core {} at host {} port {}'.format(gg_core.thing_arn, connectivity_info.host_address, connectivity_info.port))
                    mqtt_connection = mqtt_connection_builder.mtls_from_path(
                        endpoint=connectivity_info.host_address,
                        port=connectivity_info.port,
                        cert_filepath=args.dev_cert_path,
                        pri_key_filepath=args.dev_pk_path,
                        client_bootstrap=client_bootstrap,
                        ca_bytes=gg_group.certificate_authorities[0].encode('utf-8'),
                        on_connection_interrupted=on_connection_interupted,
                        on_connection_resumed=on_connection_resumed,
                        client_id=args.thing_name,
                        clean_session=False,
                        keep_alive_secs=30)

                    connect_future = mqtt_connection.connect()
                    connect_future.result()

                    logger.info('Successfully connected to IoT endpoint')

                    return mqtt_connection

                except Exception as e:
                    logger.error('Connection failed with exception {}'.format(e))
                    continue

    logger.error('Failed to connect to any IoT endpoints.')
