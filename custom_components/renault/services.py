"""Support for Renault services."""
import logging
from typing import Dict

from pyze.api import ChargeMode
import requests
import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN, REGEX_VIN
from .pyzevehicleproxy import PyzeVehicleProxy

_LOGGER = logging.getLogger(__name__)

RENAULT_SERVICES = "renault_services"

SCHEMA_CHARGE_MODE = "charge_mode"
SCHEMA_SCHEDULES = "schedules"
SCHEMA_TEMPERATURE = "temperature"
SCHEMA_VIN = "vin"
SCHEMA_WHEN = "when"

SERVICE_AC_CANCEL = "ac_cancel"
SERVICE_AC_CANCEL_SCHEMA = vol.Schema(
    {
        vol.Required(SCHEMA_VIN): cv.matches_regex(REGEX_VIN),
    }
)
SERVICE_AC_START = "ac_start"
SERVICE_AC_START_SCHEMA = vol.Schema(
    {
        vol.Required(SCHEMA_VIN): cv.matches_regex(REGEX_VIN),
        vol.Optional(SCHEMA_WHEN): cv.datetime,
        vol.Optional(SCHEMA_TEMPERATURE): cv.positive_int,
    }
)
SERVICE_CHARGE_SET_MODE = "charge_set_mode"
SERVICE_CHARGE_SET_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(SCHEMA_VIN): cv.matches_regex(REGEX_VIN),
        vol.Required(SCHEMA_CHARGE_MODE): cv.enum(ChargeMode),
    }
)
SERVICE_CHARGE_SET_SCHEDULES = "charge_set_schedules"
SERVICE_CHARGE_SET_SCHEDULES_SCHEMA = vol.Schema(
    {
        vol.Required(SCHEMA_VIN): cv.matches_regex(REGEX_VIN),
        vol.Required(SCHEMA_SCHEDULES): dict,
    }
)
SERVICE_CHARGE_START = "charge_start"
SERVICE_CHARGE_START_SCHEMA = vol.Schema(
    {
        vol.Required(SCHEMA_VIN): cv.matches_regex(REGEX_VIN),
    }
)


async def async_setup_services(hass: HomeAssistantType):
    """Register the Renault services."""
    _LOGGER.debug("Registering renault services")

    if hass.data.get(RENAULT_SERVICES, False):
        return

    hass.data[RENAULT_SERVICES] = True

    async def ac_start(service_call: Dict):
        """Start A/C."""
        try:
            when = service_call.data.get(SCHEMA_WHEN, None)
            temperature = service_call.data.get(SCHEMA_TEMPERATURE, 21)
            _LOGGER.debug("A/C start attempt: %s / %s", when, temperature)
            pyze_vehicle = get_pyze_vehicle(service_call.data)
            jsonresult = await pyze_vehicle.send_ac_start(when, temperature)
            _LOGGER.info("A/C start result: %s", jsonresult)
        except requests.exceptions.RequestException as err:
            _LOGGER.error("A/C start failed: %s", err)

    async def ac_cancel(service_call: Dict):
        """Cancel A/C."""
        try:
            _LOGGER.debug("A/C cancel attempt.")
            pyze_vehicle = get_pyze_vehicle(service_call.data)
            jsonresult = await pyze_vehicle.send_cancel_ac()
            _LOGGER.info("A/C cancel result: %s", jsonresult)
        except requests.exceptions.RequestException as err:
            _LOGGER.error("A/C cancel failed: %s", err)

    async def charge_set_mode(service_call: Dict):
        """Set charge mode."""
        # self, charge_mode):
        try:
            charge_mode = service_call.data.get(SCHEMA_CHARGE_MODE)
            _LOGGER.debug("Charge set mode attempt: %s", charge_mode)
            pyze_vehicle = get_pyze_vehicle(service_call.data)
            jsonresult = await pyze_vehicle.send_set_charge_mode(charge_mode)
            _LOGGER.info("Charge set mode result: %s", jsonresult)
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Charge set mode failed: %s", err)

    async def charge_start(service_call: Dict):
        """Start charge."""
        try:
            _LOGGER.debug("Charge start attempt.")
            pyze_vehicle = get_pyze_vehicle(service_call.data)
            jsonresult = await pyze_vehicle.send_charge_start()
            _LOGGER.info("Charge start result: %s", jsonresult)
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Charge start failed: %s", err)

    async def charge_set_schedules(service_call: Dict):
        """Set charge schedules."""
        # self, schedules
        try:
            schedules = service_call.data.get(SCHEMA_SCHEDULES)
            _LOGGER.debug("Charge set schedules attempt: %s", schedules)
            pyze_vehicle = get_pyze_vehicle(service_call.data)
            charge_schedules = await pyze_vehicle.get_charge_schedules()
            charge_schedules.update(schedules)

            jsonresult = await pyze_vehicle.send_set_charge_schedules(charge_schedules)
            _LOGGER.info("Charge set schedules result: %s", jsonresult)
            _LOGGER.info(
                "It may take some time before these changes are reflected in your vehicle."
            )
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Charge set schedules failed: %s", err)

    def get_pyze_vehicle(service_call_data: Dict) -> PyzeVehicleProxy:
        """Get pyze_vehicle from service_call data."""
        vin = service_call_data[SCHEMA_VIN]
        for proxy in hass.data[DOMAIN].values():
            pyze_vehicle = proxy.get_vehicle_from_vin(vin)
            if pyze_vehicle is not None:
                return pyze_vehicle
        raise ValueError(f"Unable to load pyze vehicle with VIN: {vin}")

    hass.services.async_register(
        DOMAIN,
        SERVICE_AC_START,
        ac_start,
        schema=SERVICE_AC_START_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_AC_CANCEL,
        ac_cancel,
        schema=SERVICE_AC_CANCEL_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CHARGE_START,
        charge_start,
        schema=SERVICE_CHARGE_START_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CHARGE_SET_MODE,
        charge_set_mode,
        schema=SERVICE_CHARGE_SET_MODE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CHARGE_SET_SCHEDULES,
        charge_set_schedules,
        schema=SERVICE_CHARGE_SET_SCHEDULES_SCHEMA,
    )


async def async_unload_services(hass: HomeAssistantType):
    """Unload Renault services."""
    if not hass.data.get(RENAULT_SERVICES):
        return

    hass.data[RENAULT_SERVICES] = False

    hass.services.async_remove(DOMAIN, SERVICE_AC_CANCEL)
    hass.services.async_remove(DOMAIN, SERVICE_AC_START)
    hass.services.async_remove(DOMAIN, SERVICE_CHARGE_SET_MODE)
    hass.services.async_remove(DOMAIN, SERVICE_CHARGE_SET_SCHEDULES)
    hass.services.async_remove(DOMAIN, SERVICE_CHARGE_START)
