"""Base classes for Renault entities."""
from typing import Any, Dict

from renault_api.kamereon.models import (
    KamereonVehicleBatteryStatusData,
    KamereonVehicleChargeModeData,
    KamereonVehicleCockpitData,
    KamereonVehicleHvacStatusData,
    KamereonVehicleLocationData,
)

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .renault_vehicle import RenaultVehicleProxy

ATTR_LAST_UPDATE = "last_update"


class RenaultDataEntity(CoordinatorEntity, Entity):
    """Implementation of a Renault entity with a data coordinator."""

    def __init__(
        self, vehicle: RenaultVehicleProxy, entity_type: str, coordinator_key: str
    ) -> None:
        """Initialise entity."""
        super().__init__(vehicle.coordinators[coordinator_key])
        self.vehicle = vehicle
        self._entity_type = entity_type

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return a device description for device registry."""
        return self.vehicle.device_info

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return slugify(f"{self.vehicle.details.vin}-{self._entity_type}")

    @property
    def name(self) -> str:
        """Return the name of this entity."""
        return f"{self.vehicle.details.vin}-{self._entity_type}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Data can succeed, but be empty
        return self.coordinator.last_update_success and self.coordinator.data


class RenaultBatteryDataEntity(RenaultDataEntity):
    """Implementation of a Renault entity with battery coordinator."""

    def __init__(self, vehicle: RenaultVehicleProxy, entity_type: str) -> None:
        """Initialise entity."""
        super().__init__(vehicle, entity_type, "battery")

    @property
    def data(self) -> KamereonVehicleBatteryStatusData:  # for type hints
        """Return collected data."""
        return self.coordinator.data

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes of this entity."""
        attrs = {}
        if self.data.timestamp:
            attrs[ATTR_LAST_UPDATE] = self.data.timestamp
        return attrs


class RenaultChargeModeDataEntity(RenaultDataEntity):
    """Implementation of a Renault entity with charge_mode coordinator."""

    def __init__(self, vehicle: RenaultVehicleProxy, entity_type: str) -> None:
        """Initialise entity."""
        super().__init__(vehicle, entity_type, "charge_mode")

    @property
    def data(self) -> KamereonVehicleChargeModeData:  # for type hints
        """Return collected data."""
        return self.coordinator.data


class RenaultHVACDataEntity(RenaultDataEntity):
    """Implementation of a Renault entity with hvac_status coordinator."""

    def __init__(self, vehicle: RenaultVehicleProxy, entity_type: str) -> None:
        """Initialise entity."""
        super().__init__(vehicle, entity_type, "hvac_status")

    @property
    def data(self) -> KamereonVehicleHvacStatusData:  # for type hints
        """Return collected data."""
        return self.coordinator.data


class RenaultLocationDataEntity(RenaultDataEntity):
    """Implementation of a Renault entity with location coordinator."""

    def __init__(self, vehicle: RenaultVehicleProxy, entity_type: str) -> None:
        """Initialise entity."""
        super().__init__(vehicle, entity_type, "location")

    @property
    def data(self) -> KamereonVehicleLocationData:  # for type hints
        """Return collected data."""
        return self.coordinator.data

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        """Return the device state attributes."""
        attrs = {}
        if self.data.lastUpdateTime:
            attrs[ATTR_LAST_UPDATE] = self.data.lastUpdateTime
        return attrs


class RenaultCockpitDataEntity(RenaultDataEntity):
    """Implementation of a Renault entity with cockpit coordinator."""

    def __init__(self, vehicle: RenaultVehicleProxy, entity_type: str) -> None:
        """Initialise entity."""
        super().__init__(vehicle, entity_type, "cockpit")

    @property
    def data(self) -> KamereonVehicleCockpitData:  # for type hints
        """Return collected data."""
        return self.coordinator.data
