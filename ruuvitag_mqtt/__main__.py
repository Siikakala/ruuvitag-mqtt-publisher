import argparse
from pathlib import Path
import json
import logging
import signal
import time

from paho.mqtt import client as mqtt
from paho.mqtt.properties import Properties, PacketTypes
from ruuvitag_sensor.ruuvi import RuuviTagSensor

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

mqtt_client = mqtt.Client("RuuviTag")

processflag = True

def exit_handler(signum, frame):
    logger.info("SIGINT %s detected, disconnecting", signum)
    processflag = False
    mqtt_client.disconnect()
    time.sleep(6) # 6 seconds as ruuvi data gathering is ratelimited to once per 5s in main loop
    exit

def process_ruuvi_data(mqtt_client, mac_address, data):
    configured_ruuvitags = config.get("ruuvitags", {})
    location = configured_ruuvitags.get(mac_address, {}).get("name", mac_address)
    topic_prefix = config.get("topic_prefix", "")
    for key, value in data.items():
        fields = configured_ruuvitags.get(mac_address, {}).get("fields")
        retain = configured_ruuvitags.get(mac_address, {}).get("retain", False)
        if fields is None or key in fields:
            if key == "humidity":
                mqtt_client.publish(
                    f"smartthings/moisture/rpi/{location}/state",
                    str(value).replace(".", ","),
                    retain=retain,
                )
            else:
                mqtt_client.publish(
                    f"{topic_prefix}{location}/{key}",
                    value,
                    retain=retain,
                )


def start_publishing(config_file_path: Path):
    global config

    logger.info("Using config file: %s", config_file_path)

    if not config_file_path:
        config_file_path = Path(__file__).parent / "ruuvitag_mqtt.json"
    with open(config_file_path) as config_file:
        config = json.load(config_file)
    print(config)

    username = config.get("broker", {}).get("username")
    if username:
        logger.info("Using authentication: %s", username)
        password = config.get("broker", {}).get("password")
        mqtt_client.username_pw_set(username=username, password=password)

    mqtt_client.connect(
        host=config.get("broker", {}).get("host", "localhost"),
        port=config.get("broker", {}).get("port", 1883),
    )

    while (True):
        if processflag:
            if not mqtt_client.is_connected:
                mqtt_client.reconnect()
            data = RuuviTagSensor.get_data_for_sensors()
            for key,value in data.items():
                process_ruuvi_data(mqtt_client, key, value)
        else:
            break


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-c", dest="config_file")
    args = argument_parser.parse_args()

    signal.signal(signal.SIGINT, exit_handler)

    start_publishing(args.config_file)
