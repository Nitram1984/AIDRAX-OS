from lifecycle import LifecycleManager
from health import health_check
from version import AIDRAX_OS_VERSION, AIDRAX_OS_BUILD, AIDRAX_OS_CODENAME

def bootstrap():
    lifecycle = LifecycleManager()
    lifecycle.boot()

    return {
        "version": AIDRAX_OS_VERSION,
        "build": AIDRAX_OS_BUILD,
        "codename": AIDRAX_OS_CODENAME,
        "lifecycle": lifecycle.state,
        "health": health_check()
    }

if __name__ == "__main__":
    print(bootstrap())
