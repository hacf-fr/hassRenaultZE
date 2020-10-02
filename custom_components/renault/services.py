"""Support for Renault services."""
import logging

from pyze.api import ChargeMode
import requests
import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, REGEX_VIN
from .pyzevehicleproxy import PyzeVehicleProxy

LOGGER = logging.getLogger(__name__)

RENAULT_SERVICES = "renault_services"

SCHEMA_CHARGE_MODE = "charge_mode"
SCHEMA_SCHEDULES = "schedules"
SCHEMA_TEMPERATURE = "temperature"
SCHEMA_VIN = "vin"
SCHEMA_WHEN = "when"

SERVICE_AC_CANCEL = "ac_cancel"
SERVICE_AC_CANCEL_SCHEMA = {
    vol.Required(SCHEMA_VIN): cv.matches_regex(REGEX_VIN),
}
SERVICE_AC_START = "ac_start"
SERVICE_AC_START_SCHEMA = {
    vol.Required(SCHEMA_VIN): cv.matches_regex(REGEX_VIN),
    vol.Optional(SCHEMA_WHEN): cv.datetime,
    vol.Optional(SCHEMA_TEMPERATURE): cv.positive_int,
}
SERVICE_CHARGE_SET_MODE = "charge_set_mode"
SERVICE_CHARGE_SET_MODE_SCHEMA = {
    vol.Required(SCHEMA_VIN): cv.matches_regex(REGEX_VIN),
    vol.Required(SCHEMA_CHARGE_MODE): cv.enum(ChargeMode),
}
SERVICE_CHARGE_SET_SCHEDULES = "charge_set_schedules"
SERVICE_CHARGE_SET_SCHEDULES_SCHEMA = {
    vol.Required(SCHEMA_VIN): cv.matches_regex(REGEX_VIN),
    vol.Required(SCHEMA_SCHEDULES): dict,
}
SERVICE_CHARGE_START = "charge_start"
SERVICE_CHARGE_START_SCHEMA = {
    vol.Required(SCHEMA_VIN): cv.matches_regex(REGEX_VIN),
}


async def async_setup_services(hass):
    """Register the Renault services."""
    LOGGER.debug("Registering renault services")

    if hass.data.get(RENAULT_SERVICES, False):
        return

    hass.data[RENAULT_SERVICES] = True

    async def call_renault_service(service_call):
        """Call correct Renault service."""
        service = service_call.service

        if service == SERVICE_AC_CANCEL:
            await ac_cancel(hass, service_call)
        elif service == SERVICE_AC_START:
            await ac_start(hass, service_call)
        elif service == SERVICE_CHARGE_SET_MODE:
            await charge_set_mode(hass, service_call)
        elif service == SERVICE_CHARGE_SET_SCHEDULES:
            await charge_set_schedules(hass, service_call)
        elif service == SERVICE_CHARGE_START:
            await charge_start(hass, service_call)

    hass.services.async_register(
        DOMAIN,
        SERVICE_AC_START,
        call_renault_service,
        schema=SERVICE_AC_START_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_AC_CANCEL,
        call_renault_service,
        schema=SERVICE_AC_CANCEL_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CHARGE_START,
        call_renault_service,
        schema=SERVICE_CHARGE_START_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CHARGE_SET_MODE,
        call_renault_service,
        schema=SERVICE_CHARGE_SET_MODE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CHARGE_SET_SCHEDULES,
        call_renault_service,
        schema=SERVICE_CHARGE_SET_SCHEDULES_SCHEMA,
    )


async def async_unload_services(hass):
    """Unload Renault services."""
    if not hass.data.get(RENAULT_SERVICES):
        return

    hass.data[RENAULT_SERVICES] = False

    hass.services.async_remove(DOMAIN, SERVICE_AC_CANCEL)
    hass.services.async_remove(DOMAIN, SERVICE_AC_START)
    hass.services.async_remove(DOMAIN, SERVICE_CHARGE_SET_MODE)
    hass.services.async_remove(DOMAIN, SERVICE_CHARGE_SET_SCHEDULES)
    hass.services.async_remove(DOMAIN, SERVICE_CHARGE_START)


async def ac_start(hass, service_call):
    """Start A/C."""
    try:
        LOGGER.debug("ac_start: %s", service_call)
        pyze_vehicle = await get_pyze_vehicle(hass, service_call.data)
        when = service_call.data.get(SCHEMA_WHEN, None)
        temperature = service_call.data.get(SCHEMA_TEMPERATURE, 21)
        LOGGER.debug("A/C start attempt: %s / %s", when, temperature)
        jsonresult = await pyze_vehicle.send_ac_start(when, temperature)
        LOGGER.info("A/C start result: %s", jsonresult)
    except requests.exceptions.RequestException as err:
        LOGGER.error("A/C start failed: %s", err)


async def ac_cancel(hass, service_call):
    """Cancel A/C."""
    try:
        pyze_vehicle = await get_pyze_vehicle(hass, service_call.data)
        LOGGER.debug("A/C cancel attempt.")
        jsonresult = await pyze_vehicle.send_cancel_ac()
        LOGGER.info("A/C cancel result: %s", jsonresult)
    except requests.exceptions.RequestException as err:
        LOGGER.error("A/C cancel failed: %s", err)


async def charge_set_mode(hass, service_call):
    """Set charge mode."""
    # self, charge_mode):
    try:
        pyze_vehicle = await get_pyze_vehicle(hass, service_call.data)
        charge_mode = service_call.data.get(SCHEMA_CHARGE_MODE)
        LOGGER.debug("Charge set mode attempt: %s", charge_mode)
        jsonresult = await pyze_vehicle.send_set_charge_mode(charge_mode)
        LOGGER.info("Charge set mode result: %s", jsonresult)
    except requests.exceptions.RequestException as err:
        LOGGER.error("Charge set mode failed: %s", err)


async def charge_start(hass, service_call):
    """Start charge."""
    try:
        pyze_vehicle = await get_pyze_vehicle(hass, service_call.data)
        LOGGER.debug("Charge start attempt.")
        jsonresult = await pyze_vehicle.send_charge_start()
        LOGGER.info("Charge start result: %s", jsonresult)
    except requests.exceptions.RequestException as err:
        LOGGER.error("Charge start failed: %s", err)


async def charge_set_schedules(hass, service_call):
    """Set charge schedules."""
    # self, schedules
    try:
        pyze_vehicle = await get_pyze_vehicle(hass, service_call.data)
        schedules = service_call.data.get(SCHEMA_SCHEDULES)
        LOGGER.debug("Charge set schedules attempt: %s", schedules)
        charge_schedules = await pyze_vehicle.get_charge_schedules()
        charge_schedules.update(schedules)

        jsonresult = await pyze_vehicle.send_set_charge_schedules(charge_schedules)
        LOGGER.info("Charge set schedules result: %s", jsonresult)
        LOGGER.info(
            "It may take some time before these changes are reflected in your vehicle."
        )
    except requests.exceptions.RequestException as err:
        LOGGER.error("Charge set schedules failed: %s", err)


async def get_pyze_vehicle(hass, service_call_data: dict) -> PyzeVehicleProxy:
    """Get pyze_vehicle from service_call data."""
    vin = service_call_data[SCHEMA_VIN]
    for proxy in hass.data[DOMAIN].values():
        pyze_vehicle = proxy.get_vehicle_from_vin(vin)
        if pyze_vehicle is not None:
            return pyze_vehicle
    raise ValueError(f"Unable to load pyze vehicle with VIN: {vin}")
