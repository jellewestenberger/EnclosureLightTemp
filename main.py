import sys
import paho.mqtt.publish as publish
import json
import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqtt
import credentials
import threading
import gpiozero
import Adafruit_DHT
hostname = credentials.mqtthost
username=credentials.username
password=credentials.password
port = 1883 



#  publish.single(topic, payload=None, qos=0, retain=False, hostname="localhost",
#     port=1883, client_id="", keepalive=60, will=None, auth=None, tls=None,
#     protocol=mqtt.MQTTv311, transport="tcp")


global base_topic_light
global base_topic_hum
global base_topic_temp
global light_on
light_on = False
lightport = 27
global lightoutput
lightoutput=gpiozero.OutputDevice(lightport,initial_value=False)
dhtsensor=Adafruit_DHT.AM2302
dhtpin=4

base_topic_light = "homeassistant/light/enclosure"
base_topic_temp = "homeassistant/sensor/enclosure_temp"
base_topic_hum = "homeassistant/sensor/enclosure_humidity"

def on_connect(mqttc,obj, flags, rc):
    global base_topic_light
    print("Connected \n rc: ",str(rc))
    config_light=  '{"~": "%s", "name": "Enclosure", "unique_id": "enclosure_light", "cmd_t": "~/set", "stat_t": "~/state", "schema": "json", "brightness": false }' % base_topic_light
    config_temp = u'{"~": "%s","dev_cla": "temperature", "name": "enclosure_temp", "unit_of_meas": "\N{DEGREE SIGN}C", "stat_t": "~"}' % base_topic_temp
    config_hum = u'{"~": "%s","dev_cla": "humidity", "name": "enclosure_humidity", "unit_of_meas": "%%", "stat_t": "~"}' % base_topic_hum
    # config_light="" 
    mqttc.publish(base_topic_light+"/config",config_light,retain=True)
    mqttc.publish(base_topic_temp+"/config",config_temp,retain=True)
    mqttc.publish(base_topic_hum+"/config",config_hum,retain=True)

    check_light()   
    update_light()

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
            update_light()
               
            
def set_light():
    try:
        if light_on:
            lightoutput.on()
        elif not light_on:
            lightoutput.off()
        success= True
    except:
        success =False
        print("Failed to set light")
    return success

def check_light():
    global lightoutput
    global light_on
    val = lightoutput.value
    if val == 1: 
        light_on = True
        print("Light is on")
    else:
        light_on = False
        print("Light is off")
        

def update_light():
    global light_on
    global base_topic_light

    if light_on:
        mqttc.publish(base_topic_light+"/state",'{"state": "ON"}',qos=1)
    else:
        mqttc.publish(base_topic_light+"/state",'{"state": "OFF"}',qos=1)

def publish_dht(mqttc,temp,hum):
    global base_topic_hum
    global base_topic_temp
    mqttc.publish(base_topic_temp,temp)
    mqttc.publish(base_topic_hum,hum)

def on_publish(mqttc, obj, mid):
    print("publish: \n")
    print("mid: " + str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)


def read_dht(sensor,pin,T, mqttc):
    hum, temp = Adafruit_DHT.read_retry(sensor,pin,2,0.5)
    if hum is not None and temp is not None:
        hum = round(hum,2)
        temp = round(temp,2)
        publish_dht(mqttc,temp,hum)
        print("Temperature: %f \n Humidity: %f \n" % (hum, temp))        
    else:
        print('-1 | -1')    

    threading.Timer(T,read_dht,[sensor,pin,T,mqttc]).start()
    
mqttc=mqtt.Client()
mqttc.username_pw_set(username=username,password=password)
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

mqttc.connect(host=hostname,port=port)
mqttc.subscribe(base_topic_light+"/#")
read_dht(dhtsensor,dhtpin,15,mqttc)

mqttc.loop_forever()
