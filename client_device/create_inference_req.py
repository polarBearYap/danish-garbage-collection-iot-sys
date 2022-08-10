# Author: Yap Jheng Khin
# 
# In production environment, 
#   - The image is uploaded via other protocols such as HTTPS. It is because AWS IoT MQTT protocol 
#     only support payload size up to 128KB. The payload may contain the filename and image format 
#     that is uploaded to the core device.
# 
# In this assignment,
#   - Due to time constraint and absence of hardware, the image is preloaded in the inference 
#     component's working directory. So, the payload doesn't need to contain the complete information 
#     of the image file since the component will randomly fetch an image from the directory. 
# 
# Source: https://docs.aws.amazon.com/general/latest/gr/iot-core.html#iot-protocol-limits

from datetime import datetime, timedelta
import json

inference_requests = []

TOTAL_IMAGE = 12
req_interval_in_minute = 5

for iter_no in range(TOTAL_IMAGE):
    inference_req = {
        # Change the thing name if use other client downstream device
        "client-id": "danish-garbage-bin-1",
        # Change this response topic if not using danish-garbage-bin-1
        # Refer to the recipe in the aws.greengrass.clientdevices.Auth to check the authorization policies
        "res-topic": "command/danish-gcs/area-beijing/house-1059/floor-1/bin/1/res",
        "action": {
            "type": "trash-classification",
            # The format is pre-determined since this assignment only use sample image
            "img-format": "jpg"
        }
    }
    cur_utc_time = datetime.utcnow() + timedelta(minutes=req_interval_in_minute*iter_no)
	# Discard the seconds
    inference_req["utc-timestamp"] = int(cur_utc_time.timestamp()) # UTC timestamp
    # Replace this with industry-grade session generator
    # For this assignment, session-id will be used as the name of the image file uploaded to the core device
    inference_req["session-id"] = f'{inference_req["client-id"]}-{inference_req["utc-timestamp"]}'
    inference_requests.append(inference_req)

with open("./inference_req_payload.json", 'w') as f:
    f.write(json.dumps(inference_requests))