#!/bin/sh
python3 exporter.py --device-file devices.yaml --mqtt-server $MQTT_SERVER --mqtt-port $MQTT_PORT --mqtt-username $MQTT_USERNAME --mqtt-password $MQTT_PASSWORD --mqtt-topic $MQTT_TOPIC --mqtt-secure --tapo-username $TAPO_USERNAME --tapo-password $TAPO_PASSWORD
