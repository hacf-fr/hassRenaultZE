"""Support for Renault ZE services."""

import asyncio
import logging
from datetime import datetime
from .shared.renaultzeservice import RenaultZEService

import voluptuous as vol

from homeassistant.helpers.entity import Entity

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_NAME

_LOGGER = logging.getLogger(__name__)

ATTR_CHARGING = 'charging'
ATTR_PLUGGED = 'plugged'
ATTR_CHARGE_LEVEL = 'charge_level'
ATTR_REMAINING_RANGE = 'remaining_range'
ATTR_LAST_UPDATE = 'last_update'

CONF_VIN = 'vin'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_VIN): cv.string,
    vol.Optional(CONF_NAME, default=None): cv.string,
})


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Setup the sensor platform."""
    wrapper = RenaultZEService()
    await wrapper.getAccessToken(config.get(CONF_USERNAME),
                                 config.get(CONF_PASSWORD))

    devices = [
        RenaultZESensor(wrapper, 
                        config.get(CONF_VIN),
                        config.get(CONF_NAME, config.get(CONF_VIN))
                        )
        ]
    async_add_entities(devices)


class RenaultZESensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, wrapper, vin, name):
        """Initialize the sensor."""
        self._state = None
        self._wrapper = wrapper
        self._vin = vin
        self._name = name
        self._attrs = {}

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
        jsonresult = await self._wrapper.apiCall(
            '/api/vehicle/' + self._vin + '/battery'
            )
        self._attrs[ATTR_CHARGE_LEVEL] = jsonresult[ATTR_CHARGE_LEVEL]
        self._attrs[ATTR_CHARGING] = jsonresult[ATTR_CHARGING]
        self._attrs[ATTR_LAST_UPDATE] = datetime.fromtimestamp(jsonresult[ATTR_LAST_UPDATE] / 1000).isoformat()
        self._attrs[ATTR_PLUGGED] = jsonresult[ATTR_PLUGGED]
        self._attrs[ATTR_REMAINING_RANGE] = jsonresult[ATTR_REMAINING_RANGE]

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return self._attrs
