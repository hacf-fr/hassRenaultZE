"""Config flow to configure Renault component."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from renault_api.const import AVAILABLE_LOCALES

from .const import (  # pylint: disable=unused-import
    CONF_KAMEREON_ACCOUNT_ID,
    CONF_LOCALE,
    DOMAIN,
)
from .pyzeproxy import PyzeProxy


class RenaultFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Renault config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize the Renault config flow."""
        self.renault_config = {}
        self.pyzeproxy = None

    async def async_step_user(self, user_input=None):
        """Handle a Renault config flow start.

        Ask the user for API keys.
        """
        if user_input:
            locale = user_input[CONF_LOCALE]
            user_input.update(AVAILABLE_LOCALES[locale])
            self.renault_config.update(user_input)
            return await self.async_step_credentials()
        return self._show_user_form()

    def _show_user_form(self, errors=None):
        """Show the API keys form."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LOCALE): vol.In(AVAILABLE_LOCALES.keys()),
                }
            ),
            errors=errors if errors else {},
        )

    async def async_step_credentials(self, user_input=None):
        """Request credentials."""
        if user_input:
            self.renault_config.update(user_input)
            self.pyzeproxy = PyzeProxy(self.hass)
            self.pyzeproxy.set_api_keys(self.renault_config)
            if not await self.pyzeproxy.attempt_login(self.renault_config):
                return self._show_credentials_form({"base": "invalid_credentials"})
            return await self.async_step_kamereon()
        return self._show_credentials_form()

    def _show_credentials_form(self, errors=None):
        """Show the credentials form."""
        return self.async_show_form(
            step_id="credentials",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors if errors else {},
        )

    async def async_step_kamereon(self, user_input=None):
        """Select Kamereon account."""
        if user_input:
            self.renault_config.update(user_input)
            return self.async_create_entry(
                title=user_input[CONF_KAMEREON_ACCOUNT_ID], data=self.renault_config
            )

        accounts = await self.pyzeproxy.get_account_ids()
        if len(accounts) == 0:
            return self.async_abort(reason="kamereon_no_account")
        if len(accounts) == 1:
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
