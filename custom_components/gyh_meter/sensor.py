import logging
import async_timeout
import json
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_WECHAT_USER_ID, CONF_METER_ID, CONF_OPENID, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    wechat_user_id = config_entry.data[CONF_WECHAT_USER_ID]
    meter_id = config_entry.data[CONF_METER_ID]
    openid = config_entry.data[CONF_OPENID]
    
    update_interval_hours = config_entry.options.get(
        CONF_UPDATE_INTERVAL, 
        config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    )

    coordinator = GYHMeterCoordinator(hass, wechat_user_id, meter_id, openid, update_interval_hours)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        GYHSensor(coordinator, "shengyu", "剩余电量", "mdi:lightning-bolt", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL),
        GYHSensor(coordinator, "leiji", "累计用电", "mdi:chart-bell-curve-cumulative", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        GYHPriceSensor(meter_id)
    ])

class GYHMeterCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, wechat_user_id, meter_id, openid, interval_hours):
        super().__init__(
            hass, _LOGGER, name="公元汇电费数据抓取",
            update_interval=timedelta(hours=interval_hours),
        )
        self.wechat_user_id, self.meter_id, self.openid = wechat_user_id, meter_id, openid

    async def _async_update_data(self):
        url = "http://www.gywy8.com/kddz/electricmeterpost/electricMeterQuery"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": f"http://www.gywy8.com/electricmeter/pages/meterlist/meterquery?wechatUserOpenid={self.openid}&meterId={self.meter_id}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138.0.0.0"
        }
        payload = {"wechatUserId": self.wechat_user_id, "electricUserUid": self.meter_id}
        session = async_get_clientsession(self.hass)
        try:
            async with async_timeout.timeout(15):
                async with session.post(url, data=payload, headers=headers) as resp:
                    res_json = json.loads(await resp.text())
                    if res_json.get("code") == 0:
                        return res_json.get("data", {})
                    raise UpdateFailed(res_json.get('msg'))
        except Exception as err:
            raise UpdateFailed(str(err))

class GYHSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, icon, device_class, state_class):
        super().__init__(coordinator)
        self.key = key
        self._attr_name = f"{coordinator.meter_id} {name}"
        self._attr_unique_id = f"gyh_{coordinator.meter_id}_{key}"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_icon = icon  # 引入原生图标
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self):
        try: return float(self.coordinator.data.get(self.key))
        except (TypeError, ValueError): return None

class GYHPriceSensor(SensorEntity):
    def __init__(self, meter_id):
        self._attr_name = f"{meter_id} 电费单价"
        self._attr_unique_id = f"gyh_{meter_id}_price"
        self._attr_native_unit_of_measurement = "CNY/kWh" 
        self._attr_icon = "mdi:currency-cny" # 原生人民币图标
        self._attr_device_class = SensorDeviceClass.MONETARY

    @property
    def native_value(self):
        return 0.9
