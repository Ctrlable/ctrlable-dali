from __future__ import annotations
_A='select'
import logging
from homeassistant.components.select import SelectEntity
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
NONE_OPTION='None'
SCENE_COUNT=16
async def async_setup_entry(hass,entry,async_add_entities):
	H='_scene';A=hass
	if not takeover_active(A):return
	G=await async_load_recorded(A);I=(A.data.get(DOMAIN)or{}).get('cache')or{};D=sorted({A[len('dali_'):-len(H)]for(A,B)in(G.get('entities')or{}).items()if B.get('domain')==_A and A.endswith(H)})
	if not D:D=sorted((I.get('gateways')or{}).keys())
	E=[DaliSceneSelect(A,B)for B in D];J=er.async_get(A)
	for B in E:
		C=recorded_entity_id(G,B.unique_id)
		if not C:continue
		F=J.async_get_entity_id(B.entity_id.split('.')[0]if B.entity_id else PLATFORM_DOMAIN,DOMAIN,B.unique_id)
		if F and F!=C:async_repair_entity_id(A,F,C)
		if async_release_entity_id(A,C,B.unique_id):B.entity_id=C
	async_add_entities(E);_LOGGER.info('Ctrlable DALI: added %d scene select(s) after takeover',len(E))
class DaliSceneSelect(DaliEntity,SelectEntity):
	_attr_name='Scene'
	def __init__(B,hass,bus):A=bus;DaliEntity.__init__(B,hass,A);B._attr_unique_id=f"dali_{A}_scene";B._attr_device_info=DeviceInfo(identifiers={gateway_identifier(A)},name=A,manufacturer=GATEWAY_MANUFACTURER,model=GATEWAY_MODEL)
	@property
	def options(self):B=self._gateway.get('scene_names')or{};return[NONE_OPTION]+[B.get(str(A))or f"Scene {A}"for A in range(SCENE_COUNT)]
	@property
	def current_option(self):
		A=self._gateway.get('scene_state')
		if A in(None,'',NONE_OPTION):return NONE_OPTION
		B=self.options
		if A in B:return A
		try:C=int(A)
		except(TypeError,ValueError):return NONE_OPTION
		return B[C+1]if 0<=C<SCENE_COUNT else NONE_OPTION
	async def async_select_option(A,option):await A._publish(f"{A._base}/{A._bus}/scene/select",option)