"""Device tracker for Renault vehicles."""
import logging

from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity

from .const import DOMAIN, MODEL_SUPPORTS_LOCATION
from .pyzeproxy import PyzeProxy
from .pyzevehicleproxy import PyzeVehicleProxy
from .renaultentity import RenaultLocationDataEntity

LOGGER = logging.getLogger(__name__)


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
        model_code = vehicle_link["vehicleDetails"]["model"]["code"]
        if model_code in MODEL_SUPPORTS_LOCATION:
            vehicle_proxy = await proxy.get_vehicle_proxy(vehicle_link)
            entities.extend(await get_vehicle_entities(hass, vehicle_proxy))
        else:
            LOGGER.warning("Model code %s does not support location.", model_code)
    return entities


async def get_vehicle_entities(hass, vehicle_proxy: PyzeVehicleProxy):
    """Create Renault entities for single vehicle."""
    entities = []
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
        data = self.coordinator.data
        if "gpsLatitude" in data:
            return data["gpsLatitude"]
        LOGGER.warning("gpsLatitude not available in coordinator data %s", data)

    @property
    def longitude(self) -> float:
        """Return longitude value of the device."""
        data = self.coordinator.data
        if "gpsLongitude" in data:
            return data["gpsLongitude"]
        LOGGER.warning("gpsLongitude not available in coordinator data %s", data)

    @property
    def source_type(self):
        """Return the source type of the device."""
        return SOURCE_TYPE_GPS
