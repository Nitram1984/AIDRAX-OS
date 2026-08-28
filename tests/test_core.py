from aidrax_core.runtime.core import CoreRuntime
from aidrax_core.config import Config
from aidrax_core.errors import RuntimeValidationError
import pytest

def test_register():
 r=CoreRuntime();r.register('x');assert r.status()['count']==1


def test_runtime_reads_shared_config(tmp_path):
    config_path = tmp_path / "settings.json"
    config_path.write_text('{"mode": "closed-alpha"}', encoding="utf-8")

    assert CoreRuntime(Config(config_path)).settings == {"mode": "closed-alpha"}


def test_runtime_invalid_registration_has_classified_error():
    with pytest.raises(RuntimeValidationError) as error:
        CoreRuntime().register("")

    assert error.value.status()["code"] == "validation"
