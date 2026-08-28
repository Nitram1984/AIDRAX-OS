from aidrax_ai.runtime.health import RuntimeHealth
h=RuntimeHealth()
h.set("runtime",True)
assert h.summary()["runtime"] is True
