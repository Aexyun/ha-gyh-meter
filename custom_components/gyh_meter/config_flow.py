import logging
import voluptuous as vol
import json
import async_timeout

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_WECHAT_USER_ID, CONF_METER_ID, CONF_OPENID, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class GYHMeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_WECHAT_USER_ID],
                user_input[CONF_METER_ID],
                user_input[CONF_OPENID]
            )
            if valid:
                return self.async_create_entry(
                    title=f"公元汇电表 ({user_input[CONF_METER_ID]})",
                    data=user_input
                )
            else:
                errors["base"] = "invalid_auth"

        data_schema = vol.Schema({
            vol.Required(CONF_WECHAT_USER_ID): str,
            vol.Required(CONF_METER_ID): str,
            vol.Required(CONF_OPENID): str,
            vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=1))
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def _test_credentials(self, wechat_user_id, meter_id, openid):
        url = "http://www.gywy8.com/kddz/electricmeterpost/electricMeterQuery"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": f"http://www.gywy8.com/electricmeter/pages/meterlist/meterquery?wechatUserOpenid={openid}&meterId={meter_id}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138.0.0.0"
        }
        payload = {"wechatUserId": wechat_user_id, "electricUserUid": meter_id}
        session = async_get_clientsession(self.hass)
        try:
            async with async_timeout.timeout(10):
                async with session.post(url, data=payload, headers=headers) as resp:
                    res_json = json.loads(await resp.text())
                    if res_json.get("code") == 0 and "shengyu" in res_json.get("data", {}):
                        return True
        except Exception:
            pass
        return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return GYHMeterOptionsFlowHandler(config_entry)

class GYHMeterOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_UPDATE_INTERVAL, 
            self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )

        options_schema = vol.Schema({
            vol.Required(CONF_UPDATE_INTERVAL, default=current_interval): vol.All(vol.Coerce(int), vol.Range(min=1))
        })
        return self.async_show_form(step_id="init", data_schema=options_schema)