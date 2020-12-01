"""Support for Renault devices."""

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import CONF_KAMEREON_ACCOUNT_ID, CONF_LOCALE, DOMAIN, SUPPORTED_PLATFORMS
from .renault_hub import RenaultHub
from .services import async_setup_services, async_unload_services


async def async_setup(hass, config):
    """Set up renault integrations."""
    return True


async def async_setup_entry(hass, config_entry):
    """Load a config entry."""
    hass.data.setdefault(DOMAIN, {})

    renault_hub = RenaultHub(hass, config_entry.data[CONF_LOCALE])
    if not await renault_hub.attempt_login(
        config_entry.data[CONF_USERNAME], config_entry.data[CONF_PASSWORD]
    ):
        return False

    await renault_hub.set_account_id(config_entry.data[CONF_KAMEREON_ACCOUNT_ID])

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
