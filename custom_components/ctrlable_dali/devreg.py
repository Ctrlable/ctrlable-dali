from __future__ import annotations
_A=None
def all_devices(dev_reg):
	A=dev_reg.devices;B=next(iter(A),_A)
	if B is _A:return[]
	if isinstance(B,str):return list(A.values())
	return list(A)
def devices_by_identifier(dev_reg,identifiers):
	B=identifiers;A=dev_reg;C=getattr(A,'async_get_devices',_A)
	if C is not _A:return C(identifiers=B)
	return[A for A in all_devices(A)if set(A.identifiers)&B]
def first_device_by_identifier(dev_reg,identifiers):A=devices_by_identifier(dev_reg,identifiers);return A[0]if A else _A
def supports_multi_entry_devices(dev_reg):return'new_config_entry_id'not in _update_params(dev_reg)
def _update_params(dev_reg):
	import inspect as A
	try:return set(A.signature(dev_reg.async_update_device).parameters)
	except(TypeError,ValueError):return set()