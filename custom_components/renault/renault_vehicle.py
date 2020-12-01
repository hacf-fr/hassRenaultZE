"""Proxy to handle account communication with Renault servers."""
from datetime import timedelta
import logging
from typing import Dict

from renault_api.kamereon.models import KamereonVehiclesDetails, KamereonVehiclesLink
from renault_api.renault_vehicle import RenaultVehicle

from .renault_coordinator import RenaultDataUpdateCoordinator

from .const import DOMAIN

DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)
LONG_SCAN_INTERVAL = timedelta(minutes=10)

LOGGER = logging.getLogger(__name__)


class RenaultVehicleProxy:
    """Handle vehicle communication with Renault servers."""

    def __init__(
        self, hass, vehicle_link: KamereonVehiclesLink, vehicle: RenaultVehicle
    ):
        """Initialise vehicle proxy."""
        self.hass = hass
        self._vehicle_link = vehicle_link
        self._vehicle = vehicle
        self._device_info = None
        self.coordinators: Dict[str, RenaultDataUpdateCoordinator] = {}
        self.hvac_target_temperature = 21

    @property
    def vehicle_details(self) -> KamereonVehiclesDetails:
        """Return the specs of the vehicle."""
        return self._vehicle_link.vehicleDetails

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._device_info

    @property
    def registration(self) -> str:
        """Return the registration of the vehicle."""
        return self.vehicle_details.registrationNumber

    @property
    def model_code(self) -> str:
        """Return the model code of the vehicle."""
        return self.vehicle_details.model.code

    @property
    def vin(self) -> str:
        """Return the VIN of the vehicle."""
        return self._vehicle_link.vin

    async def async_initialise(self):
        """Load available sensors."""
        self._device_info = {
            "identifiers": {(DOMAIN, self.vin)},
            "manufacturer": self.vehicle_details.brand.label.capitalize(),
            "model": self.vehicle_details.model.label.capitalize(),
            "name": self.registration,
            "sw_version": self.vehicle_details.model.code,
        }

        self.coordinators["cockpit"] = RenaultDataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.vin} cockpit",
            update_method=self.get_cockpit,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=LONG_SCAN_INTERVAL,
        )
        self.coordinators["hvac_status"] = RenaultDataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.vin} hvac_status",
            update_method=self.get_hvac_status,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        if self._vehicle_link.vehicleDetails.uses_electricity():
            self.coordinators["battery"] = RenaultDataUpdateCoordinator(
                self.hass,
                LOGGER,
                # Name of the data. For logging purposes.
                name=f"{self.vin} battery",
                update_method=self.get_battery_status,
                # Polling interval. Will only be polled if there are subscribers.
                update_interval=DEFAULT_SCAN_INTERVAL,
            )
            self.coordinators["charge_mode"] = RenaultDataUpdateCoordinator(
                self.hass,
                LOGGER,
                # Name of the data. For logging purposes.
                name=f"{self.vin} charge_mode",
                update_method=self.get_charge_mode,
                # Polling interval. Will only be polled if there are subscribers.
                update_interval=DEFAULT_SCAN_INTERVAL,
            )
        self.coordinators["location"] = RenaultDataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.vin} location",
            update_method=self.get_location,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        for key in list(self.coordinators.keys()):
            await self.coordinators[key].async_refresh()
            if self.coordinators[key].not_supported:
                del self.coordinators[key]
            elif self.coordinators[key].access_denied:
                del self.coordinators[key]

    async def get_battery_status(self):
        """Get battery_status."""
        return await self._vehicle.get_battery_status()

    async def get_charge_mode(self):
        """Get charge_mode."""
        return await self._vehicle.get_charge_mode()

    async def get_charge_schedules(self):
        """Get charge schedules."""
        return await self._vehicle.get_charging_settings()

    async def get_hvac_status(self):
        """Get hvac_status."""
        return await self._vehicle.get_hvac_status()

    async def get_location(self):
        """Get location."""
        return await self._vehicle.get_location()

    async def get_cockpit(self):
        """Get cockpit."""
        return await self._vehicle.get_cockpit()

    async def send_ac_start(self, temperature, when=None):
        """Start A/C."""
        return await self._vehicle.set_ac_start(temperature, when)

    async def send_cancel_ac(self):
        """Cancel A/C."""
        return await self._vehicle.set_ac_stop()

    async def send_set_charge_mode(self, charge_mode):
        """Set charge mode."""
        return await self._vehicle.set_charge_mode(charge_mode)

    async def send_charge_start(self):
        """Start charge."""
        return await self._vehicle.set_charge_start()

    async def send_set_charge_schedules(self, schedules):
        """Set charge schedules."""
        return await self._vehicle.set_charge_schedules(schedules)
