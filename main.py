import sys
import paho.mqtt.publish as publish
import json
import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqtt
import credentials
import gpiozero
hostname = "192.168.178.44"
username=credentials.username
password=credentials.password
port = 1883 



#  publish.single(topic, payload=None, qos=0, retain=False, hostname="localhost",
#     port=1883, client_id="", keepalive=60, will=None, auth=None, tls=None,
#     protocol=mqtt.MQTTv311, transport="tcp")


global base_topic
global light_on
lightport = 22
# lightoutput=gpiozero.OutputDevice(lightport,initial_value=True)
global base_topic
base_topic = "homeassistant/light/enclosure"
light_on= False
# config_payload = "" 

# publish.single(config_topic,payload=config_payload,hostname=hostname,client_id="viscode",auth={'username': username, 'password': password}, port =port)

def on_connect(mqttc,obj, flags, rc):
    global base_topic
    print("rc: ",str(rc))
    config_payload=  '{"~": "%s", "name": "Enclosure", "unique_id": "enclosure_light", "cmd_t": "~/set", "stat_t": "~/state", "schema": "json", "brightness": false }' % base_topic
    # config_payload="" 
    mqttc.publish(base_topic+"/config",config_payload)
    state_update()

def on_message(mqttc, obj, msg):
    global light_on
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if msg.topic.split("/")[-1] == 'set':
        payload=json.loads(msg.payload)
        if payload['state'] == 'ON': 
            light_on = True           
        elif payload['state'] == 'OFF':
            light_on = False
                   
        if set_light():
            state_update()
               
            
def set_light():
    success= True
    return success

def state_update():
    global light_on, base_topic

    if light_on:
        mqttc.publish(base_topic+"/state",'{"state": "ON"}',qos=1)
    else:
        mqttc.publish(base_topic+"/state",'{"state": "OFF"}',qos=1)

def on_publish(mqttc, obj, mid):
    print("publish: \n")
    print("mid: " + str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)


mqttc=mqtt.Client()
mqttc.username_pw_set(username=username,password=password)
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

mqttc.connect(host=hostname,port=port)
mqttc.subscribe(base_topic+"/#")
mqttc.loop_forever()