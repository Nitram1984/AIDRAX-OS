
REQUIRED=["project","build","codename","ring","host"]
def validate(cfg):
    missing=[k for k in REQUIRED if k not in cfg]
    return {"status":"GREEN" if not missing else "RED","missing":missing}
