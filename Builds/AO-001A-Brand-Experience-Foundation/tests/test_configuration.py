import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidrax_brand_experience import BrandCatalog, ExperienceEngine


class ConfigurationTests(unittest.TestCase):
    def test_shipped_configuration_satisfies_both_contracts(self):
        catalog = json.loads((ROOT / "config" / "brand-catalog.json").read_text(encoding="utf-8"))
        experience = json.loads((ROOT / "config" / "experience-map.json").read_text(encoding="utf-8"))
        assets = BrandCatalog.from_mapping(catalog).assets_for("wallpaper")
        self.assertEqual(assets[0].asset_id, "aidrax.spectral-dragon.wallpaper.001")
        self.assertEqual(ExperienceEngine.from_mapping(experience).cue_for("LOGIN_READY").scene, "desktop")


if __name__ == "__main__":
    unittest.main()
