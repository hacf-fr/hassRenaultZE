#!/usr/bin/env python3

import asyncio
import time
from datetime import datetime, timedelta

# All the shared functions are in this package.
from custom_components.sensor.renaultzeservice.renaultzeservice import (
    RenaultZEService,
    RenaultZEServiceException
    )

# This script makes heavy use of JSON parsing.
import json

ATTR_CHARGING = 'charging'
ATTR_PLUGGED = 'plugged'
ATTR_CHARGE_LEVEL = 'charge_level'
ATTR_REMAINING_RANGE = 'remaining_range'
ATTR_LAST_UPDATE = 'last_update'

# Load credentials.
in_file = open('credentials.json', 'r')
credentials = json.load(in_file)
in_file.close()

# Get the VIN.
vin = credentials['VIN']


class logger():
    def error(self, value):
        print("Error: %s" % value)

    def warning(self, value):
        print("Warning: %s" % value)

    def warn(self, value):
        print("Warn: %s" % value)

    def info(self, value):
        print("Info: %s" % value)

    def debug(self, value):
        print("Debug: %s" % value)


class Entity():
    """Fake HASS Entity"""


class RenaultZESensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, wrapper, vin, name):
        """Initialize the sensor."""
        _LOGGER.debug("Initialising RenaultZESensor %s" % name)
        self._state = None
        self._wrapper = wrapper
        self._battery_url = '/api/vehicle/' + vin + '/battery'
        self._name = name
        self._attrs = {}
        self._attrs[ATTR_CHARGING] = None
        self._attrs[ATTR_LAST_UPDATE] = None
        self._attrs[ATTR_PLUGGED] = None
        self._attrs[ATTR_REMAINING_RANGE] = None
        self._lastdeepupdate = 0

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return self._attrs

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return '%'

    def process_response(self, jsonresult):
        """Update new state data for the sensor."""
        self._state = jsonresult[ATTR_CHARGE_LEVEL]

        self._attrs[ATTR_CHARGING] = jsonresult[ATTR_CHARGING]
        self._attrs[ATTR_LAST_UPDATE] = datetime.fromtimestamp(
            jsonresult[ATTR_LAST_UPDATE] / 1000
            ).isoformat()
        self._attrs[ATTR_PLUGGED] = jsonresult[ATTR_PLUGGED]
        self._attrs[ATTR_REMAINING_RANGE] = jsonresult[ATTR_REMAINING_RANGE]

        # Check lastserverupdate (prevent 
        lastserverupdate = jsonresult[ATTR_LAST_UPDATE] / 1000
        if lastserverupdate > self._lastdeepupdate:
            self._lastdeepupdate = lastserverupdate

    async def async_update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # Run standard update
        try:
            jsonresult = await self._wrapper.apiGetCall(self._battery_url)
            _LOGGER.debug("Update result: %s" % jsonresult)
            self.process_response(jsonresult)
            await self.async_deep_update()
        except RenaultZEServiceException as e:
            _LOGGER.error("Update failed: %s" % e)


    async def async_deep_update(self):
        """Send update request to car.

        This should not be called more than every 20 minutes.
        """
        try:
            nextdeepupdate = self._lastdeepupdate + 60 * 20

            if (int(time.time()) > nextdeepupdate):
                await self._wrapper.apiPostCall(self._battery_url)
                _LOGGER.debug("Deep update succeeded")
        except RenaultZEServiceException as e:
                _LOGGER.warning("Deep update failed: %s" % e)

_LOGGER = logger()

async def async_setup_platform():
    """Setup the sensor platform."""
    wrapper = RenaultZEService('temp_token.json',
                               credentials['ZEServicesUsername'],
                               credentials['ZEServicesPassword'])
    # Check we can get a token
    token = await wrapper.getAccessToken()

    device = RenaultZESensor(wrapper,
                             vin,
                             'Zoe')
    await device.async_update()
    print("%s: %s%s %s" % (device.name, device.state, device.unit_of_measurement, device.device_state_attributes))

loop = asyncio.get_event_loop()
buffer = loop.run_until_complete(async_setup_platform())
loop.close()
