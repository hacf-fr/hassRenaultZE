"""Support for Renault services."""
import logging
from typing import Any, Dict

from renault_api.kamereon.enums import ChargeMode
from renault_api.kamereon.exceptions import KamereonResponseException
import requests
import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN, REGEX_VIN
from .renault_hub import RenaultHub
from .renault_vehicle import RenaultVehicleProxy

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
        vol.Required(SCHEMA_CHARGE_MODE): cv.string,
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


async def async_setup_services(hass: HomeAssistantType) -> None:
    """Register the Renault services."""
    _LOGGER.debug("Registering renault services")

    if hass.data.get(RENAULT_SERVICES, False):
        return

    hass.data[RENAULT_SERVICES] = True

    async def ac_start(service_call) -> None:
        """Start A/C."""
        service_call_data: Dict[str, Any] = service_call.data
        when = service_call_data.get(SCHEMA_WHEN, None)
        temperature = service_call_data.get(SCHEMA_TEMPERATURE, 21)
        vehicle = get_vehicle(service_call_data)
        _LOGGER.debug("A/C start attempt: %s / %s", when, temperature)
        try:
            result = await vehicle.send_ac_start(temperature=temperature, when=when)
        except KamereonResponseException as err:
            _LOGGER.error("A/C start failed: %s", err)
        else:
            _LOGGER.info("A/C start result: %s", result.raw_data)

    async def ac_cancel(service_call) -> None:
        """Cancel A/C."""
        service_call_data: Dict[str, Any] = service_call.data
        vehicle = get_vehicle(service_call_data)
        _LOGGER.debug("A/C cancel attempt.")
        try:
            result = await vehicle.send_cancel_ac()
        except KamereonResponseException as err:
            _LOGGER.error("A/C cancel failed: %s", err)
        else:
            _LOGGER.info("A/C cancel result: %s", result)

    async def charge_set_mode(service_call) -> None:
        """Set charge mode."""
        service_call_data: Dict[str, Any] = service_call.data
        charge_mode: str = service_call_data[SCHEMA_CHARGE_MODE]
        vehicle = get_vehicle(service_call_data)
        _LOGGER.debug("Charge set mode attempt: %s", charge_mode)
        try:
            # there was some confusion in earlier release regarding upper or lower case of charge-mode
            # so forcing to lower manually for the custom-component (always or always_charging or schedule_mode)
            result = await vehicle.send_set_charge_mode(ChargeMode(charge_mode.lower()))
        except KamereonResponseException as err:
            _LOGGER.error("Charge set mode failed: %s", err)
        else:
            _LOGGER.info("Charge set mode result: %s", result)

    async def charge_start(service_call) -> None:
        """Start charge."""
        service_call_data: Dict[str, Any] = service_call.data
        vehicle = get_vehicle(service_call_data)
        _LOGGER.debug("Charge start attempt.")
        try:
            result = await vehicle.send_charge_start()
        except KamereonResponseException as err:
            _LOGGER.error("Charge start failed: %s", err)
        else:
            _LOGGER.info("Charge start result: %s", result)

    async def charge_set_schedules(service_call) -> None:
        """Set charge schedules."""
        service_call_data: Dict[str, Any] = service_call.data
        schedules = service_call_data.get(SCHEMA_SCHEDULES)
        vehicle = get_vehicle(service_call_data)
        charge_schedules = await vehicle.get_charging_settings()
        charge_schedules.update(schedules)
        try:
            _LOGGER.debug("Charge set schedules attempt: %s", schedules)
            result = await vehicle.send_set_charge_schedules(charge_schedules)
        except KamereonResponseException as err:
            _LOGGER.error("Charge set schedules failed: %s", err)
        else:
            _LOGGER.info("Charge set schedules result: %s", result)
            _LOGGER.info(
                "It may take some time before these changes are reflected in your vehicle."
            )

    def get_vehicle(service_call_data: Dict[str, Any]) -> RenaultVehicleProxy:
        """Get vehicle from service_call data."""
        vin: str = service_call_data[SCHEMA_VIN]
        proxy: RenaultHub
        for proxy in hass.data[DOMAIN].values():
            # there was some confusion in earlier release regarding upper or lower case of vin
            # so forcing to upper manually for the custom-component
            vehicle = proxy.vehicles.get(vin.upper())
            if vehicle is not None:
                return vehicle
        raise ValueError(f"Unable to find vehicle with VIN: {vin}")

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


async def async_unload_services(hass: HomeAssistantType) -> None:
    """Unload Renault services."""
    if not hass.data.get(RENAULT_SERVICES):
        return

    hass.data[RENAULT_SERVICES] = False

    hass.services.async_remove(DOMAIN, SERVICE_AC_CANCEL)
    hass.services.async_remove(DOMAIN, SERVICE_AC_START)
    hass.services.async_remove(DOMAIN, SERVICE_CHARGE_SET_MODE)
    hass.services.async_remove(DOMAIN, SERVICE_CHARGE_SET_SCHEDULES)
    hass.services.async_remove(DOMAIN, SERVICE_CHARGE_START)
