# hassRenaultZE
A custom component for [Home Assistant](http://home-assistant.io/) to add car status from the MyRenault services.

This is based on work by [jamesremuscat](https://github.com/jamesremuscat/pyze)

## What's Available?
The custom component will create various sensors and trackers:

binary sensors:
- charging (with last update attribute)
- plugged in (with last update attribute)

sensors:
- battery level (with last update, available energy and battery temperature attributes)
- charge mode
- charge state (with last update attribute)
- charging power (with last update attribute)
- mileage
- outside temperature
- plug state (with last update attribute)
- range (with last update attribute)


## Getting started
To install the component, you will need to copy the content of the renault folder into your local configuration folder:
```
 - .homeassistant
 | - custom_components
 | | - renault
 | | | - translations
 | | | | - en.json
 | | | - __init__.py
 | | | - binary_sensor.json
 | | | - (...)
 | | | - services.yaml
 | | | - strings.json
```

Then, you will need to prepare the Gigya and Kamereon API keys (for instructions, check https://github.com/jamesremuscat/pyze#obtaining-api-keys)
Once you have made a note of the keys, you can configure the component via the config-flow, available through the configuration > integrations menu.
You will be prompted for your Renault credentials (email/password) and finally you will need to select a Kamereon account id (if more than one is available).

## Logging
If you are having issues with the component, please enable debug logging in your configuration.yaml, for example:
```
logger:
  default: info
  logs:
    pyze: debug
    custom_components.renault: debug
```
