"""Support for MyRenault services."""

import asyncio
import logging
import time
import json
import aiohttp
import traceback
from datetime import datetime, timedelta
from pyze.api import Gigya, Kamereon, Vehicle, CredentialStore

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
ATTR_BATTERY_TEMPERATURE = 'battery_temperature'
ATTR_MILEAGE = 'mileage'

CONF_VIN = 'vin'
CONF_ANDROID_LNG = 'android_lng'
CONF_K_ACCOUNTID = 'k_account_id'

SCAN_INTERVAL = timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_VIN): cv.string,
    vol.Optional(CONF_ANDROID_LNG, default='fr_FR'): cv.string,
    vol.Optional(CONF_NAME, default=None): cv.string,
    vol.Optional(CONF_K_ACCOUNTID, default=''): cv.string,
})


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Setup the sensor platform."""
    _LOGGER.debug("Initialising renaultze platform")
    
    g_url = None
    g_key = None
    k_url = None
    k_key = None
    k_account_id = config.get(CONF_K_ACCOUNTID, '')

    cred = CredentialStore()
    cred.clear()

    url = 'https://renault-wrd-prod-1-euw1-myrapp-one.s3-eu-west-1.amazonaws.com/configuration/android/config_%s.json' % config.get(CONF_ANDROID_LNG)
    async with aiohttp.ClientSession(
            ) as session:
        async with session.get(url) as response:
            responsetext = await response.text()
            if responsetext == '':
                responsetext = '{}'
            jsonresponse = json.loads(responsetext)
            
            g_url = jsonresponse['servers']['gigyaProd']['target']
            g_key = jsonresponse['servers']['gigyaProd']['apikey']
            k_url = jsonresponse['servers']['wiredProd']['target']
            k_key = jsonresponse['servers']['wiredProd']['apikey']

    g = Gigya(api_key=g_key,root_url=g_url)
    if not g.login(config.get(CONF_USERNAME),
                          config.get(CONF_PASSWORD)):
        raise RenaultZEError("Login failed")
    g.account_info()
    
    k = Kamereon(api_key=k_key,root_url=k_url,gigya=g)
    if k_account_id != '':
        k.set_account_id(k_account_id)

    v = Vehicle(config.get(CONF_VIN), k)

    devices = [
        RenaultZESensor(v,
                        config.get(CONF_NAME, config.get(CONF_VIN))
                        )
        ]
    async_add_entities(devices)


class RenaultZESensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, vehicle, name):
        """Initialize the sensor."""
        _LOGGER.debug("Initialising RenaultZESensor %s" % name)
        self._state = None
        self._vehicle = vehicle
        self._name = name
        self._attrs = {}
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

    def process_battery_response(self, jsonresult):
        """Update new state data for the sensor."""
        self._state = jsonresult['batteryLevel']

        if 'chargeStatus' in jsonresult:
            self._attrs[ATTR_CHARGING] = jsonresult['chargeStatus'] > 0
        if 'lastUpdateTime' in jsonresult:
            self._attrs[ATTR_LAST_UPDATE] = jsonresult['lastUpdateTime']
        if 'plugStatus' in jsonresult:
            self._attrs[ATTR_PLUGGED] = jsonresult['plugStatus'] > 0
        if 'batteryTemperature' in jsonresult:
            self._attrs[ATTR_BATTERY_TEMPERATURE] = jsonresult['batteryTemperature']
        if 'rangeHvacOff' in jsonresult:
            self._attrs[ATTR_REMAINING_RANGE] = jsonresult['rangeHvacOff']

    def process_mileage_response(self, jsonresult):
        """Update new state data for the sensor."""
        if 'totalMileage' in jsonresult:
            self._attrs[ATTR_MILEAGE] = jsonresult['totalMileage']

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # Run standard update
        try:
            jsonresult = self._vehicle.battery_status()
            _LOGGER.debug("Battery update result: %s" % jsonresult)
            self.process_battery_response(jsonresult)
        except Exception as e:
            _LOGGER.warning("Battery update failed: %s" % traceback.format_exc())

        try:
            jsonresult =  self._vehicle.mileage()
            _LOGGER.debug("Mileage update result: %s" % jsonresult)
            self.process_mileage_response(jsonresult)
        except Exception as e:
            _LOGGER.warning("Mileage update failed: %s" % traceback.format_exc())

class RenaultZEError(Exception):
    pass