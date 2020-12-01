"""Support for Renault sensors."""
import logging
from typing import List, Optional

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_PLUG,
    DEVICE_CLASS_BATTERY_CHARGING,
    BinarySensorEntity,
)
from renault_api.kamereon.enums import ChargeState, PlugState

from .const import DOMAIN
from .renault_hub import RenaultHub
from .renault_vehicle import RenaultVehicleProxy
from .renault_entities import RenaultBatteryDataEntity, RenaultDataEntity

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Renault entities from config entry."""
    proxy: RenaultHub = hass.data[DOMAIN][config_entry.unique_id]
    entities: List[RenaultDataEntity] = await get_entities(proxy)
    proxy.entities.extend(entities)
    async_add_entities(entities)


async def get_entities(proxy: RenaultHub) -> List[RenaultDataEntity]:
    """Create Renault entities for all vehicles."""
    entities: List[RenaultDataEntity] = []
    for vehicle_link in proxy.get_vehicle_links():
        vehicle_proxy = await proxy.get_vehicle(vehicle_link)
        entities.extend(await get_vehicle_entities(vehicle_proxy))
    return entities


async def get_vehicle_entities(
    vehicle_proxy: RenaultVehicleProxy,
) -> List[RenaultDataEntity]:
    """Create Renault entities for single vehicle."""
    entities: List[RenaultDataEntity] = []
    if "battery" in vehicle_proxy.coordinators:
        entities.append(RenaultPluggedInSensor(vehicle_proxy, "Plugged In"))
        entities.append(RenaultChargingSensor(vehicle_proxy, "Charging"))
    return entities


class RenaultPluggedInSensor(RenaultBatteryDataEntity, BinarySensorEntity):
    """Plugged In sensor."""

    @property
    def is_on(self) -> Optional[bool]:
        """Return true if the binary sensor is on."""
        return (
            self.data.get_plug_status() == PlugState.PLUGGED
            if self.data.plugStatus is not None
            else None
        )

    @property
    def icon(self) -> str:
        """Icon handling."""
        if self.is_on:
            return "mdi:power-plug"
        return "mdi:power-plug-off"

    @property
    def device_class(self) -> str:
        """Returning binary sensor device class"""
        return DEVICE_CLASS_PLUG


class RenaultChargingSensor(RenaultBatteryDataEntity, BinarySensorEntity):
    """Charging sensor."""

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return (
            self.data.get_charging_status() == ChargeState.CHARGE_IN_PROGRESS
            if self.data.chargingStatus is not None
            else None
        )

    @property
    def icon(self) -> str:
        """Icon handling."""
        if self.is_on:
            return "mdi:flash"
        return "mdi:flash-off"

    @property
    def device_class(self) -> str:
        """Returning binary sensor device class"""
        return DEVICE_CLASS_BATTERY_CHARGING
