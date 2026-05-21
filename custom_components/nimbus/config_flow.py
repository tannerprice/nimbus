from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_HISTORY_LIMIT,
    CONF_TOPIC_ROOT,
    DEFAULT_HISTORY_LIMIT,
    DEFAULT_TOPIC_ROOT,
    DOMAIN,
)


class NimbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id("nimbus")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Nimbus",
                data={
                    CONF_TOPIC_ROOT: user_input[CONF_TOPIC_ROOT].strip().strip("/"),
                    CONF_HISTORY_LIMIT: user_input[CONF_HISTORY_LIMIT],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TOPIC_ROOT, default=DEFAULT_TOPIC_ROOT): str,
                    vol.Required(
                        CONF_HISTORY_LIMIT,
                        default=DEFAULT_HISTORY_LIMIT,
                    ): vol.All(int, vol.Range(min=1, max=500)),
                }
            ),
            errors={},
        )
