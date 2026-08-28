from aidrax_ai.capability_manager.registry import CapabilityRegistry
r=CapabilityRegistry()
assert r.resolve("x") is None
print("capability registry ok")
