"""Device tracker for Renault vehicles."""
import logging
from typing import List

from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity

from .const import DOMAIN
from .renault_hub import RenaultHub
from .renault_vehicle import RenaultVehicleProxy
from .renault_entities import RenaultDataEntity, RenaultLocationDataEntity

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
    if "location" in vehicle_proxy.coordinators:
        entities.append(RenaultLocationSensor(vehicle_proxy, "Location"))
    return entities


class RenaultLocationSensor(RenaultLocationDataEntity, TrackerEntity):
    """Location sensor."""

    @property
    def icon(self):
        """Icon handling."""
        return "mdi:car"

    @property
    def latitude(self) -> float:
        """Return latitude value of the device."""
        # return self.data.gpsLatitude
        return self.data.gpsLatitude

    @property
    def longitude(self) -> float:
        """Return longitude value of the device."""
        # return self.data.gpsLongitude
        return self.data.gpsLongitude

    @property
    def source_type(self):
        """Return the source type of the device."""
        return SOURCE_TYPE_GPS
