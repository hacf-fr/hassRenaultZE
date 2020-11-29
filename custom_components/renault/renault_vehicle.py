"""Proxy to handle account communication with Renault servers."""
from datetime import timedelta
import logging
from renault_api.kamereon.models import KamereonVehiclesLink

from renault_api.renault_vehicle import RenaultVehicle

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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
        self.coordinators = {}
        self.hvac_target_temperature = 21

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._device_info

    @property
    def registration(self) -> str:
        """Return the registration of the vehicle."""
        return self._vehicle_link.raw_data["vehicleDetails"]["registrationNumber"]

    @property
    def model_code(self) -> str:
        """Return the model code of the vehicle."""
        return self._vehicle_link.raw_data["vehicleDetails"]["model"]["code"]

    @property
    def vin(self) -> str:
        """Return the VIN of the vehicle."""
        return self._vehicle_link.vin

    async def async_initialise(self):
        """Load available sensors."""
        brand = self._vehicle_link.raw_data["brand"]
        model_label = self._vehicle_link.raw_data["vehicleDetails"]["model"]["label"]
        self._device_info = {
            "identifiers": {(DOMAIN, self.vin)},
            "manufacturer": brand.capitalize(),
            "model": model_label.capitalize(),
            "name": self.registration,
            "sw_version": self.model_code,
        }

        self.coordinators["battery"] = DataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.vin} battery",
            update_method=self.get_battery_status,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.coordinators["mileage"] = DataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.vin} mileage",
            update_method=self.get_mileage,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=LONG_SCAN_INTERVAL,
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
        self.coordinators["hvac_status"] = DataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.vin} hvac_status",
            update_method=self.get_hvac_status,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        if self.model_code in MODEL_SUPPORTS_LOCATION:
            self.coordinators["location"] = DataUpdateCoordinator(
                self.hass,
                LOGGER,
                # Name of the data. For logging purposes.
                name=f"{self.vin} location",
                update_method=self.get_location,
                # Polling interval. Will only be polled if there are subscribers.
                update_interval=DEFAULT_SCAN_INTERVAL,
            )
        else:
            LOGGER.warning("Model code %s does not support location.", self.model_code)
        for key in self.coordinators:
            await self.coordinators[key].async_refresh()

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

    async def get_mileage(self):
        """Get mileage."""
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
