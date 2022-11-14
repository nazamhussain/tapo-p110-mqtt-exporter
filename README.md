# Tapo P110 MQTT Exporter

*Python based MQTT exporter for energy usage stats from Tapo P110 smart plugs*

Export energy usage data from Tapo P110 smart plugs to a specified MQTT topic - from there you can choose what you wish to do with the data.


## Environment Variables

The following variables must be specified - either as arguments to the Python script if running manually or by adding them to a **variables.env** file if you choose to use Docker Compose.

`MQTT_SERVER`

`MQTT_PORT`

`MQTT_USERNAME`

`MQTT_PASSWORD`

`MQTT_TOPIC`

`TAPO_USERNAME`

`TAPO_PASSWORD`


## Secure MQTT

The assumption is that MQTT communication will authenticated via username/password and encrypted via SSL.

Overwrite the contents of **ca.crt** with the public certificate of the CA used to generate the SSL certificate for your MQTT server.

If you want to use anonymous or insecure MQTT then you will need to adjust the config accordingly - but why would you do that? :-)


## Python Script

The Python script essentially does the following:

- Gets details of smart plugs from the **devices.yaml** file
- Starts a polling process for each smart plug
- Each process connects to the MQTT server via a unique client id
- Each process connects to an individual smart plug
- When connected to the MQTT server and smart plug, each process collects energy usage data and publishes it to the specified MQTT topic on a regular basis (at 10 second intervals)


## Adding Devices

Add your smart plugs to the **devices.yaml** file

```
p110:
  01:
    name: plug_01
    ip: 192.168.0.1
  02:
    name: plug_02
    ip: 192.168.0.2
```
