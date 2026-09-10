from __future__ import annotations
_K='device_area_id'
_J='caps_remembered'
_I='version'
_H='mqtt'
_G=False
_F='ha_discovery'
_E='entity_id'
_D=True
_C='caps'
_B='entities'
_A=None
import logging
from homeassistant.core import HomeAssistant,callback
from homeassistant.helpers import device_registry as dr,entity_registry as er
from.const import DOMAIN
_LOGGER=logging.getLogger(__name__)
STORAGE_VERSION=1
STORAGE_KEY='ctrlable_dali_takeover'
_UID_PREFIX='dali_'
def _store(hass):from homeassistant.helpers.storage import Store;return Store(hass,STORAGE_VERSION,STORAGE_KEY)
async def async_record_mqtt_entities(hass):
	E=hass;J=er.async_get(E);K=dr.async_get(E);G={}
	for A in J.entities.values():
		C=str(A.unique_id or'')
		if A.platform!=_H or not C.startswith(_UID_PREFIX):continue
		D=K.async_get(A.device_id)if A.device_id else _A;G[C]={_E:A.entity_id,'domain':A.entity_id.split('.')[0],'entity_area_id':A.area_id,_K:D.area_id if D else _A,'device_identifiers':sorted(list(A)for A in D.identifiers)if D else[],'device_name':D.name_by_user or D.name if D else _A,'name':A.name,'capabilities':dict(A.capabilities or{}),'hidden_by':A.hidden_by,'disabled_by':A.disabled_by}
	F=await async_load_recorded(E);B=dict(F.get(_B)or{})
	if takeover_active(E):
		if B:_LOGGER.debug('Ctrlable DALI: takeover active — keeping the recorded map of %d entities untouched',len(B));return{_I:1,_B:B,_C:F.get(_C)}
	for(C,I)in G.items():
		if C in B:L=B[C].get(_E);B[C]={**I,_E:L}
		else:B[C]=I
	H={_I:1,_B:B,_C:F.get(_C)}
	if B==(F.get(_B)or{}):return H
	await _store(E).async_save(H);_LOGGER.debug('Ctrlable DALI: takeover map holds %d entities (%d seen this run)',len(B),len(G));return H
async def async_load_recorded(hass):return await _store(hass).async_load()or{_I:1,_B:{}}
def takeover_active(hass):
	C=hass.data.get(DOMAIN)or{};A=(C.get('cache')or{}).get(_C)
	if isinstance(A,dict)and _F in A:return A.get(_F)is _G
	B=C.get(_J)
	if isinstance(B,dict)and _F in B:return B.get(_F)is _G
	return _G
def recorded_entity_id(recorded,unique_id):return(recorded.get(_B)or{}).get(unique_id,{}).get(_E)
@callback
def async_release_entity_id(hass,entity_id,unique_id):
	C=unique_id;B=entity_id;D=er.async_get(hass);A=D.async_get(B)
	if A is _A:return _D
	if A.platform==DOMAIN and str(A.unique_id)==C:return _D
	if A.platform==_H and str(A.unique_id)==C:_LOGGER.info('Ctrlable DALI: reclaiming %s from the MQTT entity of the same fixture',B);D.async_remove(B);return _D
	_LOGGER.warning('Ctrlable DALI: %s is held by %s (unique_id %s) — not reclaiming it',B,A.platform,A.unique_id);return _G
async def async_restore_areas(hass,recorded):
	D=dr.async_get(hass);G=er.async_get(hass);A=0
	for(H,E)in(recorded.get(_B)or{}).items():
		F=E.get(_K)
		if not F:continue
		B=G.async_get(E.get(_E)or'')
		if B is _A or B.platform!=DOMAIN or not B.device_id:continue
		C=D.async_get(B.device_id)
		if C is _A or C.area_id:continue
		D.async_update_device(C.id,area_id=F);A+=1
	if A:_LOGGER.info('Ctrlable DALI: restored %d device area(s) after takeover',A)
	return A
@callback
def async_repair_entity_id(hass,current,wanted):
	B=current;A=wanted;C=er.async_get(hass)
	if B==A:return _D
	if C.async_get(A)is not _A:_LOGGER.warning('Ctrlable DALI: cannot move %s back to %s — that id is taken',B,A);return _G
	_LOGGER.info('Ctrlable DALI: restoring entity id %s -> %s',B,A);C.async_update_entity(B,new_entity_id=A);return _D
async def async_hand_back(hass):
	C=er.async_get(hass);G=await async_load_recorded(hass);D=E=0
	for A in list(C.entities.values()):
		F=str(A.unique_id or'')
		if not F.startswith(_UID_PREFIX):continue
		if A.platform==DOMAIN:C.async_remove(A.entity_id);D+=1
		elif A.platform==_H:
			B=recorded_entity_id(G,F)
			if B and A.entity_id!=B:
				if C.async_get(B)is _A:C.async_update_entity(A.entity_id,new_entity_id=B);E+=1
				else:_LOGGER.warning('Ctrlable DALI: cannot put %s back on %s — that id is taken',A.entity_id,B)
	if D or E:_LOGGER.warning('Ctrlable DALI: handing entities back to MQTT — released %d of ours, moved %d MQTT entities off a fallback id back onto their recorded one',D,E)
	return D+E
async def async_remember_caps(hass,caps):
	B=hass;A=caps
	if not isinstance(A,dict)or _F not in A:return
	B.data.setdefault(DOMAIN,{})[_J]=dict(A);C=await async_load_recorded(B)
	if C.get(_C)==A:return
	C[_C]=dict(A);await _store(B).async_save(C);_LOGGER.debug('Ctrlable DALI: remembered bridge caps %s',A)
async def async_load_remembered_caps(hass):
	B=await async_load_recorded(hass);A=B.get(_C)
	if isinstance(A,dict):hass.data.setdefault(DOMAIN,{})[_J]=dict(A)
	return A or{}
async def async_prune_empty_devices(hass,entry_id):
	C=dr.async_get(hass);D=er.async_get(hass);A=0
	for B in list(C.devices):
		if B.config_entry_id!=entry_id:continue
		if er.async_entries_for_device(D,B.id,include_disabled_entities=_D):continue
		if getattr(B,'composite_device_id',_A):continue
		C.async_remove_device(B.id);A+=1
	if A:_LOGGER.warning('Ctrlable DALI: removed %d empty device row(s) left by the 2026.9 device split or a rolled-back takeover — they were duplicates of the MQTT devices that hold the entities',A)
	return A
_BUS_SUFFIXES='_scene','_config_commission','_config_scan'
def known_buses(recorded,cache=_A):
	C=cache;A=set()
	for D in recorded.get(_B)or{}:
		if not D.startswith(_UID_PREFIX):continue
		B=D[len(_UID_PREFIX):]
		for E in _BUS_SUFFIXES:
			if B.endswith(E):A.add(B[:-len(E)]);break
		else:
			F=B.rfind('_group_')
			if F>0:A.add(B[:F])
	if C:A.update((C.get('gateways')or{}).keys())
	return sorted(A,key=len,reverse=_D)