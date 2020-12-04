"""Device tracker for Renault vehicles."""
from typing import List, Optional

from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN
from .renault_hub import RenaultHub
from .renault_vehicle import RenaultVehicleProxy
from .renault_entities import RenaultDataEntity, RenaultLocationDataEntity


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
    if "location" in vehicle.coordinators:
        entities.append(RenaultLocationSensor(vehicle, "Location"))
    return entities


class RenaultLocationSensor(RenaultLocationDataEntity, TrackerEntity):
    """Location sensor."""

    @property
    def icon(self) -> str:
        """Icon handling."""
        return "mdi:car"

    @property
    def latitude(self) -> Optional[float]:
        """Return latitude value of the device."""
        return self.data.gpsLatitude

    @property
    def longitude(self) -> Optional[float]:
        """Return longitude value of the device."""
        return self.data.gpsLongitude

    @property
    def source_type(self) -> str:
        """Return the source type of the device."""
        return SOURCE_TYPE_GPS
