from aidrax_ai.runtime.health import RuntimeHealth
h=RuntimeHealth()
h.set("bootstrap", True)
assert h.summary()["bootstrap"] is True
print("bootstrap ok")
