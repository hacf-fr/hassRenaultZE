"""Support for Renault sensors."""
import logging
from typing import List

from renault_api.kamereon.enums import ChargeState, PlugState

from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_TEMPERATURE,
    PERCENTAGE,
    POWER_KILO_WATT,
    TEMP_CELSIUS,
)
from homeassistant.helpers.icon import icon_for_battery_level
from homeassistant.util import slugify
from homeassistant.util.distance import LENGTH_KILOMETERS, LENGTH_MILES
from homeassistant.util.unit_system import IMPERIAL_SYSTEM, METRIC_SYSTEM

from .const import (
    DOMAIN,
    MODEL_USES_KWH,
    DEVICE_CLASS_PLUG_STATE,
    DEVICE_CLASS_CHARGE_STATE,
)
from .renault_hub import RenaultHub
from .renault_vehicle import RenaultVehicleProxy
from .renault_entities import (
    RenaultBatteryDataEntity,
    RenaultChargeModeDataEntity,
    RenaultDataEntity,
    RenaultHVACDataEntity,
    RenaultCockpitDataEntity,
)

ATTR_BATTERY_AVAILABLE_ENERGY = "battery_available_energy"
ATTR_CHARGING_POWER = "charging_power"
ATTR_CHARGING_REMAINING_TIME = "charging_remaining_time"
ATTR_PLUGGED = "plugged"
ATTR_PLUG_STATUS = "plug_status"

LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way of setting up platforms."""


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Renault entities from config entry."""
    proxy: RenaultHub = hass.data[DOMAIN][config_entry.unique_id]
    entities = await get_entities(hass, proxy)
    proxy.entities.extend(entities)
    async_add_entities(entities)


async def get_entities(hass, proxy: RenaultHub) -> List[RenaultDataEntity]:
    """Create Renault entities for all vehicles."""
    entities = []
    for vehicle_link in proxy.get_vehicle_links():
        vehicle_proxy = await proxy.get_vehicle(vehicle_link)
        entities.extend(await get_vehicle_entities(hass, vehicle_proxy))
    return entities


async def get_vehicle_entities(
    hass, vehicle_proxy: RenaultVehicleProxy
) -> List[RenaultDataEntity]:
    """Create Renault entities for single vehicle."""
    entities = []
    if "cockpit" in vehicle_proxy.coordinators:
        entities.append(RenaultMileageSensor(vehicle_proxy, "Mileage"))
    if "hvac_status" in vehicle_proxy.coordinators:
        entities.append(
            RenaultOutsideTemperatureSensor(vehicle_proxy, "Outside Temperature")
        )
    if "battery" in vehicle_proxy.coordinators:
        entities.append(RenaultBatteryLevelSensor(vehicle_proxy, "Battery Level"))
        entities.append(RenaultChargeStateSensor(vehicle_proxy, "Charge State"))
        entities.append(
            RenaultChargingRemainingTimeSensor(vehicle_proxy, "Charging Remaining Time")
        )
        entities.append(RenaultChargingPowerSensor(vehicle_proxy, "Charging Power"))
        entities.append(RenaultPlugStateSensor(vehicle_proxy, "Plug State"))
        entities.append(RenaultBatteryRangeSensor(vehicle_proxy, "Range"))
        entities.append(
            RenaultBatteryTemperatureSensor(vehicle_proxy, "Battery Temperature")
        )
    if "charge_mode" in vehicle_proxy.coordinators:
        entities.append(RenaultChargeModeSensor(vehicle_proxy, "Charge Mode"))
    return entities


class RenaultBatteryLevelSensor(RenaultBatteryDataEntity):
    """Battery Level sensor."""

    @property
    def state(self):
        """Return the state of this entity."""
        return self.data.batteryLevel

    @property
    def device_class(self):
        """Return the class of this entity."""
        return DEVICE_CLASS_BATTERY

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return PERCENTAGE

    @property
    def icon(self):
        """Icon handling."""
        if self.data.chargingStatus is not None:  # Zero can be a valid value
            charging = self.data.get_charging_status() == ChargeState.CHARGE_IN_PROGRESS
        else:
            charging = False
        return icon_for_battery_level(battery_level=self.state, charging=charging)

    @property
    def device_state_attributes(self):
        """Return the state attributes of this entity."""
        attrs = {}
        attrs.update(super().device_state_attributes)
        if "batteryAvailableEnergy" in self.data.raw_data:
            attrs[ATTR_BATTERY_AVAILABLE_ENERGY] = self.data.raw_data[
                "batteryAvailableEnergy"
            ]
        return attrs


class RenaultBatteryTemperatureSensor(RenaultBatteryDataEntity):
    """Battery Temperature sensor."""

    @property
    def state(self):
        """Return the state of this entity."""
        return self.data.batteryTemperature

    @property
    def device_class(self):
        """Return the class of this entity."""
        return DEVICE_CLASS_TEMPERATURE

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return TEMP_CELSIUS


class RenaultChargeModeSensor(RenaultChargeModeDataEntity):
    """Charge Mode sensor."""

    @property
    def state(self):
        """Return the state of this entity."""
        if self.data.chargeMode is not None:  # Zero can be a valid value
            return self.data.get_charge_mode()


class RenaultChargingRemainingTimeSensor(RenaultBatteryDataEntity):
    """Charging Remaining Time sensor."""

    @property
    def state(self):
        """Return the state of this entity."""
        return self.data.chargingRemainingTime


class RenaultChargingPowerSensor(RenaultBatteryDataEntity):
    """Charging Power sensor."""

    @property
    def state(self):
        """Return the state of this entity."""
        result = self.data.chargingInstantaneousPower
        if result is not None:  # Zero can be a valid value
            if self.proxy.model_code not in MODEL_USES_KWH:
                result = result / 1000
        return result

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return POWER_KILO_WATT


class RenaultOutsideTemperatureSensor(RenaultHVACDataEntity):
    """HVAC Outside Temperature sensor."""

    @property
    def state(self):
        """Return the state of this entity."""
        return self.data.externalTemperature

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""
        return TEMP_CELSIUS


class RenaultPlugStateSensor(RenaultBatteryDataEntity):
    """Plug State sensor."""

    @property
    def state(self):
        """Return the state of this entity."""
        if self.data.plugStatus is not None:  # Zero can be a valid value
            plug_status = self.data.get_plug_status()
            return slugify(plug_status.name)

    @property
    def icon(self):
        """Icon handling."""
        if self.state == PlugState.PLUGGED.name:
            return "mdi:power-plug"
        return "mdi:power-plug-off"

    @property
    def device_class(self):
        """Returning sensor device class"""
        return DEVICE_CLASS_PLUG_STATE


class RenaultChargeStateSensor(RenaultBatteryDataEntity):
    """Charge State sensor."""

    @property
    def state(self):
        """Return the state of this entity."""
        if self.data.chargingStatus is not None:  # Zero can be a valid value
            charging_status = self.data.get_charging_status()
            return slugify(charging_status.name)

    @property
    def icon(self):
        """Icon handling."""
        if self.state == ChargeState.CHARGE_IN_PROGRESS.name:
            return "mdi:flash"
        return "mdi:flash-off"

    @property
    def device_class(self):
        """Returning sensor device class"""
        return DEVICE_CLASS_CHARGE_STATE


class RenaultMileageSensor(RenaultCockpitDataEntity):
    """Mileage sensor."""

    @property
    def state(self):
        """Return the state of this entity."""
        mileage = self.data.totalMileage
        if mileage is not None:  # Zero can be a valid value
            if not self.hass.config.units.is_metric:
                mileage = IMPERIAL_SYSTEM.length(mileage, METRIC_SYSTEM.length_unit)
            return round(mileage)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        if not self.hass.config.units.is_metric:
            return LENGTH_MILES
        return LENGTH_KILOMETERS


class RenaultBatteryRangeSensor(RenaultBatteryDataEntity):
    """Battery range sensor."""

    @property
    def state(self):
        """Return the state of this entity."""
        autonomy = self.data.batteryAutonomy
        if autonomy is not None:  # Zero can be a valid value
            if not self.hass.config.units.is_metric:
                autonomy = IMPERIAL_SYSTEM.length(autonomy, METRIC_SYSTEM.length_unit)
            return autonomy

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        if not self.hass.config.units.is_metric:
            return LENGTH_MILES
        return LENGTH_KILOMETERS
