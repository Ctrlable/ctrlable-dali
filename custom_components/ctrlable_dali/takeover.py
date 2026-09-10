from __future__ import annotations
_C='entities'
_B='version'
_A=None
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr,entity_registry as er
from.const import DOMAIN
_LOGGER=logging.getLogger(__name__)
STORAGE_VERSION=1
STORAGE_KEY='ctrlable_dali_takeover'
_UID_PREFIX='dali_'
def _store(hass):from homeassistant.helpers.storage import Store;return Store(hass,STORAGE_VERSION,STORAGE_KEY)
async def async_record_mqtt_entities(hass):
	C=hass;G=er.async_get(C);H=dr.async_get(C);D={}
	for A in G.entities.values():
		E=str(A.unique_id or'')
		if A.platform!='mqtt'or not E.startswith(_UID_PREFIX):continue
		B=H.async_get(A.device_id)if A.device_id else _A;D[E]={'entity_id':A.entity_id,'domain':A.entity_id.split('.')[0],'entity_area_id':A.area_id,'device_area_id':B.area_id if B else _A,'device_identifiers':sorted(list(A)for A in B.identifiers)if B else[],'device_name':B.name_by_user or B.name if B else _A,'name':A.name,'hidden_by':A.hidden_by,'disabled_by':A.disabled_by}
	F={_B:1,_C:D};await _store(C).async_save(F);_LOGGER.debug('Ctrlable DALI: recorded %d MQTT entities for takeover',len(D));return F
async def async_load_recorded(hass):return await _store(hass).async_load()or{_B:1,_C:{}}
async def async_prune_empty_devices(hass,entry_id):
	C=dr.async_get(hass);D=er.async_get(hass);A=0
	for B in list(C.devices):
		if B.config_entry_id!=entry_id:continue
		if er.async_entries_for_device(D,B.id,include_disabled_entities=True):continue
		if getattr(B,'composite_device_id',_A):continue
		C.async_remove_device(B.id);A+=1
	if A:_LOGGER.warning('Ctrlable DALI: removed %d empty device row(s) left by the 2026.9 device split or a rolled-back takeover — they were duplicates of the MQTT devices that hold the entities',A)
	return A