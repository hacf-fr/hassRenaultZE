"""Tests for the Renault integration."""
from unittest.mock import patch

from homeassistant.config_entries import CONN_CLASS_CLOUD_POLL
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.renault.const import (
    CONF_KAMEREON_ACCOUNT_ID,
    CONF_LOCALE,
    DOMAIN,
)


async def setup_renault_integration(hass):
    """Create the Renault integration."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        source="user",
        data={
            CONF_LOCALE: "fr_FR",
            CONF_USERNAME: "email@test.com",
            CONF_PASSWORD: "test",
            CONF_KAMEREON_ACCOUNT_ID: "account_id_2",
        },
        unique_id="account_id_2",
        connection_class=CONN_CLASS_CLOUD_POLL,
        options={},
        entry_id="1",
    )
    config_entry.add_to_hass(hass)

    with patch(
        "custom_components.renault.RenaultHub.attempt_login", return_value=True
    ), patch("custom_components.renault.RenaultHub.async_initialise"):
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    return config_entry
