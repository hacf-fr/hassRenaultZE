"""Support for Renault devices."""
import aiohttp
from awesomeversion import AwesomeVersion
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import __version__, CONF_PASSWORD, CONF_USERNAME
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import HomeAssistantType
import logging


from .const import CONF_LOCALE, DOMAIN, SUPPORTED_PLATFORMS
from .renault_hub import RenaultHub
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up renault integrations."""
    if AwesomeVersion(__version__) >= "2021.10.0b0":
        _LOGGER.error(
            "The Renault integration was originally merged into core in 2021.8 "
            "and finalised in 2021.10. The use of this custom component has been "
            "deprecated since then and should be removed from your installation"
        )
    return True


async def async_setup_entry(hass: HomeAssistantType, config_entry: ConfigEntry):
    """Load a config entry."""
    hass.data.setdefault(DOMAIN, {})

    renault_hub = RenaultHub(hass, config_entry.data[CONF_LOCALE])
    try:
        login_success = await renault_hub.attempt_login(
            config_entry.data[CONF_USERNAME], config_entry.data[CONF_PASSWORD]
        )
    except aiohttp.ClientConnectionError as exc:
        raise ConfigEntryNotReady() from exc

    if not login_success:
        return False

    await renault_hub.async_initialise(config_entry)

    hass.data[DOMAIN][config_entry.unique_id] = renault_hub

    for component in SUPPORTED_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    await async_setup_services(hass)

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    unload_ok = True

    for component in SUPPORTED_PLATFORMS:
        unload_ok = unload_ok and await hass.config_entries.async_forward_entry_unload(
            config_entry, component
        )

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.unique_id)
        if not hass.data[DOMAIN]:
            await async_unload_services(hass)

    return unload_ok
