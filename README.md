# hassRenaultZE
A custom component for [Home Assistant](http://home-assistant.io/) to add battery status from the [Renault ZE Services website](https://www.services.renault-ze.com).

This is based on work by [edent] (https://github.com/edent/Renault-Zoe-API)

## What's Available?
The custom component will create a sensor with the battery information as attributes:

* plugged: false
* remaining_range: 151
* last_update: 2019-01-07T07:33:48
* charge_level: 60
* charging: false

A few point to note. The `remaining_range` is in Kilometres, and the `charge_level` is in %.

## Getting started
Initially, you'll need to make a note of your vehicule VIN, and register with [Renault ZE Services](https://www.services.renault-ze.com/). You will need to add the vin, the username and the password to your configuration file.

To install the component, you will need to copy renaultze.py and renaultzeservice.py to you local configuration folder:
```
 - .homeassistant
 | - custom_components
 | | - sensor
 | | | - renaultze.py
 | | | - shared
 | | | | - renaultzeservice.py
```

In your configuration.yaml, you will need to add a sensor:
```
sensor:
  - platform: renaultze
    name: MyCarBattery
    username: myemail@address.com
    password: !secret renaultze_password
    vin: XXXXXXXX
```

