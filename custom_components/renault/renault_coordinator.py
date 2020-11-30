"""Proxy to handle account communication with Renault servers."""
from datetime import timedelta
import logging
from typing import Optional

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    T,
    UpdateFailed,
)

from renault_api.kamereon.exceptions import KamereonResponseException

DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)
LONG_SCAN_INTERVAL = timedelta(minutes=10)

LOGGER = logging.getLogger(__name__)


class RenaultDataUpdateCoordinator(DataUpdateCoordinator):
    """Handle vehicle communication with Renault servers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_denied = False
        self.not_supported = False

    async def _async_update_data(self) -> Optional[T]:
        """Fetch the latest data from the source."""
        if self.update_method is None:
            raise NotImplementedError("Update method not implemented")
        try:
            return await self.update_method()
        except KamereonResponseException as err:
            if (
                err.error_code == ["err.func.403"]
                and err.error_details == "Access is denied for this resource"
            ):
                self.update_interval = None
                self.access_denied = True
            elif (
                err.error_code == ["err.tech.501"]
                and err.error_details
                == "This feature is not technically supported by this gateway"
            ):
                self.update_interval = None
                self.not_supported = True
            raise UpdateFailed(f"Error communicating with API: {err}")
