# hassRenaultZE
A custom component for [Home Assistant](http://home-assistant.io/) to add battery status from the MyRenault services.

This is based on work by [jamesremuscat](https://github.com/jamesremuscat/pyze)

## What's Available?
The custom component will create a sensor with the battery charge level (in %), together with the following attributes:

- charging: false
- last_update: 2019-01-07T07:33:48Z
- plugged: false
- remaining_range: 151
- battery_temperature: 14 *(the attribute appeared on MyRenault, and then disappeared - maybe linked to model?)*

A few point to note. The `remaining_range` is in Kilometres, and the `charge_level` is in %.

## Getting started
Initially, you'll need to make a note of your vehicule VIN, and register with MyRenault application. You will need to add the vin, the language code for your country, the username and the password to your configuration file.

To install the component, you will need to copy the three files to you local configuration folder:
```
 - .homeassistant
 | - custom_components
 | | - renaultze
 | | | - __init__.py
 | | | - manifest.json
 | | | - sensor.py
 | | | - services.yaml
```

In your configuration.yaml, you will need to add a sensor:
```
sensor:
  - platform: renaultze
    name: MyCar
    username: myemail@address.com
    password: !secret renaultze_password
    vin: XXXXXXXX
    android_lng: fr_FR
    k_account_id: abcdef123456789
```

Please note that these configuration setting are optional:
- name *(defaults to VIN)*
- android_lng *(defaults to fr_FR)*
- k_account_id *(default to empty, which may cause a warning if multiple accounts are associated with the credentials)*

## Converting attributes to sensors
Template sensors can be added to your configuration.yaml to display the attributes as sensors.
```
sensor:
  - platform: template
    sensors:
      mycar_plugged:
        value_template: "{{ state_attr('sensor.mycar' , 'plugged') }}"
        friendly_name: "Plugged"
  - platform: template
    sensors:
      mycar_charging:
        value_template: "{{ state_attr('sensor.mycar' , 'charging') }}"
        friendly_name: "Charging"
  - platform: template
    sensors:
      mycar_remaining_range:
        value_template: "{{ state_attr('sensor.mycar' , 'remaining_range') }}"
        friendly_name: "Range"
        unit_of_measurement: "km"
  - platform: template
    sensors:
      mycar_mileage:
        value_template: "{{ state_attr('sensor.mycar' , 'mileage') }}"
        friendly_name: "Mileage"
        unit_of_measurement: "km"
  - platform: template
    sensors:
      mycar_battery_temperature:
        value_template: "{{ state_attr('sensor.mycar' , 'battery_temperature') }}"
        friendly_name: "Battery temperature"
        unit_of_measurement: "°C"
```

## Logging
If you are having issues with the component, please enable debug logging in your configuration.yaml, for example:
```
logger:
  default: warn
  logs:
    custom_components.renaultze.sensor: debug
```
