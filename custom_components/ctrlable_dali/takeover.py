from __future__ import annotations
_B='entities'
_A='version'
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
	E=None;C=hass;H=er.async_get(C);I=dr.async_get(C);D={}
	for A in H.entities.values():
		F=str(A.unique_id or'')
		if A.platform!='mqtt'or not F.startswith(_UID_PREFIX):continue
		B=I.async_get(A.device_id)if A.device_id else E;D[F]={'entity_id':A.entity_id,'domain':A.entity_id.split('.')[0],'entity_area_id':A.area_id,'device_area_id':B.area_id if B else E,'device_identifiers':sorted(list(A)for A in B.identifiers)if B else[],'device_name':B.name_by_user or B.name if B else E,'name':A.name,'hidden_by':A.hidden_by,'disabled_by':A.disabled_by}
	G={_A:1,_B:D};await _store(C).async_save(G);_LOGGER.debug('Ctrlable DALI: recorded %d MQTT entities for takeover',len(D));return G
async def async_load_recorded(hass):return await _store(hass).async_load()or{_A:1,_B:{}}