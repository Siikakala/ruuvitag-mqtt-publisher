#!/bin/bash

cp ruuvitag-mqtt.service /etc/systemd/system/
cp -n ruuvitag_mqtt/ruuvitag_mqtt.json /etc
systemctl enable ruuvitag-mqtt.service
