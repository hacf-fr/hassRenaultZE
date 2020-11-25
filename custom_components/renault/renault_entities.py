"""Base classes for Renault entities."""
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify
from renault_api.model.kamereon import (
    KamereonVehicleBatteryStatusData,
    KamereonVehicleChargeModeData,
    KamereonVehicleCockpitData,
    KamereonVehicleHvacStatusData,
    KamereonVehicleLocationData,
)

from .renault_vehicle import RenaultVehicleProxy

ATTR_LAST_UPDATE = "last_update"


class RenaultDataEntity(CoordinatorEntity, Entity):
    """Implementation of a Renault entity with a data coordinator."""

    def __init__(
        self, proxy: RenaultVehicleProxy, entity_type: str, coordinator_key: str
    ):
        """Initialise entity."""
        super().__init__(proxy.coordinators[coordinator_key])
        self.proxy = proxy
        self._entity_type = entity_type

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self.proxy.device_info

    @property
    def unique_id(self):
        """Return a unique identifier for this entity."""
        return slugify(f"{self.proxy.vin}-{self._entity_type}")

    @property
    def name(self):
        """Return the name of this entity."""
        return f"{self.proxy.vin}-{self._entity_type}"


class RenaultBatteryDataEntity(RenaultDataEntity):
    """Implementation of a Renault entity with battery coordinator."""

    def __init__(self, proxy: RenaultVehicleProxy, entity_type: str):
        """Initialise entity."""
        super().__init__(proxy, entity_type, "battery")

    @property
    def data(self) -> KamereonVehicleBatteryStatusData:
        return self.coordinator.data

    @property
    def device_state_attributes(self):
        """Return the state attributes of this entity."""
        attrs = {}
        if "timestamp" in self.data.raw_data:
            attrs[ATTR_LAST_UPDATE] = self.data.raw_data["timestamp"]
        return attrs


class RenaultChargeModeDataEntity(RenaultDataEntity):
    """Implementation of a Renault entity with charge_mode coordinator."""

    def __init__(self, proxy: RenaultVehicleProxy, entity_type: str):
        """Initialise entity."""
        super().__init__(proxy, entity_type, "charge_mode")

    @property
    def data(self) -> KamereonVehicleChargeModeData:
        return self.coordinator.data


class RenaultHVACDataEntity(RenaultDataEntity):
    """Implementation of a Renault entity with hvac_status coordinator."""

    def __init__(self, proxy: RenaultVehicleProxy, entity_type: str):
        """Initialise entity."""
        super().__init__(proxy, entity_type, "hvac_status")

    @property
    def data(self) -> KamereonVehicleHvacStatusData:
        return self.coordinator.data


class RenaultLocationDataEntity(RenaultDataEntity):
    """Implementation of a Renault entity with location coordinator."""

    def __init__(self, proxy: RenaultVehicleProxy, entity_type: str):
        """Initialise entity."""
        super().__init__(proxy, entity_type, "location")

    @property
    def data(self) -> KamereonVehicleLocationData:
        return self.coordinator.data

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = {}
        if "lastUpdateTime" in self.data.raw_data:
            attrs[ATTR_LAST_UPDATE] = self.data.raw_data["lastUpdateTime"]
        return attrs


class RenaultMileageDataEntity(RenaultDataEntity):
    """Implementation of a Renault entity with mileage coordinator."""

    def __init__(self, proxy: RenaultVehicleProxy, entity_type: str):
        """Initialise entity."""
        super().__init__(proxy, entity_type, "mileage")

    @property
    def data(self) -> KamereonVehicleCockpitData:
        return self.coordinator.data
