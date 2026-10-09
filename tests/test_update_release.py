import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('update_release', ROOT / 'tools/update_release.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class ReleaseTests(unittest.TestCase):
    def test_only_stable_versions_and_numeric_order(self):
        with patch.object(updater, 'fetch', return_value=b'[{"name":"v0.1.9"},{"name":"v0.1.10"},{"name":"v0.2.0-rc1"},{"name":"nightly"}]'):
            self.assertEqual(updater.latest_tag(), 'v0.1.10')

    def test_paginated_tags(self):
        import json
        first = json.dumps([{'name': 'nightly'}] * 100).encode()
        with patch.object(updater, 'fetch', side_effect=[first, b'[{"name":"v0.1.41"}]']):
            self.assertEqual(updater.latest_tag(), 'v0.1.41')

    def test_upstream_four_part_hotfix_tags(self):
        with patch.object(updater, 'fetch', return_value=b'[{"name":"v0.1.40"},{"name":"v0.1.40.4"},{"name":"v0.1.40.3"}]'):
            self.assertEqual(updater.latest_tag(), 'v0.1.40.4')

    def test_no_stable_tag_fails(self):
        with patch.object(updater, 'fetch', return_value=b'[]'):
            with self.assertRaises(RuntimeError):
                updater.latest_tag()

    def test_package_name_and_recipe_preserved(self):
        old = (ROOT / 'PKGBUILD').read_text()
        new = updater.update_text(old, 'v0.1.99', 'a' * 40, ['b' * 64] * 5)
        self.assertIn('pkgname=strata-inference-cuda\n', new)
        self.assertIn('pkgver=0.1.99\npkgrel=1\n', new)
        self.assertEqual(new[new.index('build()'):], old[old.index('build()'):])


if __name__ == '__main__':
    unittest.main()
