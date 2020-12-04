"""Proxy to handle account communication with Renault servers."""
from datetime import timedelta
import logging
from typing import Any, Dict

from renault_api.kamereon import models
from renault_api.renault_vehicle import RenaultVehicle

from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN
from .renault_coordinator import RenaultDataUpdateCoordinator

DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)

LOGGER = logging.getLogger(__name__)


class RenaultVehicleProxy:
    """Handle vehicle communication with Renault servers."""

    def __init__(
        self,
        hass: HomeAssistantType,
        vehicle: RenaultVehicle,
        details: models.KamereonVehiclesDetails,
    ) -> None:
        """Initialise vehicle proxy."""
        self.hass = hass
        self._vehicle = vehicle
        self._details = details
        self._device_info = {
            "identifiers": {(DOMAIN, details.vin)},
            "manufacturer": details.get_brand_label().capitalize(),
            "model": details.get_model_label().capitalize(),
            "name": details.registrationNumber,
            "sw_version": details.get_model_code(),
        }
        self.coordinators: Dict[str, RenaultDataUpdateCoordinator] = {}
        self.hvac_target_temperature = 21

    @property
    def details(self) -> models.KamereonVehiclesDetails:
        """Return the specs of the vehicle."""
        return self._details

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return a device description for device registry."""
        return self._device_info

    async def async_initialise(self) -> None:
        """Load available sensors."""
        self.coordinators["cockpit"] = RenaultDataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.details.vin} cockpit",
            update_method=self.get_cockpit,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.coordinators["hvac_status"] = RenaultDataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.details.vin} hvac_status",
            update_method=self.get_hvac_status,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        if self.details.uses_electricity():
            self.coordinators["battery"] = RenaultDataUpdateCoordinator(
                self.hass,
                LOGGER,
                # Name of the data. For logging purposes.
                name=f"{self.details.vin} battery",
                update_method=self.get_battery_status,
                # Polling interval. Will only be polled if there are subscribers.
                update_interval=DEFAULT_SCAN_INTERVAL,
            )
            self.coordinators["charge_mode"] = RenaultDataUpdateCoordinator(
                self.hass,
                LOGGER,
                # Name of the data. For logging purposes.
                name=f"{self.details.vin} charge_mode",
                update_method=self.get_charge_mode,
                # Polling interval. Will only be polled if there are subscribers.
                update_interval=DEFAULT_SCAN_INTERVAL,
            )
        self.coordinators["location"] = RenaultDataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.details.vin} location",
            update_method=self.get_location,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        for key in list(self.coordinators.keys()):
            await self.coordinators[key].async_refresh()
            if self.coordinators[key].not_supported:
                # Remove endpoint if it is not supported for this vehicle.
                del self.coordinators[key]
            elif self.coordinators[key].access_denied:
                # Remove endpoint if it is denied for this vehicle.
                del self.coordinators[key]

    async def get_battery_status(self) -> models.KamereonVehicleBatteryStatusData:
        """Get battery status information from vehicle."""
        return await self._vehicle.get_battery_status()

    async def get_charge_mode(self) -> models.KamereonVehicleChargeModeData:
        """Get charge mode information from vehicle."""
        return await self._vehicle.get_charge_mode()

    async def get_charging_settings(self) -> models.KamereonVehicleChargingSettingsData:
        """Get charging settings information from vehicle."""
        return await self._vehicle.get_charging_settings()

    async def get_hvac_status(self) -> models.KamereonVehicleHvacStatusData:
        """Get hvac status information from vehicle."""
        return await self._vehicle.get_hvac_status()

    async def get_location(self) -> models.KamereonVehicleLocationData:
        """Get location information from vehicle."""
        return await self._vehicle.get_location()

    async def get_cockpit(self) -> models.KamereonVehicleCockpitData:
        """Get cockpit information from vehicle."""
        return await self._vehicle.get_cockpit()

    async def send_ac_start(
        self, temperature, when=None
    ) -> models.KamereonVehicleHvacStartActionData:
        """Start A/C on vehicle."""
        return await self._vehicle.set_ac_start(temperature, when)

    async def send_cancel_ac(self) -> models.KamereonVehicleHvacStartActionData:
        """Cancel A/C on vehicle."""
        return await self._vehicle.set_ac_stop()

    async def send_set_charge_mode(
        self, charge_mode
    ) -> models.KamereonVehicleChargeModeActionData:
        """Set charge mode on vehicle."""
        return await self._vehicle.set_charge_mode(charge_mode)

    async def send_charge_start(self) -> models.KamereonVehicleChargingStartActionData:
        """Start charge on vehicle."""
        return await self._vehicle.set_charge_start()

    async def send_set_charge_schedules(
        self, schedules: models.KamereonVehicleChargingSettingsData
    ) -> models.KamereonVehicleChargeScheduleActionData:
        """Set charge schedules on vehicle."""
        return await self._vehicle.set_charge_schedules(schedules.schedules)
