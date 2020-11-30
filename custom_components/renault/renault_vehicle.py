"""Proxy to handle account communication with Renault servers."""
from datetime import timedelta
import logging
from typing import Dict
from renault_api.kamereon.enums import EnergyCode

from renault_api.kamereon.exceptions import KamereonResponseException
from renault_api.kamereon.models import KamereonVehiclesLink
from renault_api.renault_vehicle import RenaultVehicle

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, MODEL_SUPPORTS_LOCATION

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
        self.coordinators: Dict[str, DataUpdateCoordinator] = {}
        self.hvac_target_temperature = 21

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._device_info

    @property
    def registration(self) -> str:
        """Return the registration of the vehicle."""
        return self._vehicle_link.get_details().get_registration_number()

    @property
    def model_code(self) -> str:
        """Return the model code of the vehicle."""
        return self._vehicle_link.get_details().raw_data["model"]["code"]

    @property
    def vin(self) -> str:
        """Return the VIN of the vehicle."""
        return self._vehicle_link.vin

    async def async_initialise(self):
        """Load available sensors."""
        brand = self._vehicle_link.raw_data["brand"]
        model_label = self._vehicle_link.get_details().get_model_label()
        self._device_info = {
            "identifiers": {(DOMAIN, self.vin)},
            "manufacturer": brand.capitalize(),
            "model": model_label.capitalize(),
            "name": self.registration,
            "sw_version": self.model_code,
        }

        self.coordinators["cockpit"] = DataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.vin} cockpit",
            update_method=self.get_cockpit,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=LONG_SCAN_INTERVAL,
        )
        self.coordinators["hvac_status"] = DataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.vin} hvac_status",
            update_method=self.get_hvac_status,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        if self._vehicle_link.get_details().get_energy_code() == EnergyCode.ELECTRIQUE:
            self.coordinators["battery"] = DataUpdateCoordinator(
                self.hass,
                LOGGER,
                # Name of the data. For logging purposes.
                name=f"{self.vin} battery",
                update_method=self.get_battery_status,
                # Polling interval. Will only be polled if there are subscribers.
                update_interval=DEFAULT_SCAN_INTERVAL,
            )
            self.coordinators["charge_mode"] = DataUpdateCoordinator(
                self.hass,
                LOGGER,
                # Name of the data. For logging purposes.
                name=f"{self.vin} charge_mode",
                update_method=self.get_charge_mode,
                # Polling interval. Will only be polled if there are subscribers.
                update_interval=DEFAULT_SCAN_INTERVAL,
            )
        if self.model_code in MODEL_SUPPORTS_LOCATION:
            coordinator = DataUpdateCoordinator(
                self.hass,
                LOGGER,
                # Name of the data. For logging purposes.
                name=f"{self.vin} location",
                update_method=self.get_location,
                # Polling interval. Will only be polled if there are subscribers.
                update_interval=DEFAULT_SCAN_INTERVAL,
            )
        for coordinator in self.coordinators.values():
            await coordinator.async_refresh()

    async def get_battery_status(self, ignore_errors: bool = None):
        """Get battery_status."""
        try:
            return await self._vehicle.get_battery_status()
        except KamereonResponseException as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def get_charge_mode(self, ignore_errors: bool = None):
        """Get charge_mode."""
        try:
            return await self._vehicle.get_charge_mode()
        except KamereonResponseException as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def get_charge_schedules(self, ignore_errors: bool = None):
        """Get charge schedules."""
        try:
            return await self._vehicle.get_charging_settings()
        except KamereonResponseException as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def get_hvac_status(self, ignore_errors: bool = None):
        """Get hvac_status."""
        try:
            return await self._vehicle.get_hvac_status()
        except KamereonResponseException as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def get_location(self, ignore_errors: bool = None):
        """Get location."""
        try:
            return await self._vehicle.get_location()
        except KamereonResponseException as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def get_cockpit(self, ignore_errors: bool = None):
        """Get cockpit."""
        try:
            return await self._vehicle.get_cockpit()
        except KamereonResponseException as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

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
