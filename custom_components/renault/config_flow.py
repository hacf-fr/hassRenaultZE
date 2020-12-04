"""Config flow to configure Renault component."""
from typing import Any, Dict

from renault_api.const import AVAILABLE_LOCALES
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import (  # pylint: disable=unused-import
    CONF_KAMEREON_ACCOUNT_ID,
    CONF_LOCALE,
    DOMAIN,
)
from .renault_hub import RenaultHub


class RenaultFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Renault config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialize the Renault config flow."""
        self.renault_config = {}
        self.renault_hub = None

    async def async_step_user(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle a Renault config flow start.

        Ask the user for API keys.
        """
        if user_input:
            locale = user_input[CONF_LOCALE]
            self.renault_config.update(user_input)
            self.renault_config.update(AVAILABLE_LOCALES[locale])
            self.renault_hub = RenaultHub(self.hass, locale)
            if not await self.renault_hub.attempt_login(
                user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            ):
                return self._show_user_form({"base": "invalid_credentials"})
            return await self.async_step_kamereon()
        return self._show_user_form()

    def _show_user_form(self, errors: Dict[str, Any] = None) -> Dict[str, Any]:
        """Show the API keys form."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LOCALE): vol.In(AVAILABLE_LOCALES.keys()),
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors if errors else {},
        )

    async def async_step_kamereon(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Select Kamereon account."""
        if user_input:
            await self.async_set_unique_id(user_input[CONF_KAMEREON_ACCOUNT_ID])
            self._abort_if_unique_id_configured()

            self.renault_config.update(user_input)
            return self.async_create_entry(
                title=user_input[CONF_KAMEREON_ACCOUNT_ID], data=self.renault_config
            )

        accounts = await self.renault_hub.get_account_ids()
        if len(accounts) == 0:
            return self.async_abort(reason="kamereon_no_account")
        if len(accounts) == 1:
            await self.async_set_unique_id(accounts[0])
            self._abort_if_unique_id_configured()

            self.renault_config[CONF_KAMEREON_ACCOUNT_ID] = accounts[0]
            return self.async_create_entry(
                title=self.renault_config[CONF_KAMEREON_ACCOUNT_ID],
                data=self.renault_config,
            )

        return self.async_show_form(
            step_id="kamereon",
            data_schema=vol.Schema(
                {vol.Required(CONF_KAMEREON_ACCOUNT_ID): vol.In(accounts)}
            ),
        )
