import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidrax_brand_experience import BrandCatalog


class BrandCatalogTests(unittest.TestCase):
    def test_empty_approved_catalog_is_explicit_and_valid(self):
        catalog = BrandCatalog.from_mapping({"schema_version": 1, "assets": []})
        self.assertEqual(catalog.all_assets(), ())

    def test_assets_are_declared_but_not_read_from_disk(self):
        catalog = BrandCatalog.from_mapping({"schema_version": 1, "assets": [{
            "asset_id": "dragon.boot", "kind": "animation", "path": "media/dragon.webm", "sha256": "a" * 64,
        }]})
        self.assertEqual(catalog.assets_for("animation")[0].path, "media/dragon.webm")

    def test_catalog_rejects_traversal_and_invalid_digest(self):
        with self.assertRaises(ValueError):
            BrandCatalog.from_mapping({"schema_version": 1, "assets": [{"asset_id": "x", "kind": "image", "path": "../x", "sha256": "a" * 64}]})
        with self.assertRaises(ValueError):
            BrandCatalog.from_mapping({"schema_version": 1, "assets": [{"asset_id": "x", "kind": "image", "path": "x", "sha256": "bad"}]})


if __name__ == "__main__":
    unittest.main()
