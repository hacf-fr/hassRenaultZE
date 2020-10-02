"""Support for Renault sensors."""
import logging
from typing import List

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from .const import DOMAIN
from .pyzeproxy import PyzeProxy
from .pyzevehicleproxy import PyzeVehicleProxy
from .renaultentity import RenaultHVACDataEntity

ATTR_HVAC_STATUS = "hvac_status"

LOGGER = logging.getLogger(__name__)

SUPPORT_HVAC = [HVAC_MODE_HEAT_COOL, HVAC_MODE_OFF]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way of setting up platforms."""


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Renault entities from config entry."""
    proxy = hass.data[DOMAIN][config_entry.unique_id]
    entities = await get_entities(hass, proxy)
    proxy.entities.extend(entities)
    async_add_entities(entities, True)


async def get_entities(hass, proxy: PyzeProxy):
    """Create Renault entities for all vehicles."""
    entities = []
    for vehicle_link in proxy.get_vehicle_links():
        vehicle_proxy = await proxy.get_vehicle_proxy(vehicle_link)
        entities.extend(await get_vehicle_entities(hass, vehicle_proxy))
    return entities


async def get_vehicle_entities(hass, vehicle_proxy: PyzeVehicleProxy):
    """Create Renault entities for single vehicle."""
    entities = []
    entities.append(RenaultHVACController(vehicle_proxy, "HVAC"))
    return entities


class RenaultHVACController(RenaultHVACDataEntity, ClimateEntity):
    """HVAC controller."""

    @property
    def hvac_mode(self) -> str:
        """Return hvac current operation mode."""
        data = self.coordinator.data
        if "hvacStatus" in data:
            if data["hvacStatus"] == "off":
                return HVAC_MODE_OFF
            return HVAC_MODE_HEAT_COOL
        return None

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return SUPPORT_HVAC

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature.

        Not available for this platform.
        """
        return None

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.proxy.hvac_target_temperature

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature:
            LOGGER.debug("%s: Setting temperature to %s", self.name, temperature)
            self.proxy.hvac_target_temperature = temperature

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        LOGGER.debug("%s: Setting hvac mode to %s", self.name, hvac_mode)
        if hvac_mode == HVAC_MODE_OFF:
            await self.proxy.send_cancel_ac()
        elif hvac_mode == HVAC_MODE_HEAT_COOL:
            await self.proxy.send_ac_start(None, self.proxy.hvac_target_temperature)
