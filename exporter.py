#!/usr/bin/env python

import ssl
import argparse
import paho.mqtt.client as mqtt
from time import sleep
from PyP100 import PyP110
from yaml import safe_load
from multiprocessing import Process
from requests.exceptions import ConnectionError

mqtt_server = None
mqtt_port = None
mqtt_secure = False
mqtt_username = None
mqtt_password = None
mqtt_topic = None
tapo_username = None
tapo_password = None

### Get Command Line Arguments
def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--device-file", help="File containing device config", required=True)
  parser.add_argument("-s", "--mqtt-server", help="MQTT Server", required=True)
  parser.add_argument("-n", "--mqtt-port", help="MQTT Port", type=int, default="1883")
  parser.add_argument("-x", "--mqtt-secure", help="Enable MQTT over SSL", action="store_true")
  parser.add_argument("-u", "--mqtt-username", help="MQTT Username", required=True)
  parser.add_argument("-p", "--mqtt-password", help="MQTT Password", required=True)
  parser.add_argument("-t", "--mqtt-topic", help="MQTT Topic Prefix", required=True)
  parser.add_argument("-U", "--tapo-username", help="Tapo Username", required=True)
  parser.add_argument("-P", "--tapo-password", help="Tapo Password", required=True)
  args = parser.parse_args()
  return args

### Polling Function
def poll_device(device_name, device_ip):
  ### MQTT Connect Callback Function
  def on_connect(client, userdata, flags, rc):
    nonlocal mqtt_connected
    mqtt_connected = True
    print(f"Connected to MQTT Server - {device_name}")
  ### MQTT Disconnect Callback Function
  def on_disconnect(client, userdata, rc):
    nonlocal mqtt_connected
    mqtt_connected = False
    print(f"Disconnected from MQTT Server - {device_name}")

  mqtt_connected = False
  p110_connected = False

  try:
    mqtt_client = f"p110_{device_name}"
    client = mqtt.Client(mqtt_client)
    if mqtt_secure:
      client.tls_set(ca_certs='ca.crt', certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    client.username_pw_set(mqtt_username,mqtt_password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(mqtt_server, mqtt_port)
    client.loop_start()

    while True:
      sleep(60)
      try:
        if not p110_connected:
          print(f"Connecting to P110 - {device_name}")
          device = PyP110.P110(device_ip, tapo_username, tapo_password)
          device.handshake()
          device.login()
          p110_connected = True
          print(f"Connected to P110  - {device_name}")

        while mqtt_connected and p110_connected:
          sleep(10)
          energy = device.getEnergyUsage()['result']
          client.publish(f"{mqtt_topic}/{mqtt_client}/mqtt/today_runtime", energy['today_runtime'])
          client.publish(f"{mqtt_topic}/{mqtt_client}/mqtt/month_runtime", energy['month_runtime'])
          client.publish(f"{mqtt_topic}/{mqtt_client}/mqtt/today_energy", energy['today_energy'])
          client.publish(f"{mqtt_topic}/{mqtt_client}/mqtt/month_energy", energy['month_energy'])
          client.publish(f"{mqtt_topic}/{mqtt_client}/mqtt/current_power", energy['current_power'])
          client.publish(f"{mqtt_topic}/{mqtt_client}/mqtt/month_cost", sum(energy['electricity_charge']))

      except ConnectionError as e:
        p110_connected = False
        print(e)
        pass
      except KeyboardInterrupt:
        exit()
      except Exception as e:
        print(e)
  except ConnectionRefusedError:
    print(f"MQTT Server refused the connection for p110_{device_name}")
  except Exception as e:
    print(e)


### Main Function
def main():
  args = get_args()
  global mqtt_server
  global mqtt_port
  global mqtt_secure
  global mqtt_username
  global mqtt_password
  global mqtt_topic
  global tapo_username
  global tapo_password
  mqtt_server = args.mqtt_server
  mqtt_port = args.mqtt_port
  mqtt_secure = args.mqtt_secure
  mqtt_username = args.mqtt_username
  mqtt_password = args.mqtt_password
  mqtt_topic = args.mqtt_topic
  tapo_username = args.tapo_username
  tapo_password = args.tapo_password

  try:
    with open(args.device_file, "r") as device_cfg:
      devices = safe_load(device_cfg)
  except FileNotFoundError:
    print(f"File not found - {args.devices_file}")
    exit()

  # Create All Processes
  processes = [Process(target=poll_device, args=(plug['name'], plug['ip'])) for plug in devices['p110'].values()]

  # Start All Processes
  for process in processes:
    process.start()

  # Wait For All Processes To Complete
  for process in processes:
    process.join()

  # Report That All Processes Completed
  print('All processes stopped', flush=True)

if __name__ == "__main__":
  main()
