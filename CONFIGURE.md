# Configuration

The component is generic and tries to adapt to all supported models. It is mostly configured via the UI however, due to limitations on the Renault API, some features may need to be configured manually.

## HVAC
Hvac status is not available for Zoe50 (model code X102VE). But Starting HVAC is possible with service `renault.ac_start`.

The service `renault.ac_stop` does not provide errors, but it is assumed that is as no effect on the vehicle.
Following MyRenaultApp documentation, HVAC is started between 5 and 50 min.

This is an example script to start HVAC for Zoe50 :
```yaml
# Scripts
script:
  start_hvac:
  alias: Start HVAC
  sequence:
  - service: renault.ac_start
      data:
      vin: VF1xxxxxxx
      temperature: 21
  # optional notification to device
  - device_id: xxxxxxxxxxxxx
    domain: mobile_app
    type: notify
    message: Starting HVAC at 21°C
    title: Renault ZOE
  # optional delay to avoid multiple launch 
  - delay:
      seconds: 300
  mode: single
  icon: mdi:snowflake
```

This is and example of switch :
```yaml
# Switches
switch:
  - platform: template
    switches:
      # Start AC now for five minutes (see script)
      zoe_ac_start:
        friendly_name: "A/C"
        icon_template: mdi:fan
        value_template: "{{ is_state('script.zoe_ac_start', 'on') }}"
        turn_on:
          service: homeassistant.turn_on
          data:
            entity_id: script.start_hvac
        turn_off:
          service: homeassistant.turn_off
          data:
            entity_id: script.start_hvac
```
