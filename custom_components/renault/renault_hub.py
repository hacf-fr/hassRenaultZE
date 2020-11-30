"""Proxy to handle account communication with Renault servers."""
import logging
from typing import Dict, List, Optional

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import HomeAssistantType

from renault_api.gigya.exceptions import GigyaResponseException
from renault_api.kamereon.models import KamereonVehiclesLink
from renault_api.renault_account import RenaultAccount
from renault_api.renault_client import RenaultClient

from .renault_entities import RenaultDataEntity
from .renault_vehicle import RenaultVehicleProxy

LOGGER = logging.getLogger(__name__)


class RenaultHub:
    """Handle account communication with Renault servers."""

    def __init__(self, hass: HomeAssistantType, locale: str) -> None:
        """Initialise proxy."""
        LOGGER.debug("Creating RenaultHub")
        self._hass = hass
        self._client = RenaultClient(
            websession=async_get_clientsession(self._hass), locale=locale
        )
        self._account: Optional[RenaultAccount] = None
        self._vehicle_links: List[KamereonVehiclesLink] = []
        self._vehicle_proxies: Dict[str, RenaultVehicleProxy] = {}
        self.entities: List[RenaultDataEntity] = []

    async def attempt_login(self, username: str, password: str) -> bool:
        """Attempt login to Renault servers."""
        try:
            await self._client.session.login(username, password)
        except GigyaResponseException as ex:
            LOGGER.error("Login to Renault failed: %s", ex.error_details)
        else:
            return True
        return False

    async def set_account_id(self, account_id: str) -> None:
        """Set up proxy."""
        self._account = await self._client.get_api_account(account_id)
        vehicles = await self._account.get_vehicles()
        self._vehicle_links = vehicles.vehicleLinks
        for vehicle_link in vehicles.vehicleLinks:
            # Generate vehicle proxy
            await self.get_vehicle(vehicle_link)

    async def get_account_ids(self) -> list:
        """Get Kamereon account ids."""
        accounts = []
        for account in await self._client.get_api_accounts():
            vehicles = await account.get_vehicles()

            # Skip the account if no vehicles found in it.
            if len(vehicles.vehicleLinks) > 0:
                accounts.append(account._account_id)
        return accounts

    def get_vehicle_links(self) -> List[KamereonVehiclesLink]:
        """Get list of vehicles."""
        return self._vehicle_links

    def get_vehicle_from_vin(self, vin: str) -> RenaultVehicleProxy:
        """Get vehicle from VIN."""
        return self._vehicle_proxies[vin]

    async def get_vehicle(
        self, vehicle_link: KamereonVehiclesLink
    ) -> RenaultVehicleProxy:
        """Get a proxy for the vehicle."""
        vin = vehicle_link.vin
        vehicle_proxy = self._vehicle_proxies.get(vin)
        if vehicle_proxy is None:
            vehicle_proxy = RenaultVehicleProxy(
                self._hass,
                vehicle_link,
                await self._account.get_api_vehicle(vin),
            )
            await vehicle_proxy.async_initialise()
            self._vehicle_proxies[vin] = vehicle_proxy
        return self._vehicle_proxies[vin]
