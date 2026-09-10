from __future__ import annotations
_A='via_device_id'
from homeassistant.core import HomeAssistant,callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from.const import DOMAIN
SIGNAL_UPDATED=f"{DOMAIN}_cache_updated"
GATEWAY_MODEL='DALI gateway'
GATEWAY_MANUFACTURER='Ctrlable Pro'
_SUPPORTS_VIA_DEVICE_ID=_A in getattr(DeviceInfo,'__annotations__',{})
def gateway_identifier(bus):return DOMAIN,f"dali_bus_{bus}"
def fixture_identifier(bus,key):return DOMAIN,f"dali_{bus}_{key}"
def link_to_gateway(info,bus,gateway_device_id):
	B=gateway_device_id;A=info
	if _SUPPORTS_VIA_DEVICE_ID:
		if B:A[_A]=B
	else:A['via_device']=gateway_identifier(bus)
	return A
class DaliEntity(Entity):
	_attr_should_poll=False
	def __init__(A,hass,bus):A.hass=hass;A._bus=bus
	@property
	def _cache(self):return(self.hass.data.get(DOMAIN)or{}).get('cache')or{}
	@property
	def _gateway(self):return(self._cache.get('gateways')or{}).get(self._bus)or{}
	@property
	def _base(self):return(self.hass.data.get(DOMAIN)or{}).get('base_topic')or'dali'
	@property
	def available(self):return self._gateway.get('bridge')=='online'
	async def _publish(B,topic,payload):A=payload;from homeassistant.components import mqtt;import json;await mqtt.async_publish(B.hass,topic,A if isinstance(A,str)else json.dumps(A))
	async def async_added_to_hass(A):await super().async_added_to_hass();A.async_on_remove(async_dispatcher_connect(A.hass,SIGNAL_UPDATED,A._handle_update))
	@callback
	def _handle_update(self):self.async_write_ha_state()