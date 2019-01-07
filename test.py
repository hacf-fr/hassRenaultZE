#!/usr/bin/env python3

import asyncio
import time
from datetime import datetime

# All the shared functions are in this package.
from custom_components.sensor.renaultzeservice.renaultzeservice import (
    RenaultZEService
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


class Entity():
    """Fake HASS Entity"""


class RenaultZESensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, wrapper, vin, name):
        """Initialize the sensor."""
        self._state = None
        self._wrapper = wrapper
        self._battery_url = '/api/vehicle/' + vin + '/battery'
        self._name = name
        self._attrs = {}
        self._attrs[ATTR_CHARGE_LEVEL] = None
        self._attrs[ATTR_CHARGING] = None
        self._attrs[ATTR_LAST_UPDATE] = None
        self._attrs[ATTR_PLUGGED] = None
        self._attrs[ATTR_REMAINING_RANGE] = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        textresult = await self._wrapper.apiGetCall(self._battery_url)
        jsonresult = json.loads(textresult)

        # Update attributes
        self._attrs[ATTR_CHARGE_LEVEL] = jsonresult[ATTR_CHARGE_LEVEL]
        self._attrs[ATTR_CHARGING] = jsonresult[ATTR_CHARGING]
        self._attrs[ATTR_LAST_UPDATE] = datetime.fromtimestamp(
            jsonresult[ATTR_LAST_UPDATE] / 1000
            ).isoformat()
        self._attrs[ATTR_PLUGGED] = jsonresult[ATTR_PLUGGED]
        self._attrs[ATTR_REMAINING_RANGE] = jsonresult[ATTR_REMAINING_RANGE]

        # Request server update if required
        await self.async_check_update_server(jsonresult)

    async def async_check_update_server(self, jsonresult):
        """Send update request to car.

        This should only be called if the car is charging,
        and the data was last updated more than 20 minutes ago.
        """
        if jsonresult[ATTR_CHARGING]:
            last_serverupdate = int(jsonresult[ATTR_LAST_UPDATE] / 1000)
            min_nextserverupdate = last_serverupdate + 60 * 20

            if (int(time.time()) > min_nextserverupdate):
                await self._wrapper.apiPostCall(self._battery_url)

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return self._attrs


async def async_setup_platform():
    """Setup the sensor platform."""
    wrapper = RenaultZEService('temp_token.json')
    await wrapper.getAccessToken(credentials['ZEServicesUsername'],
                                 credentials['ZEServicesPassword'])

    device = RenaultZESensor(wrapper,
                             vin,
                             'Zoe')
    await device.async_update()
    print(device.device_state_attributes)

loop = asyncio.get_event_loop()
buffer = loop.run_until_complete(async_setup_platform())
loop.close()
