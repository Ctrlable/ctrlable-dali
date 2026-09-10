from __future__ import annotations
_G='color_temp'
_F='attributes'
_E='devices'
_D='brightness'
_C='tc_capable'
_B='state'
_A=None
import logging
from homeassistant.components.light import ATTR_BRIGHTNESS,ATTR_COLOR_TEMP_KELVIN,ColorMode,LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant,callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from.const import DOMAIN
from.entity import GATEWAY_MANUFACTURER,GATEWAY_MODEL,DaliEntity,fixture_identifier,gateway_identifier,link_to_gateway
from.takeover import async_load_recorded,known_buses,async_repair_entity_id,async_release_entity_id,recorded_entity_id,takeover_active
_LOGGER=logging.getLogger(__name__)
PLATFORM_DOMAIN='light'
DEFAULT_MIN_MIREK=153
DEFAULT_MAX_MIREK=370
def _mirek_to_kelvin(mirek):A=mirek;return int(1000000/A)if A else 0
def _kelvin_to_mirek(kelvin):A=kelvin;return int(1000000/A)if A else 0
def _parse_light_uid(unique_id,buses):
	E='group_';B=unique_id
	for A in buses:
		C=f"dali_{A}_"
		if not B.startswith(C):continue
		D=B[len(C):]
		if D.startswith(E):
			try:return A,int(D[len(E):])
			except ValueError:return
		return A,_A
async def async_setup_entry(hass,entry,async_add_entities):
	A=hass
	if not takeover_active(A):_LOGGER.debug('Ctrlable DALI: bridge still publishes MQTT discovery — not creating lights');return
	F=await async_load_recorded(A);I=(A.data.get(DOMAIN)or{}).get('cache')or{};C=[];M=known_buses(F,I)
	for(G,N)in sorted((F.get('entities')or{}).items()):
		if N.get('domain')!='light':continue
		J=_parse_light_uid(G,M)
		if J is _A:_LOGGER.debug('Ctrlable DALI: skipping unrecognised light uid %s',G);continue
		E,K=J
		if K is not _A:C.append(DaliGroupLight(A,E,K))
		else:L=G[len(f"dali_{E}_"):];O=(((I.get('gateways')or{}).get(E)or{}).get(_E)or{}).get(L)or{};C.append(DaliFixtureLight(A,E,L,O))
	P=er.async_get(A)
	for B in C:
		D=recorded_entity_id(F,B.unique_id)
		if not D:continue
		H=P.async_get_entity_id(B.entity_id.split('.')[0]if B.entity_id else PLATFORM_DOMAIN,DOMAIN,B.unique_id)
		if H and H!=D:async_repair_entity_id(A,H,D)
		if async_release_entity_id(A,D,B.unique_id):B.entity_id=D
	async_add_entities(C);_LOGGER.info('Ctrlable DALI: added %d light(s) after takeover',len(C))
class DaliFixtureLight(DaliEntity,LightEntity):
	_attr_has_entity_name=True;_attr_name=_A
	def __init__(B,hass,bus,key,dev):C=key;A=bus;DaliEntity.__init__(B,hass,A);B._key=C;B._attr_unique_id=f"dali_{A}_{C}";D=dev.get(_F)or{};E=D.get('name')or f"DALI {C}";F=(hass.data.get(DOMAIN)or{}).get('gateway_device_ids',{}).get(A);B._attr_device_info=link_to_gateway(DeviceInfo(identifiers={fixture_identifier(A,C)},name=E,manufacturer='DALI',model='DT6/8'if D.get(_C)else'DT6'),A,F)
	@property
	def _dev(self):return(self._gateway.get(_E)or{}).get(self._key)or{}
	@property
	def _attrs(self):return self._dev.get(_F)or{}
	@property
	def _state(self):return self._dev.get(_B)or{}
	@property
	def extra_state_attributes(self):return self._attrs
	@property
	def supported_color_modes(self):
		if self._attrs.get(_C):return{ColorMode.COLOR_TEMP}
		return{ColorMode.BRIGHTNESS}
	@property
	def color_mode(self):return ColorMode.COLOR_TEMP if self._attrs.get(_C)else ColorMode.BRIGHTNESS
	@property
	def min_color_temp_kelvin(self):return _mirek_to_kelvin(self._attrs.get('tc_max_mirek')or DEFAULT_MAX_MIREK)
	@property
	def max_color_temp_kelvin(self):return _mirek_to_kelvin(self._attrs.get('tc_min_mirek')or DEFAULT_MIN_MIREK)
	@property
	def color_temp_kelvin(self):A=self._state.get(_G);return _mirek_to_kelvin(A)if A else _A
	@property
	def is_on(self):return str(self._state.get(_B,'')).upper()=='ON'
	@property
	def brightness(self):return self._state.get(_D)
	@property
	def _set_topic(self):A=self;return f"{A._base}/{A._bus}/light/{A._key}/set"
	async def async_turn_on(C,**A):
		B={_B:'ON'}
		if ATTR_BRIGHTNESS in A:B[_D]=int(A[ATTR_BRIGHTNESS])
		if ATTR_COLOR_TEMP_KELVIN in A:B[_G]=_kelvin_to_mirek(int(A[ATTR_COLOR_TEMP_KELVIN]))
		await C._publish(C._set_topic,B)
	async def async_turn_off(A,**B):await A._publish(A._set_topic,{_B:'OFF'})
class DaliGroupLight(DaliEntity,LightEntity):
	_attr_color_mode=ColorMode.BRIGHTNESS;_attr_supported_color_modes={ColorMode.BRIGHTNESS};_attr_assumed_state=True
	def __init__(A,hass,bus,group):C=group;B=bus;DaliEntity.__init__(A,hass,B);A._group=C;A._attr_unique_id=f"dali_{B}_group_{C}";A._attr_is_on=False;A._attr_brightness=_A;A._attr_device_info=DeviceInfo(identifiers={gateway_identifier(B)},name=B,manufacturer=GATEWAY_MANUFACTURER,model=GATEWAY_MODEL)
	@property
	def name(self):A=self;B=A._gateway.get('group_names')or{};return B.get(str(A._group))or f"Group {A._group}"
	@property
	def _set_topic(self):A=self;return f"{A._base}/{A._bus}/light/group/{A._group}/set"
	async def async_turn_on(A,**B):
		C={_B:'ON'}
		if ATTR_BRIGHTNESS in B:C[_D]=int(B[ATTR_BRIGHTNESS]);A._attr_brightness=int(B[ATTR_BRIGHTNESS])
		await A._publish(A._set_topic,C);A._attr_is_on=True;A.async_write_ha_state()
	async def async_turn_off(A,**B):await A._publish(A._set_topic,{_B:'OFF'});A._attr_is_on=False;A.async_write_ha_state()
	@callback
	def _handle_update(self):self.async_write_ha_state()