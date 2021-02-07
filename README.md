# ruuvitag-mqtt

RuuviTag MQTT Publisher. Meant to be installed on Raspberry Pi Zero.

# Install

## Libs and the actual service

Install prerequisites by following the instructions here:
https://github.com/ttu/ruuvitag-sensor

Then clone the repo and run:

    sudo python3 -m pip install -U pip setuptools

    sudo python3 -m pip install .
    ./setup_service.sh

The setup script creates a Systemd setup file and enables the ```ruuvitag-mqtt.service``` to start automatically on startup.


## Configuration

Write config file: ```/etc/ruuvitag-mqtt.conf```

Example:

```json
    {
        "broker": {
            "host": "192.168.1.11",
            "port": 1883
        },
        "ruuvitags": {
            "DE:D4:96:2C:3C:78": {
                "name": "kitchen",
                "fields": ["temperature", "humidity"],
                "retain": true
            },
            "E3:35:52:F1:D2:AA": {
                "name": "terrace",
                "fields": ["temperature", "humidity", "pressure"],
                "retain": true
            },
            "F9:89:71:39:A5:82": {
                "name": "sauna",
                "fields": ["temperature", "humidity"],
                "retain": true
            }
        }
    }
```

Note: The file must exist. By default service uses localhost:1883 as the broker address so if the broker is running on the same machine then just an empty JSON dictionary is the minimum configuration needed.


## Start service

    systemctl start ruuvitag-mqtt.service
