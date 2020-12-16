"""Support for Renault sensors."""
from typing import Any, Dict, List, Optional

from renault_api.kamereon.enums import ChargeState, PlugState

from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_TEMPERATURE,
    LENGTH_KILOMETERS,
    LENGTH_MILES,
    PERCENTAGE,
    POWER_KILO_WATT,
    TEMP_CELSIUS,
    TIME_MINUTES,
    VOLUME_GALLONS,
    VOLUME_LITERS,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.icon import icon_for_battery_level
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import slugify
from homeassistant.util.unit_system import IMPERIAL_SYSTEM, METRIC_SYSTEM

from .const import (
    DOMAIN,
    DEVICE_CLASS_PLUG_STATE,
    DEVICE_CLASS_CHARGE_STATE,
    DEVICE_CLASS_CHARGE_MODE,
)
from .renault_entities import (
    RenaultBatteryDataEntity,
    RenaultChargeModeDataEntity,
    RenaultCockpitDataEntity,
    RenaultDataEntity,
    RenaultHVACDataEntity,
)
from .renault_hub import RenaultHub
from .renault_vehicle import RenaultVehicleProxy

ATTR_BATTERY_AVAILABLE_ENERGY = "battery_available_energy"


async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the Renault entities from config entry."""
    proxy: RenaultHub = hass.data[DOMAIN][config_entry.unique_id]
    entities = await get_entities(proxy)
    async_add_entities(entities)


async def get_entities(proxy: RenaultHub) -> List[RenaultDataEntity]:
    """Create Renault entities for all vehicles."""
    entities = []
    for vehicle in proxy.vehicles.values():
        entities.extend(await get_vehicle_entities(vehicle))
    return entities


async def get_vehicle_entities(vehicle: RenaultVehicleProxy) -> List[RenaultDataEntity]:
    """Create Renault entities for single vehicle."""
    entities = []
    if "cockpit" in vehicle.coordinators.keys():
        entities.append(RenaultMileageSensor(vehicle, "Mileage"))
        if vehicle.details.uses_fuel():
            entities.append(RenaultFuelAutonomySensor(vehicle, "Fuel Autonomy"))
            entities.append(RenaultFuelQuantitySensor(vehicle, "Fuel Quantity"))
    if "hvac_status" in vehicle.coordinators:
        entities.append(RenaultOutsideTemperatureSensor(vehicle, "Outside Temperature"))
    if "battery" in vehicle.coordinators:
        entities.append(RenaultBatteryLevelSensor(vehicle, "Battery Level"))
        entities.append(RenaultChargeStateSensor(vehicle, "Charge State"))
        entities.append(
            RenaultChargingRemainingTimeSensor(vehicle, "Charging Remaining Time")
        )
        entities.append(RenaultChargingPowerSensor(vehicle, "Charging Power"))
        entities.append(RenaultPlugStateSensor(vehicle, "Plug State"))
        entities.append(RenaultBatteryAutonomySensor(vehicle, "Battery Autonomy"))
        entities.append(RenaultBatteryTemperatureSensor(vehicle, "Battery Temperature"))
    if "charge_mode" in vehicle.coordinators:
        entities.append(RenaultChargeModeSensor(vehicle, "Charge Mode"))
    return entities


class RenaultBatteryLevelSensor(RenaultBatteryDataEntity):
    """Battery Level sensor."""

    @property
    def state(self) -> Optional[int]:
        """Return the state of this entity."""
        return self.data.batteryLevel

    @property
    def device_class(self) -> str:
        """Return the class of this entity."""
        return DEVICE_CLASS_BATTERY

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        return PERCENTAGE

    @property
    def icon(self) -> str:
        """Icon handling."""
        charging = self.data.get_charging_status() == ChargeState.CHARGE_IN_PROGRESS
        return icon_for_battery_level(battery_level=self.state, charging=charging)

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes of this entity."""
        attrs = super().device_state_attributes
        if self.data.batteryAvailableEnergy is not None:
            attrs[ATTR_BATTERY_AVAILABLE_ENERGY] = self.data.batteryAvailableEnergy
        return attrs


class RenaultBatteryTemperatureSensor(RenaultBatteryDataEntity):
    """Battery Temperature sensor."""

    @property
    def state(self) -> Optional[int]:
        """Return the state of this entity."""
        return self.data.batteryTemperature

    @property
    def device_class(self) -> str:
        """Return the class of this entity."""
        return DEVICE_CLASS_TEMPERATURE

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        return TEMP_CELSIUS


class RenaultChargeModeSensor(RenaultChargeModeDataEntity):
    """Charge Mode sensor."""

    @property
    def state(self) -> Optional[str]:
        """Return the state of this entity."""
        return self.data.chargeMode

    @property
    def device_class(self) -> str:
        """Returning sensor device class"""
        return DEVICE_CLASS_CHARGE_MODE


class RenaultChargingRemainingTimeSensor(RenaultBatteryDataEntity):
    """Charging Remaining Time sensor."""

    @property
    def state(self) -> Optional[int]:
        """Return the state of this entity."""
        return self.data.chargingRemainingTime

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        return TIME_MINUTES


class RenaultChargingPowerSensor(RenaultBatteryDataEntity):
    """Charging Power sensor."""

    @property
    def state(self) -> Optional[float]:
        """Return the state of this entity."""
        if self.data.chargingInstantaneousPower is None:
            return None
        if self.vehicle.details.reports_charging_power_in_watts():
            # Need to convert to kilowatts
            return self.data.chargingInstantaneousPower / 1000
        return self.data.chargingInstantaneousPower

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        return POWER_KILO_WATT


class RenaultOutsideTemperatureSensor(RenaultHVACDataEntity):
    """HVAC Outside Temperature sensor."""

    @property
    def state(self) -> Optional[float]:
        """Return the state of this entity."""
        return self.data.externalTemperature

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        return TEMP_CELSIUS


class RenaultPlugStateSensor(RenaultBatteryDataEntity):
    """Plug State sensor."""

    @property
    def state(self) -> Optional[str]:
        """Return the state of this entity."""
        return (
            slugify(self.data.get_plug_status().name)
            if self.data.plugStatus is not None
            else None
        )

    @property
    def icon(self) -> str:
        """Icon handling."""
        if self.state == PlugState.PLUGGED.name:
            return "mdi:power-plug"
        return "mdi:power-plug-off"

    @property
    def device_class(self) -> str:
        """Returning sensor device class"""
        return DEVICE_CLASS_PLUG_STATE


class RenaultChargeStateSensor(RenaultBatteryDataEntity):
    """Charge State sensor."""

    @property
    def state(self) -> Optional[str]:
        """Return the state of this entity."""
        return (
            slugify(self.data.get_charging_status().name)
            if self.data.chargingStatus is not None
            else None
        )

    @property
    def icon(self) -> str:
        """Icon handling."""
        if self.state == ChargeState.CHARGE_IN_PROGRESS.name:
            return "mdi:flash"
        return "mdi:flash-off"

    @property
    def device_class(self) -> str:
        """Returning sensor device class"""
        return DEVICE_CLASS_CHARGE_STATE


class RenaultFuelAutonomySensor(RenaultCockpitDataEntity):
    """Fuel autonomy sensor."""

    @property
    def state(self) -> Optional[int]:
        """Return the state of this entity."""
        if self.data.fuelAutonomy is None:
            return None
        if self.hass.config.units.is_metric:
            return round(self.data.fuelAutonomy)
        return IMPERIAL_SYSTEM.length(self.data.fuelAutonomy, METRIC_SYSTEM.length_unit)

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        if self.hass.config.units.is_metric:
            return LENGTH_KILOMETERS
        return LENGTH_MILES


class RenaultFuelQuantitySensor(RenaultCockpitDataEntity):
    """Fuel quantity sensor."""

    @property
    def state(self) -> Optional[int]:
        """Return the state of this entity."""
        if self.data.fuelQuantity is None:
            return None
        if self.hass.config.units.is_metric:
            return round(self.data.fuelQuantity)
        return round(
            IMPERIAL_SYSTEM.volume(self.data.fuelQuantity, METRIC_SYSTEM.volume_unit)
        )

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        if self.hass.config.units.is_metric:
            return VOLUME_LITERS
        return VOLUME_GALLONS


class RenaultMileageSensor(RenaultCockpitDataEntity):
    """Mileage sensor."""

    @property
    def state(self) -> Optional[int]:
        """Return the state of this entity."""
        if self.data.totalMileage is None:
            return None
        if self.hass.config.units.is_metric:
            return round(self.data.totalMileage)
        return round(
            IMPERIAL_SYSTEM.length(self.data.totalMileage, METRIC_SYSTEM.length_unit)
        )

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        if self.hass.config.units.is_metric:
            return LENGTH_KILOMETERS
        return LENGTH_MILES


class RenaultBatteryAutonomySensor(RenaultBatteryDataEntity):
    """Battery autonomy sensor."""

    @property
    def state(self) -> Optional[int]:
        """Return the state of this entity."""
        if self.data.batteryAutonomy is None:
            return None
        if self.hass.config.units.is_metric:
            return self.data.batteryAutonomy
        return IMPERIAL_SYSTEM.length(
            self.data.batteryAutonomy, METRIC_SYSTEM.length_unit
        )

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        if self.hass.config.units.is_metric:
            return LENGTH_KILOMETERS
        return LENGTH_MILES
