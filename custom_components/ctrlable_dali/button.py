from __future__ import annotations
_A='button'
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from.const import DOMAIN
from.entity import GATEWAY_MANUFACTURER,GATEWAY_MODEL,DaliEntity,gateway_identifier
from.takeover import async_load_recorded,async_repair_entity_id,async_release_entity_id,recorded_entity_id,takeover_active
_LOGGER=logging.getLogger(__name__)
PLATFORM_DOMAIN=_A
BUTTONS=('config_commission','Commission','config/commission'),('config_scan','Rescan','config/scan')
async def async_setup_entry(hass,entry,async_add_entities):
	A=hass
	if not takeover_active(A):return
	G=await async_load_recorded(A);H=(A.data.get(DOMAIN)or{}).get('cache')or{};D=sorted({A[len('dali_'):-(len(B)+1)]for(A,C)in(G.get('entities')or{}).items()if C.get('domain')==_A for(B,D,E)in BUTTONS if A.endswith('_'+B)})
	if not D:D=sorted((H.get('gateways')or{}).keys())
	E=[DaliGatewayButton(A,B,C,D,E)for B in D for(C,D,E)in BUTTONS];I=er.async_get(A)
	for B in E:
		C=recorded_entity_id(G,B.unique_id)
		if not C:continue
		F=I.async_get_entity_id(B.entity_id.split('.')[0]if B.entity_id else PLATFORM_DOMAIN,DOMAIN,B.unique_id)
		if F and F!=C:async_repair_entity_id(A,F,C)
		if async_release_entity_id(A,C,B.unique_id):B.entity_id=C
	async_add_entities(E);_LOGGER.info('Ctrlable DALI: added %d gateway button(s) after takeover',len(E))
class DaliGatewayButton(DaliEntity,ButtonEntity):
	def __init__(A,hass,bus,suffix,label,topic):B=bus;DaliEntity.__init__(A,hass,B);A._topic=topic;A._attr_name=label;A._attr_unique_id=f"dali_{B}_{suffix}";A._attr_device_info=DeviceInfo(identifiers={gateway_identifier(B)},name=B,manufacturer=GATEWAY_MANUFACTURER,model=GATEWAY_MODEL)
	async def async_press(A):await A._publish(f"{A._base}/{A._bus}/{A._topic}",'{}')