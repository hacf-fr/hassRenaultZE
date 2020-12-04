"""Support for Renault sensors."""
import logging
from typing import List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN
from .renault_hub import RenaultHub
from .renault_vehicle import RenaultVehicleProxy
from .renault_entities import RenaultDataEntity, RenaultHVACDataEntity

ATTR_HVAC_STATUS = "hvac_status"

LOGGER = logging.getLogger(__name__)

SUPPORT_HVAC = [HVAC_MODE_HEAT_COOL, HVAC_MODE_OFF]


async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the Renault entities from config entry."""
    proxy: RenaultHub = hass.data[DOMAIN][config_entry.unique_id]
    entities: List[RenaultDataEntity] = await get_entities(proxy)
    async_add_entities(entities)


async def get_entities(proxy: RenaultHub) -> List[RenaultDataEntity]:
    """Create Renault entities for all vehicles."""
    entities: List[RenaultDataEntity] = []
    for vehicle in proxy.vehicles.values():
        entities.extend(await get_vehicle_entities(vehicle))
    return entities


async def get_vehicle_entities(vehicle: RenaultVehicleProxy) -> List[RenaultDataEntity]:
    """Create Renault entities for single vehicle."""
    entities: List[RenaultDataEntity] = []
    if "hvac_status" in vehicle.coordinators:
        entities.append(RenaultHVACController(vehicle, "HVAC"))
    return entities


class RenaultHVACController(RenaultHVACDataEntity, ClimateEntity):
    """HVAC controller."""

    @property
    def hvac_mode(self) -> Optional[str]:
        """Return hvac current operation mode."""
        if self.data.hvacStatus is None:
            return None
        if self.data.hvacStatus == "off":
            return HVAC_MODE_OFF
        return HVAC_MODE_HEAT_COOL

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
    def target_temperature(self) -> int:
        """Return the temperature we try to reach."""
        return self.vehicle.hvac_target_temperature

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperatures."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature:
            LOGGER.debug("%s: Setting temperature to %s", self.name, temperature)
            self.vehicle.hvac_target_temperature = temperature

    async def async_set_hvac_mode(self, hvac_mode) -> None:
        """Set new target hvac mode."""
        LOGGER.debug("%s: Setting hvac mode to %s", self.name, hvac_mode)
        if hvac_mode == HVAC_MODE_OFF:
            await self.vehicle.send_cancel_ac()
        elif hvac_mode == HVAC_MODE_HEAT_COOL:
            await self.vehicle.send_ac_start(self.vehicle.hvac_target_temperature)
