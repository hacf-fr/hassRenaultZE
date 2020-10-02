"""Support for Renault sensors."""
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN
from .pyzeproxy import PyzeProxy
from .pyzevehicleproxy import PyzeVehicleProxy
from .renaultentity import RenaultBatteryDataEntity

LOGGER = logging.getLogger(__name__)


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
    entities.append(RenaultPluggedInSensor(vehicle_proxy, "Plugged In"))
    entities.append(RenaultChargingSensor(vehicle_proxy, "Charging"))
    return entities


class RenaultPluggedInSensor(RenaultBatteryDataEntity, BinarySensorEntity):
    """Plugged In sensor."""

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.coordinator.data.get("plugStatus") == 1

    @property
    def icon(self):
        """Icon handling."""
        if self.is_on:
            return "mdi:power-plug"
        return "mdi:power-plug-off"


class RenaultChargingSensor(RenaultBatteryDataEntity, BinarySensorEntity):
    """Charging sensor."""

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.coordinator.data.get("chargingStatus") == 1

    @property
    def icon(self):
        """Icon handling."""
        if self.is_on:
            return "mdi:flash"
        return "mdi:flash-off"
