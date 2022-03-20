# MQTT Light Control + DHT Read/Publish
This code has been tested on a Raspberry Pi Zero W to read temperature and humidity measurements from a DHT22. Subsequently these are published to an MQTT broker.

Additionally, MQTT light control has been implemented that controls the digitaloutput of a GPIO. 

Home Assistant MQTT discovery is supported. So there is no need to manually configure the MQTT entities in Home Assistant 

Make sure to create a `credentials.py` file that contains


password = "yourmqttpassword" 

username= "yourmqttusername"

also modify hostname and port in `main.py` according to your mqtt host settings

## How to setup as service 
You can set up any python script as systemctl service so that it automatically runs on boot and restarts after a crash. 

First create your service file in `/etc/systemd/system/yourservice.service`

`yourservice.service` contains:

```
[Unit]
Description=Enclosure DHT read and Light Control
After=multi-user.target

[Service]
Type=simple
Restart=on-abort
ExecStart=/usr/bin/python3 <path to main.py>
User=<yourhostusername> 

[Install]
WantedBy=multi-user.target
```
Reload the deamon by running `sudo systemctl daemon-reload`

Enable your service with `sudo systemctl enable yourservice.service`

Start your service with `sudo systemctl start yourservice.service`

Stop you service with `sudo systemctl stop yourservice.service`

Check the status of your service with `sudo systemctl status yourservice.service`